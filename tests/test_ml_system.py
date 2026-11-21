"""Checks model integrity, temporal separation, actual ML use, conservation and local API boundaries."""
import copy
from dataclasses import replace
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.ml_system.config import Config
from src.ml_system.forecast import Forecast
from src.ml_system.simulation import WorkJob,simulate,make_jobs,jobs_digest
from src.scheduler.jahr import profil_laden
from src.wirtschaft import variable_bilanz

class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile=profil_laden();cls.model=Forecast(cls.profile).fit()

    def test_training_is_strictly_before_calibration_and_evaluation(self):
        self.assertTrue(all(self.profile[t]['zeit']<'2025-06-01' for t in self.model.train_indices))
        self.assertFalse(self.model.model.early_stopping)
        self.assertGreater(self.model.info['training_rows'],1000)

    def test_future_observations_do_not_enter_forecast_features(self):
        h=5000;t=h+6
        before=self.model.features(h,t)
        future=self.model.heat[h:].copy()
        try:
            self.model.heat[h:]=999999
            self.assertEqual(before,self.model.features(h,t))
        finally:self.model.heat[h:]=future

    def test_weather_run_is_available_before_decision(self):
        for h in (1000,2080,5000,7200):
            for horizon in (1,6,24):
                _,available=self.model.weather_value(h,h+horizon)
                self.assertLessEqual(available,self.model.times[h])

    def test_trained_predictions_respond_to_forecast_inputs(self):
        h=1000
        original=self.model.predict(h,6)
        saved=copy.deepcopy(self.model.weather)
        try:
            for field in ('temperature_2m_previous_day1','temperature_2m_previous_day2'):
                for t in range(h+1,h+7):self.model.weather[field][t]=30
            changed=self.model.predict(h,6)
            self.assertGreater(sum(abs(a-b) for a,b in zip(original,changed)),.1)
        finally:self.model.weather=saved

class EnergyTests(unittest.TestCase):
    @staticmethod
    def profile(count=48):
        return [{'zeit':f'2025-07-{1+h//24:02d}T{h%24:02d}:00','temp':20.,'heizung':0.,'ww':.5,'sonne':0.} for h in range(count)]

    def test_bad_profiles_rejected(self):
        for kw in ({'servers':True},{'economy_kw':.1},{'storage_loss_per_hour':1},{'backup_cop':0}, {'off_kw':float('nan')},{'startup_minutes':60}):
            with self.assertRaises(ValueError):Config(**kw)

    def test_identical_forecasts_give_identical_optimized_physics(self):
        p=self.profile();cfg=Config(servers=2)
        jobs=[WorkJob(i,'A',i,i+24,1.,True,1.) for i in range(24)]
        forecasts={h:[.5]*6 for h in range(48)}
        a=simulate(p,cfg,jobs,0,48,'efficient',forecasts)
        b=simulate(p,cfg,jobs,0,48,'ml',forecasts)
        self.assertEqual(a['energy'],b['energy'])
        self.assertEqual(a['completed_work'],24.)
        self.assertEqual(a['submitted_jobs'],a['completed_jobs']+a['pending_jobs']+a['missed_jobs'])
        self.assertAlmostEqual(sum(j.remaining_work for j in jobs),24.) # caller's jobs never mutated

    def test_no_jobs_do_not_create_revenue_and_heat_is_balanced(self):
        p=self.profile();cfg=Config(servers=2)
        r=simulate(p,cfg,[],0,48,'standard')
        self.assertEqual(r['business']['revenue_chf'],0)
        self.assertGreater(r['energy']['idle_kwh'],0)
        self.assertAlmostEqual(r['energy']['demand_kwh'],r['energy']['useful_heat_kwh']+r['energy']['backup_heat_kwh'])
        self.assertAlmostEqual(r['energy']['total_kwh'],r['energy']['it_kwh']+r['energy']['pump_kwh']+r['energy']['backup_kwh'])

    def test_power_off_is_separate_from_idle_and_backup_is_counted(self):
        p=self.profile();cfg=Config(servers=2)
        f={h:[.5]*6 for h in range(48)}
        r=simulate(p,cfg,[],0,48,'efficient',f)
        self.assertEqual(r['energy']['idle_kwh'],0)
        self.assertAlmostEqual(r['energy']['off_kwh'],48*2*cfg.off_kw)
        self.assertAlmostEqual(r['energy']['backup_kwh'],48*.5/cfg.backup_cop)

    def test_energy_and_saleable_work_are_independent(self):
        a=variable_bilanz(10,8);b=variable_bilanz(20,8)
        self.assertEqual(a['revenue_chf'],b['revenue_chf'])
        self.assertAlmostEqual(a['contribution_chf']-b['contribution_chf'],10*.3325)
        self.assertEqual(variable_bilanz(100,0)['revenue_chf'],0)

    def test_short_deadlines_and_startup_loss_are_not_hidden(self):
        p=self.profile(2);cfg=Config(servers=1,startup_minutes=30)
        jobs=[WorkJob(1,'A',0,1,1.,True,1.)]
        r=simulate(p,cfg,jobs,0,2,'efficient',{0:[.5],1:[.5]})
        self.assertEqual(r['missed_jobs'],1)
        self.assertEqual(r['completed_jobs'],0)
        self.assertEqual(r['business']['revenue_chf'],0)
        self.assertGreater(r['energy']['startup_kwh'],0)

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ml_start
        cls.server=ml_start.make_server(0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,data=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        h={'Content-Type':'application/json','X-DigitalHeat-CSRF':self.server.csrf}
        h.update(headers or {});c.request(method,path,json.dumps(data) if data is not None else None,h)
        r=c.getresponse();status=r.status;r.read();c.close();return status
    def test_origin_csrf_and_path_boundaries(self):
        self.assertEqual(self.request('GET','/api/session',headers={'Host':'foreign.example'}),403)
        self.assertEqual(self.request('GET','/api/status',headers={'Origin':'https://foreign.example'}),403)
        self.assertEqual(self.request('POST','/api/run',{}, {'X-DigitalHeat-CSRF':'wrong'}),403)
        self.assertEqual(self.request('GET','/../../ml_start.py'),404)
        self.assertEqual(self.request('GET','/src/github_token.sh'),404)
    def test_input_rejected_before_starting_training(self):
        for d in ({'days':True},{'days':10000},{'start':'2025-01-01'},{'config':{'servers':0}}, {'config':{'electricity_chf_kwh':-1}}, {'config':{'servers':'8'}}):
            self.assertEqual(self.request('POST','/api/run',d),400)
        self.assertFalse(self.server.state.running)

if __name__=='__main__':unittest.main()
