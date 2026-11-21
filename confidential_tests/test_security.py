"""Local software tests only: these fixtures are NOT hardware attestation evidence."""
import base64
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import uuid

from cryptography.exceptions import InvalidTag
from src.confidential.envelope import encode, private_write, seal, unseal, validate
from src.confidential.guest import process
from src.confidential.costs import Overhead
from src.confidential.deployment import bundle, load_deployment
from src.confidential.executor import CoCoExecutor
from src.scheduler.resource_queue import ResourceQueue, Requirements, Node, Customer

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('digitalheat_cc_test',ROOT/'prototyp/digitalheat.py')
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.key=os.urandom(32);self.jid=str(uuid.uuid4())
        self.payload=encode({'operation':'text_statistics','text':'secret alpha alpha'})
        self.sealed=seal(self.payload,self.key,'pharma',self.jid)
        self.now=1000.
        self.node=Node('tdx-node',ram_gb=16,cpu_cores=4,executor='confidential_coco',tee_type='tdx',
                       max_classification='confidential',approved_customers=('pharma',))
        self.customer=Customer('pharma',max_classification='confidential')
        self.queue=ResourceQueue([self.node],[self.customer],clock=lambda:self.now)
        self.req=Requirements(classification='confidential')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)

    def config(self):
        # A dummy certificate/policy for software tests, never a deployment template.
        init='''version = "0.1.0"
algorithm = "sha384"
[data]
"policy.rego" = "package agent_policy\\ndefault ExecProcessRequest = false"
"cdh.toml" = ''' + "'''" + '''
[kbc]
name = "cc_kbc"
url = "https://broker.example.invalid"
kbs_cert = "BEGIN CERTIFICATE test-only"
''' + "'''" + '\n' + '''"aa.toml" = ''' + "'''" + '''
[token_configs.kbs]
url = "https://broker.example.invalid"
cert = "BEGIN CERTIFICATE test-only"
''' + "'''" + '\n'
        (self.directory/'init.toml').write_text(init)
        cfg=dict(namespace='cc-test',image='registry.example.invalid/worker@sha256:'+'a'*64,
                 initdata_file='init.toml',approved_initdata_sha384=hashlib.sha384(init.encode()).hexdigest(),
                 kbs_url='https://broker.example.invalid')
        path=self.directory/'deployment.json';path.write_text(json.dumps(cfg))
        return path

    def prepared(self,gpu=False):
        if gpu:
            self.node.gpu_memory_gb=(80,);self.node.gpu_model='H100'
            self.req=Requirements(classification='confidential',gpu_count=1,gpu_memory_gb=80)
        self.queue.submit(self.jid,'pharma',self.req,runtime_seconds=60)
        ticket=self.queue.dispatch(executors=('confidential_coco',))[0]
        return bundle(self.node,ticket,self.sealed,load_deployment(self.config()),ticket.finish_by-self.now)


class EncryptionTests(Fixture):
    def test_roundtrip_and_no_plaintext_in_package(self):
        self.assertNotIn(b'secret alpha',encode(self.sealed))
        self.assertEqual(unseal(self.sealed,self.key,'input'),self.payload)

    def test_modified_ciphertext_is_rejected(self):
        changed=copy.deepcopy(self.sealed)
        raw=bytearray(base64.b64decode(changed['ciphertext']));raw[0]^=1
        changed['ciphertext']=base64.b64encode(raw).decode()
        with self.assertRaises(InvalidTag):unseal(changed,self.key,'input')

    def test_wrong_key_customer_job_and_direction_cannot_decrypt(self):
        with self.assertRaises(InvalidTag):unseal(self.sealed,os.urandom(32),'input')
        for field,value in [('customer','other'),('job_id',str(uuid.uuid4())),('direction','output')]:
            changed={**self.sealed,field:value}
            with self.assertRaises(InvalidTag):unseal(changed,self.key,changed['direction'])
        with self.assertRaises(ValueError):unseal(self.sealed,self.key,'output')

    def test_repeated_encryption_uses_new_nonce(self):
        other=seal(self.payload,self.key,'pharma',self.jid)
        self.assertNotEqual(other['nonce'],self.sealed['nonce'])

    def test_no_cross_tenant_or_unknown_metadata_fields(self):
        with self.assertRaises(PermissionError):validate(self.sealed,customer='other')
        with self.assertRaises(ValueError):validate({**self.sealed,'key':base64.b64encode(self.key).decode()})

    def test_guest_output_is_always_encrypted(self):
        with patch('src.confidential.guest.fetch_key',return_value=self.key):result=process(self.sealed)
        self.assertNotIn(b'words',encode(result))
        self.assertEqual(json.loads(unseal(result,self.key,'output'))['words'],3)

    def test_key_denial_and_unsupported_operation_fail_closed(self):
        with patch('src.confidential.guest.fetch_key',side_effect=PermissionError):
            with self.assertRaises(PermissionError):process(self.sealed)
        bad=seal(encode({'operation':'shell','text':'arbitrary program'}),self.key,'pharma',self.jid)
        with patch('src.confidential.guest.fetch_key',return_value=self.key):
            with self.assertRaises(ValueError):process(bad)

    def test_key_files_are_private_and_never_overwritten(self):
        path=self.directory/'job.cckey';private_write(path,self.key)
        self.assertEqual(path.stat().st_mode & 0o777,0o600)
        with self.assertRaises(FileExistsError):private_write(path,b'overwrite')


