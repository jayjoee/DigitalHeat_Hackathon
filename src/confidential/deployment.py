"""Generate a CoCo job and a deny-by-default Trustee key-release policy.

Run this on DigitalHeat's trusted control plane, not the household host. Hardware
evidence is verified by Trustee, not by this planner or Kubernetes node labels.
An approved SHA384 pins externally reviewed Init-Data, including guest agent policy.
"""
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit

from .envelope import encode, resource_path, validate


def _dns(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', value):
        raise ValueError('Ungültiger technischer Kubernetes-Name.')
    return value


def load_deployment(path):
    source = Path(path).resolve()
    config = json.loads(source.read_text())
    required = {'namespace', 'image', 'initdata_file', 'approved_initdata_sha384', 'kbs_url'}
    if set(config)-required-{'image_key_resource'} or not required.issubset(config):
        raise ValueError('Unvollständige oder unbekannte CoCo-Betreiberkonfiguration.')
    _dns(config['namespace'])
    image = config['image']
    if not isinstance(image, str) or not re.fullmatch(r'[a-zA-Z0-9./_:-]+@sha256:[a-f0-9]{64}', image) or image.endswith('0'*64):
        raise ValueError('Freigegebenes Worker-Image muss über seinen echten Digest festgelegt sein.')
    url = urlsplit(config['kbs_url'])
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ('', '/'):
        raise ValueError('Trustee muss eine vertrauenswürdige HTTPS-Adresse verwenden.')
    init_path = Path(config['initdata_file'])
    if not init_path.is_absolute():
        init_path = source.parent / init_path
    raw = init_path.read_bytes()
    expected = config['approved_initdata_sha384']
    if not isinstance(expected, str) or not re.fullmatch(r'[a-f0-9]{96}', expected) or hashlib.sha384(raw).hexdigest() != expected:
        raise ValueError('Init-Data stimmt nicht mit der freigegebenen SHA384-Prüfsumme überein.')
    data = tomllib.loads(raw.decode())
    if data.get('algorithm') != 'sha384' or data.get('version') != '0.1.0':
        raise ValueError('Diese erste Integration erfordert TDX mit SHA384 Init-Data.')
    components = data['data']
    if not components.get('policy.rego'):
        raise ValueError('Gemessene Kata-Agent-Policy fehlt.')
    cdh = tomllib.loads(components['cdh.toml'])
    if cdh['kbc']['name'] != 'cc_kbc' or cdh['kbc']['url'].rstrip('/') != config['kbs_url'].rstrip('/'):
        raise ValueError('CDH muss den freigegebenen externen Trustee verwenden.')
    if 'BEGIN CERTIFICATE' not in cdh['kbc'].get('kbs_cert', ''):
        raise ValueError('Trustee-Zertifikat muss innerhalb der gemessenen CDH-Konfiguration festgelegt sein.')
    aa=tomllib.loads(components['aa.toml'])['token_configs']['kbs']
    if aa.get('url','').rstrip('/')!=config['kbs_url'].rstrip('/') or aa.get('cert')!=cdh['kbc']['kbs_cert']:
        raise ValueError('Attestation Agent und CDH müssen denselben HTTPS-Trustee und dieselbe Zertifikatsbindung verwenden.')
    image_key=config.get('image_key_resource')
    if image_key is not None and (not isinstance(image_key,str) or not re.fullmatch(r'[a-z0-9-]+/image-key/[a-z0-9-]+',image_key)):
        raise ValueError('Ungültige Trustee-Ressource für ein verschlüsseltes OCI-Image.')
    config['_initdata'] = raw
    return config


def bundle(node, ticket, envelope, config, remaining_seconds):
    validate(envelope, direction='input', customer=ticket.customer)
    if envelope['job_id'] != ticket.id or ticket.requirements.classification != 'confidential':
        raise ValueError('Auftrag und verschlüsseltes Paket passen nicht zusammen.')
    if node.executor != 'confidential_coco' or node.tee_type != 'tdx' or node.slots != 1:
        raise PermissionError('Kein dedizierter TDX-CoCo-Server.')
    if len(node.gpu_memory_gb) > 1 or ticket.requirements.gpu_count != len(node.gpu_memory_gb):
        raise PermissionError('Diese erste Integration reserviert den vollständigen Single-GPU-Server oder einen CPU-only-Server.')
    # Defense in depth even if an operator mutated inventory after construction.
    if node.gpu_memory_gb and node.gpu_model not in ('H100', 'H200', 'B200'):
        raise PermissionError('GPU nicht für diese Confidential-Computing-Integration freigegeben; insbesondere keine L4.')
    if not math.isfinite(remaining_seconds) or remaining_seconds <= 0:
        raise ValueError('Keine verbleibende Ausführungszeit.')
    name = 'cc-' + ticket.id
    namespace = config['namespace']
    resources = {'memory': f'{math.ceil(ticket.requirements.ram_gb*1000)}M', 'cpu': str(ticket.requirements.cpu_cores)}
    if node.gpu_memory_gb:
        resources['nvidia.com/pgpu'] = '1'
    pod = {'metadata': {'annotations': {
        'io.katacontainers.config.hypervisor.cc_init_data': base64.b64encode(gzip.compress(config['_initdata'], mtime=0)).decode()}},
        'spec': {'nodeName': node.id, 'runtimeClassName': 'kata-qemu-nvidia-gpu-tdx' if node.gpu_memory_gb else 'kata-qemu-tdx',
                 'restartPolicy': 'Never', 'automountServiceAccountToken': False,
                 'securityContext': {'runAsNonRoot': True, 'runAsUser': 10001, 'seccompProfile': {'type': 'RuntimeDefault'}},
                 'containers': [{'name': 'worker', 'image': config['image'], 'imagePullPolicy': 'Always',
                                 'command': ['python', '-m', 'src.confidential.guest'],
                                 'resources': {'requests': resources, 'limits': dict(resources)},
                                 'securityContext': {'allowPrivilegeEscalation': False, 'readOnlyRootFilesystem': True,
                                                     'capabilities': {'drop': ['ALL']}},
                                 'volumeMounts': [{'name': 'input', 'mountPath': '/run/digitalheat-input', 'readOnly': True}]}],
                 'volumes': [{'name': 'input', 'configMap': {'name': name, 'defaultMode': 292}}]}}
    job = {'apiVersion': 'batch/v1', 'kind': 'Job', 'metadata': {'name': name, 'namespace': namespace},
           'spec': {'backoffLimit': 0, 'activeDeadlineSeconds': math.ceil(remaining_seconds), 'template': pod}}
    cm = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': name, 'namespace': namespace},
          'immutable': True, 'data': {'envelope.json': encode(envelope).decode()}}
    path = resource_path(envelope).split('/')
    paths=[path]
    if config.get('image_key_resource'):
        image_path=config['image_key_resource'].split('/')
        if image_path[0]!=envelope['customer']:raise PermissionError('Image-Schlüssel muss zum selben Kunden gehören.')
        paths.append(image_path)
    gpu_check = '\n    input["submods"]["gpu0"]["ear_status"] == "affirming"' if node.gpu_memory_gb else ''
    # This is per job. Do not replace a shared KBS policy with it; combine approved
    # per-job clauses on the trusted broker or use a dedicated broker per tenant.
    policy = f'''package policy
import rego.v1

default allow = false

allow if {{
    data.plugin == "resource"
    data["resource-path"] in {json.dumps(paths)}
    input["submods"]["cpu0"]["ear_status"] == "affirming"
    input["submods"]["cpu0"]["ear_attester_claims"]["tee"] == "tdx"
    input["submods"]["cpu0"]["ear_attester_claims"]["init_data"] == "{config['approved_initdata_sha384']}"{gpu_check}
}}
'''
    return dict(manifest={'apiVersion': 'v1', 'kind': 'List', 'items': [cm, job]}, resource_policy=policy,
                key_resource='/'.join(path), hardware_attested_here=False)
