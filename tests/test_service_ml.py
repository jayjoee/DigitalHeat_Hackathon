import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from src.service_ml import (ServiceConfig, ServiceModel, FEATURES, TARGET, calculate,
                            demo_data, validate_rows, trajectory, renewal, plan_server)
from service_start import save_report


class RenewalTests(unittest.TestCase):
    def test_no_failures_produce_exact_calendar_count(self):
        cfg=ServiceConfig(intervals=(30,))
        r=renewal(np.zeros((365,31)),0,30,cfg)
        self.assertEqual(r['expected_planned'],12)
        self.assertEqual(r['expected_unplanned'],0)
        self.assertEqual(r['expected_total_cost_chf'],12*cfg.planned_chf)

    def test_constant_hazard_without_routine_matches_bernoulli_expectation(self):
        cfg=ServiceConfig(intervals=(365,),horizon_days=100)
        r=renewal(np.full((100,366),.02),0,365,cfg)
        self.assertAlmostEqual(r['expected_unplanned'],2)
        self.assertEqual(r['expected_planned'],0)

    def test_repair_restarts_service_clock_no_double_count(self):
        cfg=ServiceConfig(horizon_days=60,intervals=(30,))
        r=renewal(np.ones((60,31)),0,30,cfg)
        self.assertEqual(r['expected_unplanned'],60)
        self.assertEqual(r['expected_planned'],0)

    def test_due_service_excludes_second_intervention_same_day(self):
        cfg=ServiceConfig(horizon_days=1,intervals=(30,))
        r=renewal(np.ones((1,41)),40,30,cfg)
        self.assertEqual(r['expected_planned'],1)
        self.assertEqual(r['expected_unplanned'],0)

    def test_downtime_margin_is_not_implicitly_revenue(self):
        cfg=ServiceConfig(horizon_days=10,intervals=(30,),lost_margin_chf_h=5)
        r=renewal(np.ones((10,31)),0,30,cfg)
        self.assertEqual(r['expected_total_cost_chf'],10*(cfg.unplanned_chf+5*cfg.unplanned_downtime_h))

    def test_invalid_probabilities_rejected(self):
        for p in (-.1,1.1,float('nan')):
            with self.assertRaises(ValueError):renewal(np.full((365,31),p),0,30,ServiceConfig())

    def test_invalid_costs_and_intervals_rejected(self):
        for options in ({'planned_chf':-1},{'unplanned_chf':float('nan')},{'intervals':(0,)},
                        {'intervals':(366,)},{'horizon_days':True},{'planned_downtime_h':25}):
            with self.assertRaises(ValueError):ServiceConfig(**options)


class InputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.history,cls.fleet=demo_data(servers=12,days=10)

    def test_missing_and_impossible_telemetry_rejected(self):
        for change in ({'flow_lpm':float('nan')},{'load_fraction':1.2},{'operating_hours':87600},
                       {'date':'yesterday'},{'server_id':''},{'gpu_temp_c':True}):
            row={**self.fleet[0],**change}
            with self.assertRaises(ValueError):validate_rows([row])

    def test_censored_days_not_counted_as_negatives_and_duplicate_inventory_rejected(self):
        rows=copy.deepcopy(self.history[:2]);rows[0]['observed_24h']=0
        self.assertEqual(len(validate_rows(rows,True)),1)
        with self.assertRaises(ValueError):validate_rows([self.fleet[0],self.fleet[0]])

    def test_no_events_cannot_train_a_fake_predictor(self):
        rows=copy.deepcopy(self.history)
        for r in rows:r[TARGET]=0
        with self.assertRaises(ValueError):ServiceModel().fit(rows)

    def test_future_labels_not_used_for_current_fleet(self):
        history=copy.deepcopy(self.history);history[0]['date']='2027-01-01'
        with self.assertRaises(ValueError):calculate(history,self.fleet)

    def test_service_does_not_rejuvenate_hardware_or_ssd(self):
        s=self.fleet[0];x=trajectory(s,np.array([0,30]),np.array([0,0]))
        self.assertEqual(x[1,FEATURES.index('server_age_days')],s['server_age_days']+30)
        self.assertEqual(x[1,FEATURES.index('ssd_wear_percent')],x[0,FEATURES.index('ssd_wear_percent')])
        self.assertEqual(x[0,FEATURES.index('ecc_errors_24h')],s['ecc_errors_24h'])
        for name in ('flow_lpm','pump_current_a'):
            self.assertEqual(x[0,FEATURES.index(name)],s[name])


class MLIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history,cls.fleet=demo_data()
        cls.model=ServiceModel().fit(cls.history)

    def test_server_groups_disjoint_and_probability_model_trained(self):
        a,b,c=map(set,self.model.info['groups'])
        self.assertFalse(a&b or a&c or b&c)
        self.assertEqual(self.model.info['rows'],[38880,12960,12960])
        x=np.array([[r[f] for f in FEATURES] for r in self.fleet])
        p=self.model.probability(x)
        self.assertTrue(np.all((p>=0)&(p<=1)))
        self.assertGreater(float(p.max()-p.min()),.0001)

    def test_expected_counts_depend_on_learned_risk(self):
        # Same fleet/config, replace only learned hazard: expected emergencies must change.
        cfg=ServiceConfig(horizon_days=30,intervals=(30,60,365))
        a=plan_server(self.model,self.fleet[0],cfg)
        with patch.object(self.model,'probability',side_effect=lambda x:np.full(len(x),.5)):
            b=plan_server(self.model,self.fleet[0],cfg)
        self.assertGreater(b['selected']['expected_unplanned'],a['selected']['expected_unplanned'])
        self.assertTrue(all(c['expected_total']<=30+1e-8 for c in b['candidates']))

    def test_equal_costs_do_not_prefer_extra_routine_services(self):
        cfg=ServiceConfig(horizon_days=30,intervals=(60,365))
        with patch.object(self.model,'probability',side_effect=lambda x:np.zeros(len(x))):
            s=plan_server(self.model,self.fleet[0],cfg)
        self.assertEqual(s['recommended_interval_days'],365)

    def test_complete_export_contains_scenario_status_and_escapes_ids(self):
        cfg=ServiceConfig(horizon_days=30,intervals=(30,60,365))
        s=plan_server(self.model,{**self.fleet[0],'server_id':'<script>alert(1)</script>'},cfg)
        result={'status':'SYNTHETISCH','servers':[s],'model':self.model.info,'config':cfg.__dict__,
                'fleet_totals':s['selected'],'limitations':['Keine reale Vorhersage']}
        with tempfile.TemporaryDirectory() as tmp:
            page=save_report(result,tmp)
            self.assertIn('&lt;script&gt;',page.read_text())
            self.assertNotIn('<script>alert(1)</script>',page.read_text())
            data=json.loads((Path(tmp)/'service_plan.json').read_text())
            self.assertEqual(data['servers'][0]['selected']['interval_days'],s['recommended_interval_days'])
            self.assertTrue((Path(tmp)/'server_service.csv').exists())

    def test_assumptions_follow_actual_costs_without_inventing_evidence(self):
        cfg=ServiceConfig(horizon_days=30,intervals=(60,365),planned_chf=123.45,unplanned_chf=678.9)
        s=plan_server(self.model,self.fleet[0],cfg)
        result={'status':'SYNTHETISCH','synthetic':True,'servers':[s],'model':self.model.info,
                'config':cfg.__dict__,'fleet_totals':s['selected'],'limitations':[]}
        with tempfile.TemporaryDirectory() as tmp:
            page=save_report(result,tmp)
            entries={r['id']:r for r in result['assumptions']}
            self.assertIn('123.45',entries['planned_cost']['value'])
            self.assertIn('Keine empirische Quelle',entries['planned_cost']['source'])
            self.assertEqual(entries['planned_cost']['source_url'],'')
            self.assertFalse(entries['l4_reference']['used_in_calculation'])
            self.assertEqual(entries['generator_hazard']['source_url'],'')
            self.assertIn('nicht',entries['generator_hazard']['scope'])
            self.assertIn('id="annahmen"',page.read_text())
            self.assertTrue((Path(tmp)/'Annahmen_und_Quellen.md').exists())
            self.assertTrue((Path(tmp)/'annahmen.csv').exists())


if __name__=='__main__':unittest.main()
