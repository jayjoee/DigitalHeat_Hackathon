"""Bounded AES-256-GCM envelopes. Only the customer and the attested guest get keys.

Metadata is public. AAD binds the protocol, customer, job and input/output direction.
This encryption alone does NOT provide confidential execution on an ordinary host.
"""
import base64
import json
import os
from pathlib import Path
import re
import uuid

MAX_PLAINTEXT = 128 * 1024
MAX_ENVELOPE = 200 * 1024
FIELDS = {'version', 'algorithm', 'customer', 'job_id', 'direction', 'nonce', 'ciphertext'}


def identity(customer, job_id):
    if not isinstance(customer, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,62}', customer):
        raise ValueError('Kunden-ID muss eine technische ID ohne Personendaten sein.')
    if not isinstance(job_id, str) or str(uuid.UUID(job_id)) != job_id:
        raise ValueError('Ungültige Auftrags-ID.')


def encode(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def validate(data, direction=None, customer=None):
    if not isinstance(data, dict) or set(data) != FIELDS or len(encode(data)) > MAX_ENVELOPE:
        raise ValueError('Ungültiges verschlüsseltes Auftragspaket.')
    identity(data['customer'], data['job_id'])
    if type(data['version']) is not int or data['version'] != 1 or data['algorithm'] != 'AES-256-GCM':
        raise ValueError('Nicht unterstütztes Paketformat.')
    if data['direction'] not in ('input', 'output') or (direction and data['direction'] != direction):
        raise ValueError('Falsche Paketrichtung.')
    if customer is not None and data['customer'] != customer:
        raise PermissionError('Auftragspaket gehört einem anderen Kunden.')
    try:
        nonce = base64.b64decode(data['nonce'], validate=True)
        ciphertext = base64.b64decode(data['ciphertext'], validate=True)
    except (ValueError, TypeError):
        raise ValueError('Ungültige Paketkodierung.') from None
    if len(nonce) != 12 or not 16 <= len(ciphertext) <= MAX_PLAINTEXT + 16:
        raise ValueError('Ungültige Paketgrösse.')
    return data


def aad(data):
    return encode({k: data[k] for k in ('version', 'algorithm', 'customer', 'job_id', 'direction')})


def seal(plaintext, key, customer, job_id, direction='input'):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    identity(customer, job_id)
    if not isinstance(plaintext, bytes) or len(plaintext) > MAX_PLAINTEXT or len(key) != 32:
        raise ValueError('Ungültiger Schlüssel oder zu grosser Inhalt.')
    nonce = os.urandom(12)
    data = dict(version=1, algorithm='AES-256-GCM', customer=customer, job_id=job_id,
                direction=direction, nonce=base64.b64encode(nonce).decode())
    data['ciphertext'] = base64.b64encode(AESGCM(key).encrypt(nonce, plaintext, aad(data))).decode()
    return validate(data)


def unseal(data, key, direction):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    validate(data, direction=direction)
    if len(key) != 32:
        raise ValueError('Ungültiger Schlüssel.')
    return AESGCM(key).decrypt(base64.b64decode(data['nonce']), base64.b64decode(data['ciphertext']), aad(data))


def private_write(path, content):
    """Never overwrite an existing key/result or follow a final symlink."""
    with os.fdopen(os.open(Path(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as stream:
        stream.write(content)


def resource_path(data):
    validate(data)
    return f"{data['customer']}/keys/{data['job_id']}"
