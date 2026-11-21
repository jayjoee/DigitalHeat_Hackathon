import json
import gzip
from pathlib import Path
import tempfile
import unittest
import sys
import shlex
import subprocess
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from messung import parse_power,integrate,summarize,load_texts,text_hash,read_wall_csv,METER_SHELL

class MeasurementTests(unittest.TestCase):
    def test_combined_power_not_double_counted(self):
        raw='''*** Sampled system activity (Fri Nov 20 21:31:00 2026 +0100) (1000.0ms elapsed) ***
CPU Power: 1000 mW
GPU Power: 500 mW
ANE Power: 100 mW
Combined Power (CPU + GPU + ANE): 1600 mW
'''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'power.txt';p.write_text(raw);samples=parse_power(p)
            compressed=Path(d)/'power.txt.gz';compressed.write_bytes(gzip.compress(raw.encode()))
            self.assertEqual(parse_power(compressed),samples)
        self.assertEqual(len(samples),1)
        self.assertAlmostEqual(samples[0]['watts'],1.6)
        r=integrate(samples,samples[0]['start'],samples[0]['end'])
        self.assertAlmostEqual(r['energy_wh_estimate'],1.6/3600)

    def test_partial_overlap_is_weighted(self):
        s=[{'start':0,'end':2,'watts':10},{'start':2,'end':4,'watts':20}]
        r=integrate(s,1,3)
        self.assertAlmostEqual(r['energy_wh_estimate'],30/3600)
        self.assertAlmostEqual(r['coverage'],1)

    def test_overlapping_samples_never_double_count_time(self):
        r=integrate([{'start':0,'end':2,'watts':10},{'start':1,'end':3,'watts':10}],0,3)
        self.assertAlmostEqual(r['coverage'],1)
        self.assertAlmostEqual(r['energy_wh_estimate'],30/3600)

    def test_no_power_means_unknown_not_zero(self):
        self.assertIsNone(integrate([],0,10)['energy_wh_estimate'])
        self.assertIsNone(integrate([{'start':0,'end':1,'watts':10}],0,10)['energy_wh_estimate'])

    def test_identical_input_and_no_energy_assumption_in_summary(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.jsonl';p.write_text(json.dumps({'text':'public test'})+'\n')
            a=load_texts(p,3);b=load_texts(p,3)
            self.assertEqual(text_hash(a),text_hash(b))
        r=summarize([{'variant':'standard','compute_seconds':2,'full_process_seconds':3,'texts_per_second':10,
                      'quality':{'close_to_reference':True},'soc_compute':{'energy_wh_estimate':None}}])
        self.assertIsNone(r[0]['median_soc_compute_wh'])

    def test_external_measurements_must_have_matching_trials_and_scope(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'wall.csv'
            p.write_text('trial_id,energy_wh,scope\na,1.5,full_process\n')
            self.assertEqual(read_wall_csv(p,{'a'}),{'a':1.5})
            for text in ['a,-1,full_process','a,nan,full_process','b,1,full_process','a,1,compute','a,1,full_process\na,2,full_process']:
                p.write_text('trial_id,energy_wh,scope\n'+text+'\n')
                with self.assertRaises(ValueError):read_wall_csv(p,{'a'})

    def test_meter_helper_stops_its_child_without_second_sudo(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fake=root/'fake_meter.py';log=root/'ready';stop=root/'STOP'
            fake.write_text("import signal,sys,time\nfrom pathlib import Path\nsignal.signal(signal.SIGINT,lambda *args:sys.exit(0))\nPath(sys.argv[sys.argv.index('-o')+1]).write_text('ready')\nwhile True:time.sleep(.05)\n")
            shell=METER_SHELL.replace('/usr/bin/powermetrics',shlex.quote(sys.executable)+' '+shlex.quote(str(fake)))
            proc=subprocess.Popen(['/bin/sh','-c',shell,'test',str(log),str(stop)])
            try:
                deadline=time.monotonic()+3
                while not log.exists() and time.monotonic()<deadline:time.sleep(.02)
                self.assertTrue(log.exists())
                stop.touch()
                self.assertEqual(proc.wait(timeout=3),0)
            finally:
                if proc.poll() is None:proc.terminate();proc.wait(timeout=3)

    def test_short_windows_and_bad_intervals_visible(self):
        self.assertTrue(integrate([],0,2)['short_window_warning'])
        with self.assertRaises(ValueError):integrate([],1,0)

if __name__=='__main__':unittest.main()
