import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.scheduler.resource_queue import ResourceQueue,Requirements,Node,Customer
from src.scheduler.runtime_config import HealthFile,apply_service_plan


class Clock:
    def __init__(self):self.now=1000.
    def __call__(self):return self.now


class ResourceQueueTests(unittest.TestCase):
    def setUp(self):
        self.clock=Clock()
        self.nodes=[Node('gpu',ram_gb=32,cpu_cores=8,gpu_memory_gb=(24,24),gpu_model='L4',slots=4,
                         executor='plan_only',region='CH',approved_customers=('a','b'),max_classification='confidential')]
        self.customers=[Customer('a',priority=2,max_classification='confidential'),Customer('b',priority=0,max_classification='confidential')]
        self.q=ResourceQueue(self.nodes,self.customers,clock=self.clock)

    def submit(self,jid='j',customer='a',**kw):
        req=kw.pop('requirements',Requirements(gpu_count=1,gpu_memory_gb=24,ram_gb=8))
        return self.q.submit(jid,customer,req,runtime_seconds=kw.pop('runtime_seconds',20),**kw)

    def test_vram_is_per_gpu_not_summed(self):
        self.submit(requirements=Requirements(gpu_count=1,gpu_memory_gb=48))
        self.assertEqual(self.q.dispatch(),[])
        self.assertIn('VRAM',self.q.snapshot('j')['waiting_reason'])

    def test_atomic_gpu_and_host_ram_reservations(self):
        self.submit('one',requirements=Requirements(gpu_count=1,gpu_memory_gb=24,ram_gb=24))
        self.submit('two',requirements=Requirements(gpu_count=1,gpu_memory_gb=24,ram_gb=24))
        self.assertEqual(len(self.q.dispatch()),1)
        self.q.finish('one')
        self.assertEqual([j.id for j in self.q.dispatch()],['two'])

    def test_customer_priority_comes_from_policy(self):
        self.submit('standard');self.submit('urgent','b')
        self.assertEqual(self.q.dispatch(max_assignments=1)[0].id,'urgent')
        with self.assertRaises(ValueError):Requirements.parse({'priority':0})

    def test_customer_permission_is_checked_before_queueing(self):
        q=ResourceQueue(self.nodes,[Customer('a')],clock=self.clock)
        with self.assertRaises(PermissionError):q.submit('secret','a',Requirements(classification='confidential'))
        self.assertEqual(q.jobs,{})

    def test_expired_approval_and_region_block_dispatch(self):
        self.submit(requirements=Requirements(region='DE'))
        self.assertEqual(self.q.dispatch(),[])
        self.nodes[0].region='DE';self.nodes[0].approved_until=self.clock.now
        self.assertEqual(self.q.dispatch(),[])

    def test_synthetic_ml_risk_is_advisory_only(self):
        self.q.set_health('gpu',risk=.99)
        self.assertEqual(self.nodes[0].maintenance,'ready')
        self.q.set_health('gpu',risk=.99,empirically_validated=True)
        self.assertEqual(self.nodes[0].maintenance,'drain')

    def test_critical_lock_is_latched_and_releases_no_running_reservation(self):
        self.submit();self.q.dispatch()
        self.q.set_health('gpu',critical=True)
        self.assertFalse(self.q.can_run('j')[0])
        self.assertEqual(len(self.q._held('gpu')),1)
        self.q.set_health('gpu',critical=False)
        self.assertEqual(self.nodes[0].maintenance,'isolated')
        self.q.set_health('gpu',clear=True)
        self.assertTrue(self.q.can_run('j')[0])

    def test_drain_allows_running_job_but_rejects_new_work(self):
        self.submit();self.q.dispatch();self.nodes[0].maintenance='drain'
        self.submit('next')
        self.assertTrue(self.q.can_run('j')[0])
        self.assertEqual(self.q.dispatch(),[])

    def test_maintenance_deadline_blocks_jobs_that_cannot_finish_in_time(self):
        self.nodes[0].maintenance_due_at=self.clock.now+10
        self.submit(runtime_seconds=20)
        self.assertEqual(self.q.dispatch(),[])

    def test_deadlines_and_paused_jobs_cannot_hold_queue_forever(self):
        self.submit(deadline_at=self.clock.now+10,runtime_seconds=20)
        self.assertEqual(self.q.dispatch(),[])
        self.assertEqual(self.q.jobs['j'].state,'expired')

    def test_safe_backfill_preserves_expected_start_for_large_job(self):
        self.nodes[0].slots=2
        self.submit('running','b',runtime_seconds=10);self.q.dispatch()
        self.submit('big','b',requirements=Requirements(gpu_count=2,gpu_memory_gb=24),runtime_seconds=20)
        self.submit('small',runtime_seconds=5)
        self.assertEqual([j.id for j in self.q.dispatch()],['small'])
        self.clock.now+=5;self.q.finish('small')
        self.submit('too-long',runtime_seconds=20)
        self.assertEqual(self.q.dispatch(),[])
        self.clock.now+=5;self.q.finish('running')
        self.assertEqual(self.q.dispatch()[0].id,'big')

    def test_fairness_immediate_reservation_penalty(self):
        self.q=ResourceQueue(self.nodes,[Customer('a',priority=1),Customer('b',priority=1)],clock=self.clock)
        for jid,c in [('a1','a'),('a2','a'),('b1','b')]:self.submit(jid,c)
        self.assertEqual([j.customer for j in self.q.dispatch()],['a','b'])

    def test_packing_uses_already_active_node(self):
        self.nodes.append(Node('other',ram_gb=32,cpu_cores=8,gpu_memory_gb=(24,24),slots=4,executor='plan_only',approved_customers=('a','b')))
        self.q=ResourceQueue(self.nodes,self.customers,clock=self.clock)
        self.submit('first');self.q.dispatch()
        self.submit('second');self.q.dispatch()
        self.assertEqual(self.q.jobs['first'].node,self.q.jobs['second'].node)

    def test_overdue_executor_still_holds_resources(self):
        self.submit();self.q.dispatch();self.clock.now+=100
        self.submit('other',requirements=Requirements(gpu_count=2,gpu_memory_gb=24))
        self.assertEqual(self.q.dispatch(),[])
        self.assertFalse(self.q.can_run('j')[0])
        self.q.finish('j','failed')
        self.assertEqual(self.q.dispatch()[0].id,'other')

    def test_concurrent_dispatch_cannot_double_book(self):
        for i in range(10):self.submit(str(i))
        assigned=[]
        def run():assigned.extend(j.id for j in self.q.dispatch())
        threads=[threading.Thread(target=run) for _ in range(8)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual(len(assigned),2)
        self.assertEqual(len(set(assigned)),2)

    def test_power_recommendation_never_changes_hardware_state(self):
        self.clock.now+=400
        self.assertEqual(self.q.power_advice()[0]['action'],'sleep_recommended')
        self.assertEqual(self.nodes[0].power_state,'on')
        self.nodes[0].power_state='sleep';self.submit()
        self.assertEqual(self.q.power_advice()[0]['action'],'wake_recommended')
        self.assertEqual(self.q.dispatch(),[])

    def test_cpu_demo_cannot_claim_gpu_execution(self):
        with self.assertRaises(ValueError):Node('fake',ram_gb=4,cpu_cores=1,gpu_memory_gb=(24,))


class HealthFileTests(unittest.TestCase):
    def test_service_ml_bridge_keeps_shared_and_individual_dates_separate(self):
        node=Node('s',ram_gb=4,cpu_cores=1,site_id='house')
        q=ResourceQueue([node],[Customer('demo')])
        report={'synthetic':True,'servers':[{'server_id':'s','next_routine_date':'2030-06-01','risk_next_30_days_without_service':.99}],
                'site_service':{'site_id':'house','scheduled_dates':['2030-02-01']}}
        apply_service_plan(q,report)
        self.assertIsNone(node.server_service_due_at)
        self.assertEqual(node.maintenance,'ready')
        apply_service_plan(q,report,approve_dates=True)
        shared=node.cooling_service_due_at
        self.assertLess(shared,node.server_service_due_at)
        report.pop('site_service');report['servers'][0]['next_routine_date']='2031-06-01'
        apply_service_plan(q,report,approve_dates=True)
        self.assertEqual(node.cooling_service_due_at,shared)
        self.assertEqual(node.maintenance,'ready')  # synthetic .99 never becomes a hard risk lock

    def test_missing_stale_and_invalid_health_fails_closed(self):
        clock=Clock();node=Node('cpu',ram_gb=4,cpu_cores=1)
        q=ResourceQueue([node],[Customer('demo')],clock=clock)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'health.json';monitor=HealthFile(path,q);monitor.poll()
            q.submit('j','demo',Requirements())
            self.assertEqual(q.dispatch(),[])
            path.write_text(json.dumps({'observed_at':clock.now,'nodes':[{'id':'cpu'}]}));monitor.poll()
            self.assertEqual(len(q.dispatch()),1)
            q.finish('j');clock.now+=121;q.submit('next','demo',Requirements())
            monitor.poll();self.assertEqual(q.dispatch(),[])
            path.write_text('{broken');monitor.poll();self.assertIsNone(node.last_health_at)

    def test_live_sensor_fault_locks_only_when_applicable(self):
        clock=Clock();node=Node('cpu',ram_gb=4,cpu_cores=1,max_gpu_temp_c=85)
        q=ResourceQueue([node],[Customer('demo')],clock=clock)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'health.json';monitor=HealthFile(path,q)
            path.write_text(json.dumps({'observed_at':clock.now,'nodes':[{'id':'cpu','powered':False,'flow_lpm':0}]}));monitor.poll()
            self.assertEqual(node.maintenance,'ready')
            clock.now+=1
            path.write_text(json.dumps({'observed_at':clock.now,'nodes':[{'id':'cpu','powered':True,'flow_lpm':0}]}));monitor.poll()
            self.assertEqual(node.maintenance,'isolated')


if __name__=='__main__':unittest.main()
