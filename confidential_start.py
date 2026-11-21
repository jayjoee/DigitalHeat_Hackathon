#!/usr/bin/env python3
"""Customer encryption, CoCo deployment planning and overhead sensitivity; no dashboard."""
import argparse
import http.client
import json
import os
from pathlib import Path
import ssl
import hashlib
import uuid
from urllib.parse import urlsplit

from src.confidential.costs import Overhead
from src.confidential.deployment import bundle, load_deployment
from src.confidential.envelope import encode, private_write, seal, unseal, validate, resource_path
from src.scheduler.resource_queue import Customer, Node, Requirements, ResourceQueue


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('seal', help='Nur auf dem vertrauenswürdigen Kundengerät ausführen')
    s.add_argument('--input', type=Path, required=True, help='Öffentlicher Text für den ersten geschützten Textstatistik-Test')
    s.add_argument('--customer', required=True)
    s.add_argument('--key-file', type=Path, required=True, help='Privater Kundenpfad; niemals auf den Haushaltsserver kopieren')
    s.add_argument('--out', type=Path, required=True)
    s.add_argument('--runtime-seconds', type=int, default=60)
    s.add_argument('--deadline-seconds', type=int, default=3600)
    s.add_argument('--ram-gb', type=float, default=1)
    s.add_argument('--gpu-count', type=int, choices=(0,1), default=0)
    s.add_argument('--gpu-memory-gb', type=float, default=0)
    plan = sub.add_parser('plan', help='CoCo-Manifest und Trustee-Ressourcenpolicy erzeugen; führt nichts aus')
    plan.add_argument('--request', type=Path, required=True)
    plan.add_argument('--inventory', type=Path, required=True)
    plan.add_argument('--deployment-config', type=Path, required=True)
    plan.add_argument('--out', type=Path, required=True)
    init = sub.add_parser('initdata', help='Bereits geprüfte Agent-Policy und Trustee-Zertifikat in gemessene Konfiguration verpacken')
    init.add_argument('--agent-policy', type=Path, required=True)
    init.add_argument('--kbs-url', required=True)
    init.add_argument('--kbs-cert', type=Path, required=True)
    init.add_argument('--out', type=Path, required=True)
    send = sub.add_parser('submit', help='Nur das verschlüsselte Paket an die vertrauenswürdige zentrale Steuerung senden')
    send.add_argument('--request', type=Path, required=True)
    send.add_argument('--worker', required=True)
    send.add_argument('--credentials', type=Path, required=True)
    dec = sub.add_parser('decrypt-result', help='Ergebnis ausschliesslich auf dem Kundengerät entschlüsseln')
    dec.add_argument('--result', type=Path, required=True)
    dec.add_argument('--request', type=Path, required=True)
    dec.add_argument('--key-file', type=Path, required=True)
    dec.add_argument('--out', type=Path, required=True)
    est = sub.add_parser('estimate', help='Ungeprüfte Mehrverbrauchsszenarien, kein Hardwarebenchmark')
    est.add_argument('--seconds', type=float, default=3600)
    est.add_argument('--kw', type=float, default=1)
    args = p.parse_args()
    try:
        if args.command == 'seal':
            req = Requirements(gpu_count=args.gpu_count,gpu_memory_gb=args.gpu_memory_gb,
                               ram_gb=args.ram_gb,classification='confidential')
            if not 1<=args.runtime_seconds<=86400 or not 1<=args.deadline_seconds<=604800:
                raise ValueError('Ungültige Laufzeit oder Frist.')
            if args.input.stat().st_size>100*1024:
                raise ValueError('Erster Prototyp: maximal 100 KiB Text.')
            payload=encode({'operation':'text_statistics','text':args.input.read_text(encoding='utf-8')})
            key=os.urandom(32);jid=str(uuid.uuid4())
            envelope=seal(payload,key,args.customer,jid)
            args.out.mkdir(mode=0o700,parents=True,exist_ok=False)
            private_write(args.key_file,key)
            request=dict(envelope=envelope,requirements=req.__dict__,runtime_seconds=args.runtime_seconds,deadline_seconds=args.deadline_seconds)
            private_write(args.out/'request.json',encode(request)+b'\n')
            print('Verschlüsselter Auftrag erstellt. Schlüssel bleibt getrennt auf dem Kundengerät.')
            print('Trustee-Ressource: '+resource_path(envelope))
        elif args.command == 'initdata':
            target=urlsplit(args.kbs_url)
            if target.scheme!='https' or not target.hostname or target.username or target.password or target.query or target.fragment or target.path not in ('','/'):
                raise ValueError('HTTPS-Trustee-Adresse benötigt.')
            cert=args.kbs_cert.read_text()
            if 'BEGIN CERTIFICATE' not in cert:raise ValueError('Trustee-Zertifikat fehlt.')
            policy=args.agent_policy.read_text()
            if not policy.strip():raise ValueError('Geprüfte Agent-Policy fehlt.')
            cdh='[kbc]\nname = "cc_kbc"\nurl = '+json.dumps(args.kbs_url)+'\nkbs_cert = '+json.dumps(cert)+'\n'
            aa='[token_configs.kbs]\nurl = '+json.dumps(args.kbs_url)+'\ncert = '+json.dumps(cert)+'\n'
            raw=('version = "0.1.0"\nalgorithm = "sha384"\n[data]\n'+
                 '\n'.join(json.dumps(k)+' = '+json.dumps(v) for k,v in {'policy.rego':policy,'cdh.toml':cdh,'aa.toml':aa}.items())+'\n').encode()
            private_write(args.out,raw)
            print('Init-Data erstellt; keine automatische Prüfung der Agent-Policy.')
            print('SHA384: '+hashlib.sha384(raw).hexdigest())
        elif args.command == 'plan':
            request=json.loads(args.request.read_text());envelope=validate(request['envelope'],direction='input')
            inventory=json.loads(args.inventory.read_text())
            customers=[Customer(**{k:v for k,v in c.items() if k!='token_env'}) for c in inventory['customers']]
            queue=ResourceQueue([Node(**n) for n in inventory['nodes']],customers,**inventory.get('scheduler',{}))
            queue.submit(envelope['job_id'],envelope['customer'],Requirements.parse(request['requirements']),
                         runtime_seconds=request['runtime_seconds'],deadline_at=queue.clock()+request['deadline_seconds'])
            assigned=queue.dispatch(executors=('confidential_coco',))
            if not assigned:raise ValueError(queue.snapshot(envelope['job_id'])['waiting_reason'])
            ticket=assigned[0]
            prepared=bundle(queue.nodes[ticket.node],ticket,envelope,load_deployment(args.deployment_config),ticket.finish_by-queue.clock())
            args.out.mkdir(mode=0o700,parents=True,exist_ok=False)
            private_write(args.out/'manifest.json',encode(prepared['manifest'])+b'\n')
            private_write(args.out/'resource-policy.rego',prepared['resource_policy'].encode())
            print('Bereitstellungsplan erstellt. Keine Hardware attestiert, kein Cluster verändert.')
        elif args.command == 'submit':
            request=json.loads(args.request.read_text());validate(request['envelope'],direction='input')
            target=urlsplit(args.worker)
            if target.scheme!='https' or not target.hostname or target.path not in ('','/') or target.username or target.password or target.query or target.fragment:
                raise ValueError('Erwartet wird die HTTPS-Adresse der zentralen Steuerung.')
            context=ssl.create_default_context(cafile=str(args.credentials/'worker-cert.pem'))
            context.minimum_version=ssl.TLSVersion.TLSv1_3
            token=(args.credentials/'token.txt').read_text().strip()
            if len(token)<40:raise ValueError('Ungültiger Kundenzugang.')
            conn=http.client.HTTPSConnection(target.hostname,target.port or 443,context=context,timeout=30)
            try:
                conn.request('POST','/v1/confidential-jobs',encode(request),{'Authorization':'Bearer '+token,'Content-Type':'application/json'})
                result=conn.getresponse();body=result.read(1024*1024)
                if result.status!=202:raise ValueError('Auftrag wurde von der zentralen Steuerung abgelehnt.')
                print('Verschlüsselter Auftrag angenommen: '+json.loads(body)['id'])
            finally:conn.close()
        elif args.command == 'decrypt-result':
            original=validate(json.loads(args.request.read_text())['envelope'],direction='input')
            result=validate(json.loads(args.result.read_text()),direction='output',customer=original['customer'])
            if result['job_id']!=original['job_id']:raise ValueError('Falsche Auftrags-ID.')
            private_write(args.out,unseal(result,args.key_file.read_bytes(),'output'))
            print('Ergebnis auf dem Kundengerät entschlüsselt.')
        else:
            scenarios={'low':Overhead(.02,0), 'planning':Overhead(), 'stress':Overhead(.30,.10)}
            print(json.dumps({name:profile.estimate(args.seconds,args.kw) for name,profile in scenarios.items()},indent=2,ensure_ascii=False))
    except Exception:
        # Never expose exception bodies from crypto, input parsers, HTTP or keys.
        p.exit(1,'Vorgang fehlgeschlagen. Eingaben und Konfiguration prüfen; keine Schlüssel oder Klartextdaten protokolliert.\n')


if __name__=='__main__':main()
