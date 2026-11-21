"""Run ONLY inside an attested CoCo guest with a pinned, restrictive agent policy.

No host key file/environment fallback, no shell, no uploaded executable, no plaintext
output. CDH performs the real Trustee RCAR/attestation flow; this module does not
interpret self-declared attestation JSON as proof. Local execution is not a TEE.
"""
import http.client
import json
import re
import sys
from pathlib import Path
from .envelope import MAX_ENVELOPE, encode, resource_path, seal, unseal, validate


def fetch_key(envelope):
    # The REST server lives INSIDE the measured guest. Never expose it to the host.
    connection = http.client.HTTPConnection('127.0.0.1', 8006, timeout=30)
    try:
        connection.request('GET', '/cdh/resource/' + resource_path(envelope))
        response = connection.getresponse()
        key = response.read(33)
        if response.status != 200 or len(key) != 32:
            raise PermissionError('Schlüsselfreigabe verweigert.')
        return key
    finally:
        connection.close()


def process(envelope):
    validate(envelope, direction='input')
    key = fetch_key(envelope)
    payload = json.loads(unseal(envelope, key, 'input'))
    # First real protected CPU workload. GPU/scientific models require a separate
    # reviewed image and policy, not arbitrary customer commands on this service.
    if not isinstance(payload, dict) or set(payload) != {'operation', 'text'} or payload['operation'] != 'text_statistics':
        raise ValueError('Nicht freigegebener Auftrag.')
    if not isinstance(payload['text'], str):
        raise ValueError('Ungültiger Text.')
    words = re.findall(r'[^\W\d_]+', payload['text'].lower(), re.UNICODE)
    result = encode(dict(words=len(words), unique_words=len(set(words)), characters=len(payload['text'])))
    return seal(result, key, envelope['customer'], envelope['job_id'], 'output')


def main():
    try:
        with Path('/run/digitalheat-input/envelope.json').open('rb') as stream:
            raw = stream.read(MAX_ENVELOPE+1)
        if len(raw) > MAX_ENVELOPE:
            raise ValueError('Paket zu gross.')
        result = process(json.loads(raw))
        # Host logs may read this: it contains ciphertext only.
        sys.stdout.buffer.write(encode(result) + b'\n')
    except Exception:
        # No exception repr, keys, plaintext or traceback in host-readable logs.
        print('Vertraulicher Auftrag fehlgeschlagen; keine Klartextausgabe.', file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
