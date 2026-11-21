"""Trusted-control-plane kubectl adapter. No keys and no plaintext pass through it."""
import json
import subprocess
import time
from .deployment import bundle, load_deployment
from .envelope import MAX_ENVELOPE, validate


class CoCoExecutor:
    def __init__(self, config_path):
        self.config = load_deployment(config_path)

    def _kubectl(self, *args, payload=None):
        result = subprocess.run(['kubectl', '--namespace', self.config['namespace'], *args],
                                input=payload, capture_output=True, timeout=40, check=False)
        if result.returncode:
            # Never reflect kubectl output: API messages can contain workload data.
            raise RuntimeError('CoCo-Clusteroperation fehlgeschlagen.')
        return result.stdout

    def run(self, queue, jid, envelope, stopping):
        ticket = queue.jobs[jid]
        node = queue.nodes[ticket.node]
        prepared = bundle(node, ticket, envelope, self.config, ticket.finish_by-queue.clock())
        name = 'cc-' + jid
        acknowledged = False
        succeeded = False
        try:
            # Trustee policy/key provisioning is deliberately separate. Without a
            # matching external KBS policy the guest cannot decrypt even if started.
            self._kubectl('create', '-f', '-', payload=json.dumps(prepared['manifest']).encode())
            while not stopping.is_set():
                allowed, reason = queue.can_run(jid)
                if not allowed:
                    # No unsafe emulation of pause/checkpoint for GPU containers.
                    raise RuntimeError('Geschützte Ausführung gestoppt: ' + reason)
                status = json.loads(self._kubectl('get', 'job', name, '-o', 'json')).get('status', {})
                if status.get('failed'):
                    raise RuntimeError('Geschützter Auftrag fehlgeschlagen; keine Klartextdiagnose.')
                if status.get('succeeded'):
                    raw = self._kubectl('logs', 'job/' + name, '-c', 'worker')
                    if len(raw) > MAX_ENVELOPE:
                        raise RuntimeError('Ungültige Ergebnisgrösse.')
                    result = validate(json.loads(raw), direction='output', customer=ticket.customer)
                    if result['job_id'] != jid:
                        raise RuntimeError('Ergebnis gehört zu einem anderen Auftrag.')
                    succeeded = True
                    return result
                stopping.wait(.5)
            raise RuntimeError('Steuerung wird beendet.')
        finally:
            try:
                # Synchronised deletion: do not reuse a GPU after an unconfirmed stop.
                self._kubectl('delete', 'job', name, '--ignore-not-found=true', '--wait=true', '--timeout=25s')
                acknowledged = True
                try:self._kubectl('delete', 'configmap', name, '--ignore-not-found=true', '--wait=true')
                except RuntimeError:pass  # Ciphertext-only cleanup failure does not undo process-stop acknowledgement.
            finally:
                if acknowledged:
                    queue.finish(jid, 'completed' if succeeded else 'failed')
                else:
                    queue.set_health(node.id, critical=True)
                    # Lease stays active until operator confirms actual termination.