class AdmissionTests(Fixture):
    def test_l4_cannot_be_declared_a_confidential_executor(self):
        with self.assertRaises(ValueError):Node('l4',ram_gb=32,cpu_cores=8,executor='confidential_coco',tee_type='tdx',gpu_memory_gb=(24,),gpu_model='L4')

    def test_security_label_alone_does_not_enable_confidential_execution(self):
        for executor in ('local_cpu_demo','gpu','plan_only'):
            node=Node('ordinary',ram_gb=32,cpu_cores=8,executor=executor,max_classification='confidential',approved_customers=('pharma',))
            q=ResourceQueue([node],[self.customer])
            q.submit(self.jid,'pharma',self.req)
            self.assertEqual(q.dispatch(),[])
            self.assertIn('CoCo',q.snapshot(self.jid)['waiting_reason'])

    def test_overhead_is_used_for_deadlines_maintenance_and_reservations(self):
        # 60 / .9 + 30 = 96.67 seconds, so a 90-second slot no longer fits.
        self.node.maintenance_due_at=self.now+90
        self.queue.submit(self.jid,'pharma',self.req,runtime_seconds=60)
        self.assertEqual(self.queue.dispatch(),[])
        self.node.maintenance_due_at=None
        self.queue.jobs[self.jid].deadline_at=self.now+90
        self.assertEqual(self.queue.dispatch(),[])
        self.assertEqual(self.queue.jobs[self.jid].state,'expired')

    def test_single_guest_owns_the_entire_gpu_node(self):
        prepared=self.prepared(gpu=True)
        self.assertEqual(prepared['manifest']['items'][1]['spec']['template']['spec']['containers'][0]['resources']['limits']['nvidia.com/pgpu'],'1')
        self.queue.submit(str(uuid.uuid4()),'pharma',self.req)
        self.assertEqual(self.queue.dispatch(),[])

    def test_plaintext_api_still_rejects_sensitive_input(self):
        store=app.Store();self.addCleanup(store.close)
        with self.assertRaises(app.APIError):store.submit({'text':'secret','requirements':{'classification':'confidential'}})
        with self.assertRaises(app.APIError) as cm:store.submit_confidential({},'pharma')
        self.assertEqual(cm.exception.status,403)

    def test_encrypted_api_keeps_only_ciphertext_and_binds_customer(self):
        store=app.Store(scheduler=self.queue,confidential_executor=object());self.addCleanup(store.close)
        store.set_heat(False)
        request=dict(envelope=self.sealed,requirements={'classification':'confidential'},runtime_seconds=60,deadline_seconds=3600)
        snapshot=store.submit_confidential(request,'pharma')
        self.assertIsNone(store.jobs[self.jid]['_text'])
        self.assertNotIn('secret alpha',json.dumps(snapshot))
        self.assertNotIn('_sealed',snapshot)
        with self.assertRaises(app.APIError):store.submit_confidential(request,'other')
        with self.assertRaises(app.APIError):store.submit_confidential({**request,'text':'secret'},'pharma')


