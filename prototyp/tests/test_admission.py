import http.client
import json
from pathlib import Path
import secrets
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import digitalheat as app
from src.scheduler.resource_queue import ResourceQueue,Node,Customer


class LiveQueueTests(unittest.TestCase):
    def setUp(self):
        self.q=ResourceQueue([Node('cpu',ram_gb=4,cpu_cores=1,approved_customers=('demo','urgent'))],
                             [Customer('demo',priority=2),Customer('urgent',priority=0)])
        self.store=app.Store(scheduler=self.q)
    def tearDown(self):self.store.close()
    def wait(self,jid,predicate,seconds=5):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            job=self.store.get(jid)
            if predicate(job):return job
            time.sleep(.03)
        self.fail('Erwarteter Warteschlangenzustand nicht erreicht.')

    def test_authenticated_customer_priority_changes_real_cpu_start_order(self):
        self.store.set_heat(False)
        low=self.store.submit({'text':'public','duration':2})
        high=self.store.submit({'text':'public','duration':2},'urgent')
        self.store.set_heat(True)
        self.wait(high['id'],lambda j:j['state']=='running')
        self.assertEqual(self.store.get(low['id'])['active_seconds'],0)
        self.wait(high['id'],lambda j:j['state']=='completed')
        self.wait(low['id'],lambda j:j['state']=='completed')

    def test_real_cpu_worker_never_runs_gpu_request(self):
        job=self.store.submit({'text':'public','duration':2,'requirements':{'gpu_count':1,'gpu_memory_gb':24}})
        time.sleep(.15)
        job=self.store.get(job['id'])
        self.assertEqual(job['state'],'queued')
        self.assertEqual(job['progress'],0)
        self.assertIn('GPU',job['waiting_reason'])

    def test_critical_health_pauses_cpu_without_freeing_resources_early(self):
        job=self.store.submit({'text':'public','duration':10})
        self.wait(job['id'],lambda j:j['active_seconds']>0)
        self.q.set_health('cpu',critical=True)
        paused=self.wait(job['id'],lambda j:j['state']=='paused')
        time.sleep(.15)
        self.assertEqual(self.store.get(job['id'])['active_seconds'],paused['active_seconds'])
        self.assertEqual(len(self.q._held('cpu')),1)
        self.q.set_health('cpu',clear=True)
        self.wait(job['id'],lambda j:j['active_seconds']>paused['active_seconds'])
        self.store.control(job['id'],'cancel')

    def test_client_cannot_claim_priority_or_submit_restricted_payload(self):
        for data in ({'text':'public','priority':0},{'text':'secret','requirements':{'classification':'confidential'}}):
            with self.assertRaises(app.APIError) as cm:self.store.submit(data)
            self.assertEqual(cm.exception.status,403)
        self.assertEqual(self.store.jobs,{})

    def test_tenant_reads_and_controls_are_scoped(self):
        self.store.set_heat(False)
        job=self.store.submit({'text':'public'})
        self.assertEqual(self.store.list('urgent'),[])
        with self.assertRaises(app.APIError):self.store.get(job['id'],'urgent')
        with self.assertRaises(app.APIError):self.store.control(job['id'],'cancel','urgent')
        self.assertEqual(self.store.get(job['id'])['state'],'paused')


class TokenIsolationTests(unittest.TestCase):
    def test_https_token_identity_cannot_read_or_control_another_customers_job(self):
        with tempfile.TemporaryDirectory() as temp:
            credentials=Path(temp)/'credentials';app.init_credentials('127.0.0.1',credentials)
            q=ResourceQueue([Node('cpu',ram_gb=4,cpu_cores=1,approved_customers=('demo','other'))],
                            [Customer('demo'),Customer('other')])
            token=secrets.token_urlsafe(48)
            worker=app.make_worker('127.0.0.1',0,credentials/'worker',scheduler=q,customer_tokens={'other':token})
            worker.store.set_heat(False)
            thread=threading.Thread(target=worker.serve_forever,daemon=True);thread.start()
            try:
                job=worker.store.submit({'text':'Only customer demo may see this','duration':2})
                context=app.tls_context(str(credentials/'sender/worker-cert.pem'))
                def request(method,path,data=None):
                    c=http.client.HTTPSConnection('127.0.0.1',worker.server_port,context=context,timeout=3)
                    c.request(method,path,json.dumps(data) if data is not None else None,
                              {'Authorization':'Bearer '+token,'Content-Type':'application/json'})
                    r=c.getresponse();code=r.status;body=json.loads(r.read());c.close();return code,body
                self.assertEqual(request('GET','/v1/status')[1]['jobs'],[])
                self.assertEqual(request('GET','/v1/jobs/'+job['id'])[0],404)
                self.assertEqual(request('POST','/v1/jobs/'+job['id']+'/cancel',{})[0],404)
                self.assertEqual(worker.store.get(job['id'])['state'],'paused')
            finally:
                worker.shutdown();worker.server_close();worker.store.close();thread.join()


if __name__=='__main__':unittest.main()
