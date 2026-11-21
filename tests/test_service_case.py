import unittest
import numpy as np

from src.service_case import case_trace,calendar_operations,case_fleet,site_plan
from src.service_ml import FEATURES,validate_rows,trajectory,ServiceConfig,plan_server,renewal,validate_operations


class CaseTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.trace=case_trace()

    def test_case_totals_unchanged_by_per_server_instrumentation(self):
        t=self.trace['totals']
        self.assertEqual(t['starts'],717)
        self.assertAlmostEqual(t['it_kwh'],35662.1,delta=.05)
        self.assertAlmostEqual(t['compute_hours'],34511.6,delta=.05)
        self.assertAlmostEqual(t['powered_hours']+t['standby_hours'],8*8760)
        self.assertEqual(len(self.trace['rows']),8*365)

    def test_real_slots_are_not_replaced_by_fleet_average(self):
        rows=self.trace['rows'];ids={r['server_id'] for r in rows}
        self.assertEqual(len(ids),8)
        totals=[sum(r['powered_hours'] for r in rows if r['server_id']==sid) for sid in ids]
        self.assertGreater(max(totals)-min(totals),100)
        for r in rows:
            self.assertLessEqual(r['compute_hours'],r['powered_hours']+1e-9)
            self.assertEqual(r['powered_hours']+r['standby_hours'],24)

    def test_calendar_rotation_keeps_full_year_totals_and_dates(self):
        operations=calendar_operations(self.trace,'2026-11-21',365)
        for field in ('powered_hours','compute_hours','starts','it_kwh'):
            self.assertAlmostEqual(sum(r[field] for rows in operations.values() for r in rows),self.trace['totals'][field])
        self.assertEqual(next(iter(operations.values()))[0]['source_date'],'2025-11-21')
        self.assertEqual(next(iter(operations.values()))[-1]['date'],'2027-11-20')

    def test_leap_day_is_explicit_reference_day_repetition(self):
        operations=calendar_operations(self.trace,'2028-02-28',3)
        rows=next(iter(operations.values()))
        self.assertEqual(rows[1]['date'],'2028-02-29')
        self.assertEqual(rows[1]['source_date'],'2025-02-28')

    def test_inventory_counters_and_dates_are_consistent(self):
        fleet=validate_rows(case_fleet(self.trace))
        self.assertEqual(len(fleet),8)
        self.assertEqual(len({r['site_id'] for r in fleet}),1)
        for s in fleet:
            self.assertLessEqual(s['compute_hours'],s['operating_hours'])


class ExposureTests(unittest.TestCase):
    def setUp(self):
        self.server=dict(server_id='s',date='2026-11-21',server_age_days=730,operating_hours=1000,
                         compute_hours=400,power_on_fraction=1,starts_total=20,starts_24h=0,
                         days_since_service=30,load_fraction=.5,gpu_temp_c=65,coolant_inlet_c=34,
                         flow_lpm=4,pump_current_a=1.1,ecc_errors_24h=2,ssd_wear_percent=10)

    def test_powered_compute_and_start_counters_are_separate(self):
        ops=[dict(powered_hours=24,compute_hours=6,starts=1),dict(powered_hours=0,compute_hours=0,starts=0),dict(powered_hours=12,compute_hours=12,starts=1)]
        x=trajectory(self.server,np.arange(3),np.array([30,0,1]),ops)
        np.testing.assert_allclose(x[:,FEATURES.index('operating_hours')],[1000,1024,1024])
        np.testing.assert_allclose(x[:,FEATURES.index('compute_hours')],[400,406,406])
        np.testing.assert_allclose(x[:,FEATURES.index('starts_total')],[20,21,21])
        np.testing.assert_allclose(x[:,FEATURES.index('starts_24h')],[0,1,0])
        np.testing.assert_allclose(x[:,FEATURES.index('flow_lpm')],[4,4,4])

    def test_bad_operation_profiles_rejected(self):
        for row in (dict(powered_hours=1,compute_hours=2,starts=0),dict(powered_hours=25,compute_hours=0,starts=0),dict(powered_hours=0,compute_hours=0,starts=-1)):
            with self.assertRaises(ValueError):validate_operations([row],1)

    def test_schedule_exposure_reaches_the_risk_model(self):
        class ExposureModel:
            bounds=np.array([[-1e9,1e9]]*len(FEATURES))
            def probability(self,x):
                return .001+.02*np.asarray(x)[:,FEATURES.index('power_on_fraction')]
        cfg=ServiceConfig(horizon_days=30,intervals=(365,))
        active=[dict(powered_hours=24,compute_hours=12,starts=0)]*30
        standby=[dict(powered_hours=0,compute_hours=0,starts=0)]*30
        a=plan_server(ExposureModel(),self.server,cfg,active)
        b=plan_server(ExposureModel(),self.server,cfg,standby)
        self.assertGreater(a['selected']['expected_unplanned'],b['selected']['expected_unplanned'])
        self.assertEqual(a['forecast_exposure']['powered_hours'],720)
        self.assertEqual(b['forecast_exposure']['powered_hours'],0)

    def test_stationary_power_hours_do_not_multiply_by_load(self):
        x=trajectory(self.server,np.array([0,1]),np.array([30,31]))
        self.assertEqual(x[1,FEATURES.index('operating_hours')],1024)
        self.assertEqual(x[1,FEATURES.index('compute_hours')],412)


class SharedCoolingTests(unittest.TestCase):
    def test_cooling_calendar_survives_daily_server_repairs(self):
        site=site_plan('2026-11-21',365,8)
        cfg=ServiceConfig(horizon_days=365,intervals=(365,))
        repairs=renewal(np.ones((365,366)),0,365,cfg)
        self.assertEqual(repairs['expected_unplanned'],365)
        self.assertEqual(site,site_plan('2026-11-21',365,8))
        self.assertEqual(site['scheduled_cooling_visits'],2)
        self.assertEqual(site['cooling_budget_chf'],1200)
        self.assertEqual(site['allocated_budget_per_server_chf'],150)

    def test_shared_visits_are_not_multiplied_by_server_count(self):
        a=site_plan('2026-11-21',365,1);b=site_plan('2026-11-21',365,8)
        self.assertEqual(a['scheduled_cooling_visits'],b['scheduled_cooling_visits'])
        self.assertEqual(a['cooling_budget_chf'],b['cooling_budget_chf'])
        self.assertEqual(b['server_hours_unavailable'],8*a['server_hours_unavailable'])

    def test_overdue_shared_service_is_due_today(self):
        s=site_plan('2026-11-21',30,8,days_since_service=200)
        self.assertEqual(s['scheduled_dates'],['2026-11-21'])

    def test_bad_site_configuration_rejected(self):
        for kwargs in ({'interval_days':0},{'cost_chf':-1},{'downtime_h':25},{'days_since_service':-1}):
            with self.assertRaises(ValueError):site_plan('2026-11-21',365,8,**kwargs)


if __name__=='__main__':unittest.main()
