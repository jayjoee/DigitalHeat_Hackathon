"""Regression and access checks for the guided case demonstration."""
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from start.demo_start import make_server

class GuidedDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=make_server(0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,data=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        h={'Content-Type':'application/json','X-DigitalHeat-CSRF':self.server.csrf};h.update(headers or {})
        c.request(method,path,json.dumps(data) if data is not None else None,h)
        r=c.getresponse();status=r.status;raw=r.read();kind=r.getheader('Content-Type');c.close()
        return status,json.loads(raw) if kind.startswith('application/json') else raw
    def test_year_matches_stored_case(self):
        gold=json.loads((ROOT/'daten/ergebnisse/bilanz_8_spot.json').read_text())
        self.assertEqual(self.server.demo.case['year'],gold)
    def test_demo_contains_heat_driven_compute_pause_and_resume(self):
        segments=self.server.demo.case['segments']
        self.assertTrue(all(len(s['hours'])==24 for s in segments))
        self.assertGreater(sum(r['duty'] for r in segments[0]['hours']),sum(r['duty'] for r in segments[1]['hours']))
        values=[r['duty'] for r in segments[2]['hours']]
        zero=next(i for i,x in enumerate(values) if x==0)
        self.assertTrue(any(x>0 for x in values[:zero]))
        self.assertTrue(any(x>0 for x in values[zero+1:]))
    def test_foreign_origin_and_missing_csrf_rejected(self):
        self.assertEqual(self.request('GET','/api/case',headers={'Origin':'https://foreign.example'})[0],403)
        self.assertEqual(self.request('GET','/api/live',headers={'Host':'foreign.example'})[0],403)
        self.assertEqual(self.request('POST','/api/start',{}, {'X-DigitalHeat-CSRF':'wrong'})[0],403)
        self.assertFalse(self.server.demo.snapshot()['active'])
    def test_only_public_demo_assets_served_and_invalid_commands_rejected(self):
        for path in ('/','/app.js','/style.css','/wallpaper.svg','/api/case','/api/live'):
            self.assertEqual(self.request('GET',path)[0],200)
        self.assertEqual(self.request('GET','/../../src/wirtschaft.py')[0],404)
        self.assertEqual(self.request('POST','/api/start',[])[0],400)
        self.assertEqual(self.request('POST','/api/unknown',{})[0],404)

if __name__=='__main__':unittest.main()
