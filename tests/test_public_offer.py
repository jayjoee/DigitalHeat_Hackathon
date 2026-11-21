import unittest
from dataclasses import replace
from src.scheduler.resource_queue import Customer,Node,Requirements,ResourceQueue
from prototyp.digitalheat import Store,APIError


class PublicOfferTests(unittest.TestCase):
    def queue(self,approved=False):
        return ResourceQueue([Node('cpu',ram_gb=4,cpu_cores=1)],
                             [Customer('demo',allow_customer_anonymized=approved)],public_only=True)

    def test_internal_and_confidential_data_rejected_before_queueing(self):
        q=self.queue()
        for classification in ('internal','confidential'):
            with self.assertRaises(PermissionError):q.submit(classification,'demo',Requirements(classification=classification))
        self.assertEqual(q.jobs,{})

    def test_public_and_synthetic_data_keep_normal_scheduling(self):
        for basis in ('public','synthetic'):
            q=self.queue();q.submit('j','demo',Requirements(data_basis=basis))
            self.assertEqual(q.dispatch()[0].id,'j')

    def test_anonymized_work_requires_both_workflow_approval_and_release_reference(self):
        with self.assertRaises(ValueError):Requirements(data_basis='customer_anonymized')
        req=Requirements(data_basis='customer_anonymized',release_reference='release_20261121')
        with self.assertRaises(PermissionError):self.queue().submit('j','demo',req)
        q=self.queue(approved=True);q.submit('j','demo',req)
        self.assertEqual(q.dispatch()[0].id,'j')

    def test_revoked_workflow_approval_blocks_running_processing(self):
        q=self.queue(approved=True)
        q.submit('j','demo',Requirements(data_basis='customer_anonymized',release_reference='release_20261121'))
        q.dispatch();q.customers['demo']=replace(q.customers['demo'],allow_customer_anonymized=False)
        self.assertFalse(q.can_run('j')[0])
        self.assertTrue(q.snapshot('j')['resource_lease_active'])

    def test_revoked_workflow_cannot_start_a_queued_job(self):
        q=self.queue(approved=True)
        q.submit('j','demo',Requirements(data_basis='customer_anonymized',release_reference='release_20261121'))
        q.customers['demo']=replace(q.customers['demo'],allow_customer_anonymized=False)
        self.assertEqual(q.dispatch(),[])

    def test_public_configuration_cannot_accidentally_enable_protected_inventory(self):
        with self.assertRaises(ValueError):ResourceQueue([Node('cpu',ram_gb=4,cpu_cores=1,max_classification='confidential')],[Customer('demo')],public_only=True)
        with self.assertRaises(ValueError):ResourceQueue([Node('cpu',ram_gb=4,cpu_cores=1)],[Customer('demo',max_classification='confidential')],public_only=True)
        with self.assertRaises(ValueError):Store(scheduler=self.queue(),confidential_executor=object())

    def test_default_worker_explicitly_rejects_encrypted_private_endpoint(self):
        store=Store();self.addCleanup(store.close)
        self.assertTrue(store.scheduler.public_only)
        with self.assertRaises(APIError) as cm:store.submit_confidential({},'demo')
        self.assertEqual(cm.exception.status,403)
        self.assertEqual(store.jobs,{})


if __name__=='__main__':unittest.main()