class DeploymentTests(Fixture):
    def test_modified_initdata_is_rejected(self):
        path=self.config();(self.directory/'init.toml').write_text('modified')
        with self.assertRaises(ValueError):load_deployment(path)

    def test_floating_image_and_http_broker_are_rejected(self):
        for field,value in [('image','worker:latest'),('kbs_url','http://broker.example.invalid')]:
            path=self.config();data=json.loads(path.read_text());data[field]=value;path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_deployment(path)

    def test_manifest_has_no_plaintext_key_host_mount_or_service_account(self):
        prepared=self.prepared();raw=json.dumps(prepared)
        self.assertNotIn('secret alpha',raw)
        self.assertNotIn(base64.b64encode(self.key).decode(),raw)
        pod=prepared['manifest']['items'][1]['spec']['template']['spec']
        self.assertFalse(pod['automountServiceAccountToken'])
        self.assertEqual(pod['runtimeClassName'],'kata-qemu-tdx')
        self.assertFalse(any('hostPath' in v for v in pod['volumes']))
        self.assertEqual(prepared['key_resource'],'pharma/keys/'+self.jid)

    def test_failed_stop_confirmation_keeps_gpu_lease_and_locks_server(self):
        self.prepared()
        executor=CoCoExecutor(self.directory/'deployment.json')
        with patch.object(executor,'_kubectl',side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):executor.run(self.queue,self.jid,self.sealed,threading.Event())
        self.assertEqual(self.queue.jobs[self.jid].state,'running')
        self.assertEqual(self.node.maintenance,'isolated')

    def test_confirmed_failure_releases_resources(self):
        self.prepared();executor=CoCoExecutor(self.directory/'deployment.json')
        def kubectl(*args,**kwargs):
            if args[0]=='get':return b'{"status":{"failed":1}}'
            return b'{}'
        with patch.object(executor,'_kubectl',side_effect=kubectl):
            with self.assertRaises(RuntimeError):executor.run(self.queue,self.jid,self.sealed,threading.Event())
        self.assertEqual(self.queue.jobs[self.jid].state,'failed')
        self.assertEqual(self.queue._held(self.node.id),[])

    def test_success_returns_only_encrypted_result_and_acknowledges_stop(self):
        self.prepared();executor=CoCoExecutor(self.directory/'deployment.json')
        encrypted=seal(b'{"words":3}',self.key,'pharma',self.jid,'output')
        calls=[]
        def kubectl(*args,**kwargs):
            calls.append(args)
            if args[0]=='get':return b'{"status":{"succeeded":1}}'
            if args[0]=='logs':return encode(encrypted)
            return b'{}'
        with patch.object(executor,'_kubectl',side_effect=kubectl):
            result=executor.run(self.queue,self.jid,self.sealed,threading.Event())
        self.assertEqual(result,encrypted)
        self.assertEqual(self.queue.jobs[self.jid].state,'completed')
        self.assertTrue(any(c[:2]==('delete','job') for c in calls))

    def test_revoked_heat_permission_deletes_job_before_releasing_lease(self):
        self.prepared();executor=CoCoExecutor(self.directory/'deployment.json')
        self.node.heat_enabled=False
        calls=[]
        def kubectl(*args,**kwargs):calls.append(args);return b'{}'
        with patch.object(executor,'_kubectl',side_effect=kubectl):
            with self.assertRaises(RuntimeError):executor.run(self.queue,self.jid,self.sealed,threading.Event())
        self.assertEqual(self.queue.jobs[self.jid].state,'failed')
        self.assertTrue(any(c[:2]==('delete','job') for c in calls))

    def test_wrong_job_result_cannot_be_counted_as_success(self):
        self.prepared();executor=CoCoExecutor(self.directory/'deployment.json')
        wrong=seal(b'{}',self.key,'pharma',str(uuid.uuid4()),'output')
        def kubectl(*args,**kwargs):
            if args[0]=='get':return b'{"status":{"succeeded":1}}'
            if args[0]=='logs':return encode(wrong)
            return b'{}'
        with patch.object(executor,'_kubectl',side_effect=kubectl):
            with self.assertRaises(RuntimeError):executor.run(self.queue,self.jid,self.sealed,threading.Event())
        self.assertEqual(self.queue.jobs[self.jid].state,'failed')


class CostTests(unittest.TestCase):
    def test_throughput_loss_is_converted_to_runtime_correctly(self):
        profile=Overhead(.2,0,0,0,0)
        self.assertEqual(profile.runtime(100),125)
        self.assertAlmostEqual(profile.estimate(3600)['total_kwh'],1.25)

    def test_default_estimate_includes_setup_power_and_broker(self):
        result=Overhead().estimate(3600)
        self.assertAlmostEqual(result['total_kwh'],1.176)
        self.assertFalse(result['measured'])

    def test_invalid_assumptions_cannot_remove_protection_costs(self):
        for value in (-.1,1,float('nan'),True):
            with self.assertRaises(ValueError):Overhead(throughput_loss=value)


class PolicyTests(Fixture):
    def test_real_opa_denies_missing_gpu_wrong_guest_and_cross_job_resource(self):
        opa=os.environ.get('OPA_BIN') or shutil.which('opa')
        if not opa:self.skipTest('OPA_BIN setzen, um echte Rego-Auswertung auszuführen.')
        prepared=self.prepared(gpu=True)
        policy=self.directory/'policy.rego';policy.write_text(prepared['resource_policy'])
        path=['pharma','keys',self.jid]
        claims={'submods':{'cpu0':{'ear_status':'affirming','ear_attester_claims':{'tee':'tdx','init_data':load_deployment(self.directory/'deployment.json')['approved_initdata_sha384']}},'gpu0':{'ear_status':'affirming'}}}
        def evaluate(evidence,resource):
            inp=self.directory/'input.json';inp.write_text(json.dumps(evidence))
            data=self.directory/'data.json';data.write_text(json.dumps({'plugin':'resource','resource-path':resource}))
            result=subprocess.run([opa,'eval','--format=json','--data',str(policy),'--data',str(data),'--input',str(inp),'data.policy.allow'],capture_output=True,check=True)
            return json.loads(result.stdout)['result'][0]['expressions'][0]['value']
        self.assertTrue(evaluate(claims,path))
        self.assertFalse(evaluate({},path))
        self.assertFalse(evaluate(claims,['other','keys',self.jid]))
        missing=copy.deepcopy(claims);missing['submods'].pop('gpu0')
        self.assertFalse(evaluate(missing,path))
        bad=copy.deepcopy(claims);bad['submods']['cpu0']['ear_attester_claims']['init_data']='changed'
        self.assertFalse(evaluate(bad,path))
        bad=copy.deepcopy(claims);bad['submods']['gpu0']['ear_status']='contraindicated'
        self.assertFalse(evaluate(bad,path))


if __name__=='__main__':unittest.main()
