#!/usr/bin/env python3
"""Controlled CPU embedding benchmark. No power assumptions masquerading as measurements."""
import argparse
from datetime import datetime,timezone,timedelta
import csv
import hashlib
import gzip
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import shutil
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
DEFAULT_DATA=(ROOT.parent/'daten/agnews_test.jsonl') if (ROOT.parent/'daten/agnews_test.jsonl').exists() else ROOT/'daten/agnews_test.jsonl'
MODEL='BAAI/bge-small-en-v1.5'
VARIANTS=[{'id':'standard','name':'Standard','threads':6,'batch':16},
          {'id':'weniger_threads','name':'Weniger CPU-Threads','threads':2,'batch':16},
          {'id':'groessere_pakete','name':'Grössere Verarbeitungspakete','threads':6,'batch':64}]

METER_SHELL = r"""
child=""
finish() {
    if [ -n "$child" ]; then
        /bin/kill -INT "$child" 2>/dev/null || true
        wait "$child" 2>/dev/null || true
        child=""
    fi
}
trap 'finish' EXIT
trap 'finish; exit 0' INT TERM HUP
LC_ALL=C /usr/bin/powermetrics --samplers cpu_power,gpu_power,ane_power -i 1000 -n 1800 -b 1 -o "$1" &
child=$!
while /bin/kill -0 "$child" 2>/dev/null; do
    if [ -e "$2" ]; then
        finish
        exit 0
    fi
    /bin/sleep 0.25
done
wait "$child"
child=""
"""

def write_json(path,data):
    path=Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False));tmp.replace(path)

def load_texts(path,count):
    if not 1<=count<=100000:raise ValueError('Textzahl muss zwischen 1 und 100000 liegen.')
    with Path(path).open(encoding='utf-8') as f:rows=[json.loads(line)['text'] for line in f if line.strip()]
    if not rows or not all(isinstance(x,str) for x in rows):raise ValueError('Ungültiger Textdatensatz.')
    return [rows[i%len(rows)] for i in range(count)]

def text_hash(texts):return hashlib.sha256(json.dumps(texts,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def worker(args):
    # Import/model loading are included in full-process time, outside steady-state inference time.
    import numpy as np
    import onnxruntime as ort
    ort.disable_telemetry_events()
    from fastembed import TextEmbedding
    texts=load_texts(args.data,args.texts)
    directory=Path(args.trial_dir)
    t0=time.perf_counter();load_start=time.time()
    model=TextEmbedding(MODEL,threads=args.threads,providers=['CPUExecutionProvider'],local_files_only=not args.download)
    load_end=time.time()
    # Same warm-up quantity in every variant; only batch and threads differ.
    list(model.embed(texts[:min(64,len(texts))],batch_size=args.batch,parallel=None))
    warmup_end=time.time()
    begin=time.time();cpu=time.process_time();steady=time.perf_counter()
    vectors=np.asarray(list(model.embed(texts,batch_size=args.batch,parallel=None)),dtype=np.float32)
    steady_seconds=time.perf_counter()-steady;cpu_seconds=time.process_time()-cpu;end=time.time()
    if vectors.shape!=(len(texts),384) or not np.isfinite(vectors).all():raise ValueError('Ungültige Embedding-Ausgabe.')
    np.save(directory/'vectors.npy',vectors)
    result={'texts':len(texts),'input_sha256':text_hash(texts),'model':MODEL,'provider':'CPUExecutionProvider',
            'threads':args.threads,'batch':args.batch,'model_load_start':load_start,'model_load_end':load_end,
            'warmup_end':warmup_end,'compute_start':begin,'compute_end':end,
            'compute_seconds':steady_seconds,'cpu_seconds':cpu_seconds,
            'texts_per_second':len(texts)/steady_seconds,'worker_seconds':time.perf_counter()-t0,
            'output_shape':list(vectors.shape),'output_sha256':hashlib.sha256(vectors.tobytes()).hexdigest(),
            'versions':{x:importlib.metadata.version(x) for x in ['numpy','onnxruntime','fastembed']}}
    write_json(directory/'worker.json',result)

def compare_vectors(reference,candidate):
    import numpy as np
    a=np.load(reference,allow_pickle=False);b=np.load(candidate,allow_pickle=False)
    if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('Ungleiche oder ungültige Vektoren.')
    denom=np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)
    if np.any(denom<=0):raise ValueError('Nullvektoren verhindern den Ergebnisvergleich.')
    cosine=np.clip(np.sum(a*b,axis=1)/denom,-1,1)
    return {'min_cosine':float(cosine.min()),'mean_cosine':float(cosine.mean()),
            'max_absolute_difference':float(np.max(np.abs(a-b))),
            'close_to_reference':bool(cosine.min()>=.999),
            'meaning':'Numerische Ähnlichkeit, keine wissenschaftliche/medizinische Qualitätsvalidierung.'}

MONTHS={m:i for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(),1)}
def sample_time(value):
    # Locale-independent parser for powermetrics' English timestamps.
    _,month,day,clock,year,offset=value.split()
    h,m,s=map(int,clock.split(':'));sign=1 if offset[0]=='+' else -1
    tz=timezone(sign*timedelta(hours=int(offset[1:3]),minutes=int(offset[3:5])))
    return datetime(int(year),MONTHS[month],int(day),h,m,s,tzinfo=tz).timestamp()

def parse_power(path):
    if Path(path).suffix=='.gz':
        with gzip.open(path,'rt',errors='replace') as f:raw=f.read()
    else:
        raw=Path(path).read_text(errors='replace')
    chunks=re.split(r'\*\*\* Sampled system activity \((.+?)\) \(([\d.]+)ms elapsed\) \*\*\*',raw)
    samples=[]
    for i in range(1,len(chunks)-2,3):
        try:end=sample_time(chunks[i]);duration=float(chunks[i+1])/1000
        except (ValueError,KeyError):continue
        values=re.findall(r'^(CPU|GPU|ANE) Power:\s*([\d.]+)\s*mW\s*$',chunks[i+2],re.M)
        if not values or duration<=0:continue
        watts=sum(float(v) for _,v in values)/1000
        if not math.isfinite(watts) or watts<0:continue
        samples.append({'start':end-duration,'end':end,'watts':watts})
    return sorted(samples,key=lambda x:x['end'])

def integrate(samples,start,end):
    if end<=start:raise ValueError('Leeres Messfenster.')
    wh=covered=0.0;last=start
    for sample in samples:
        left=max(start,sample['start'],last);right=min(end,sample['end'])
        if right>left:
            wh+=sample['watts']*(right-left)/3600;covered+=right-left;last=right
    coverage=covered/(end-start)
    return {'energy_wh_estimate':wh if coverage>=.9 else None,'coverage':coverage,
            'mean_watts_estimate':wh*3600/covered if covered else None,
            'source':'powermetrics CPU+GPU+ANE estimates; not wall power',
            'short_window_warning':end-start<10}

def summarize(trials):
    out=[]
    for variant in VARIANTS:
        selected=[t for t in trials if t['variant']==variant['id']]
        if not selected:continue
        energies=[t.get('soc_compute',{}).get('energy_wh_estimate') for t in selected]
        valid=[v for v in energies if v is not None]
        out.append({'variant':variant['id'],'name':variant['name'],'trials':len(selected),
                    'median_compute_seconds':statistics.median(t['compute_seconds'] for t in selected),
                    'min_compute_seconds':min(t['compute_seconds'] for t in selected),
                    'max_compute_seconds':max(t['compute_seconds'] for t in selected),
                    'median_full_process_seconds':statistics.median(t['full_process_seconds'] for t in selected),
                    'median_texts_per_second':statistics.median(t['texts_per_second'] for t in selected),
                    'median_soc_compute_wh':statistics.median(valid) if len(valid)==len(selected) else None,
                    'median_wall_full_process_wh':statistics.median(t['wall_full_process_wh'] for t in selected) if all(t.get('wall_full_process_wh') is not None for t in selected) else None,
                    'all_outputs_close':all(t['quality']['close_to_reference'] for t in selected)})
    return out

def read_wall_csv(path,known_trials):
    if not path:return {}
    readings={}
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            if not row.get('energy_wh','').strip():continue
            trial=row.get('trial_id')
            if trial not in known_trials or trial in readings or row.get('scope')!='full_process':
                raise ValueError('Unbekannter/doppelter Durchlauf oder falsches Messfenster in der Steckdosen-CSV.')
            value=float(row['energy_wh'])
            if not math.isfinite(value) or value<=0:raise ValueError('Externe Energie muss endlich und positiv sein.')
            readings[trial]=value
    return readings

def analyse(folder,power=None,wall_csv=None):
    folder=Path(folder);run=json.loads((folder/'run.json').read_text())
    if len(run['trials'])!=run['repeats']*len(VARIANTS) or {t['variant'] for t in run['trials']}!={v['id'] for v in VARIANTS}:
        raise ValueError('Messlauf unvollständig. Keine vollständige Varianten-Auswertung möglich.')
    trials=[]
    wall=read_wall_csv(wall_csv,{t['id'] for t in run['trials']})
    samples=parse_power(power) if power else []
    if power and not samples:raise ValueError('Keine auswertbaren Leistungssamples. powermetrics-Protokoll prüfen.')
    baseline=next(t for t in run['trials'] if t['variant']=='standard')
    reference=folder/baseline['id']/'vectors.npy'
    for trial in run['trials']:
        item={**trial,**json.loads((folder/trial['id']/'worker.json').read_text())}
        if item['input_sha256']!=run['input_sha256'] or item['texts']!=run['texts']:
            raise ValueError('Eingaben zwischen Durchläufen verändert. Vergleich ungültig.')
        item['wall_full_process_wh']=wall.get(trial['id'])
        item['quality']=compare_vectors(reference,folder/trial['id']/'vectors.npy')
        item['soc_compute']=integrate(samples,item['compute_start'],item['compute_end'])
        item['soc_full_process']=integrate(samples,trial['process_start'],trial['process_end'])
        if not power:
            item['soc_compute']['source']=item['soc_full_process']['source']='Nicht gemessen'
        trials.append(item)
    result={**run,'trials':trials,'summary':summarize(trials),'power_log':str(power) if power else None,
            'idle':integrate(samples,run['idle_start'],run['idle_end']),
            'limitations':['CPU-Test auf diesem Rechner, keine NVIDIA-L4-Messung.',
                'Weniger Threads ist kein GPU-Power-Cap und kein aktivierter macOS-Stromsparmodus.',
                'Grössere Batches lassen keinen Schluss auf ausgeschaltete Server zu. Kein automatisches Abschalten.',
                'powermetrics sind geschätzte Chip-Leistungswerte; Display, Netzteil und weitere Verbraucher fehlen.',
                'Ohne Leistungsmessung wird keine Energieersparnis berechnet.',
                'Numerischer Vektorvergleich ist keine Pharma- oder Retrieval-Qualitätsvalidierung.',
                'Andere laufende Programme und Temperatur beeinflussen die Ergebnisse.']}
    write_json(folder/'ergebnisse.json',result)
    with (folder/'ergebnisse.csv').open('w',newline='') as f:
        rows=[{k:t[k] for k in ('id','variant','threads','batch','texts','compute_seconds','full_process_seconds','texts_per_second')}|
              {'min_cosine':t['quality']['min_cosine'],'soc_compute_wh':t['soc_compute']['energy_wh_estimate'],
               'power_coverage':t['soc_compute']['coverage'],'wall_full_process_wh':t['wall_full_process_wh']} for t in trials]
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    lines=['# Messlauf auf dem vorhandenen Rechner','',f"Modell: {MODEL}. Gleiche {run['texts']} Texte pro Durchlauf. Wiederholungen: {run['repeats']}.",'',
           '| Variante | Median Rechenzeit | Texte/s | Numerisch ähnlich | Chip-Energie (Rechnen) | Steckdose (Gesamtprozess) |','|---|---:|---:|---|---|---|']
    for s in result['summary']:
        energy=f"{s['median_soc_compute_wh']:.5f} Wh (Chip-Schätzung)" if s['median_soc_compute_wh'] is not None else 'Nicht gemessen'
        external=f"{s['median_wall_full_process_wh']:.5f} Wh" if s['median_wall_full_process_wh'] is not None else 'Nicht gemessen'
        lines.append(f"| {s['name']} | {s['median_compute_seconds']:.3f} s | {s['median_texts_per_second']:.1f} | {'Ja' if s['all_outputs_close'] else 'Nein – prüfen'} | {energy} | {external} |")
    lines+=['','Die Messung zeigt Laufzeit und numerische Vergleichbarkeit. Ohne Leistungsdaten lässt sich daraus keine Energieeinsparung ableiten.',
            'Der erste Lauf ist Referenz. Die Variantenreihenfolge wird pro Wiederholung mit fester Zufallssaat gemischt; Standard wird anfangs zuerst ausgeführt.',
            'Kurze Durchläufe sind Funktionsprüfungen. Für eine Energieauswertung längere ruhige Messläufe und idealerweise ein externes Messgerät verwenden.','',
            '## Grenzen','',*['- '+x for x in result['limitations']]]
    (folder/'BERICHT.md').write_text('\n'.join(lines)+'\n')
    if not (folder/'steckdose_vorlage.csv').exists():
        with (folder/'steckdose_vorlage.csv').open('w',newline='') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(['trial_id','start_unix','end_unix','energy_wh','scope'])
            for t in run['trials']:w.writerow([t['id'],t['process_start'],t['process_end'],'','full_process'])
    return result

def main():
    p=argparse.ArgumentParser(description='DigitalHeat: fairer CPU-Embedding-Messlauf')
    p.add_argument('--texts',type=int,default=2048);p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--cooldown',type=float,default=3);p.add_argument('--idle-seconds',type=float,default=10)
    p.add_argument('--out');p.add_argument('--download',action='store_true',help='Modell herunterladen, falls nicht lokal vorhanden')
    p.add_argument('--powermetrics',action='store_true',help='macOS-Chip-Schätzungen sammeln; fragt im Terminal nach sudo')
    p.add_argument('--analyse',help='Vorhandenen Lauf erneut auswerten');p.add_argument('--power-log');p.add_argument('--wall-csv',help='Externe Energie je Prozess aus passendem Messfenster')
    p.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    p.add_argument('--threads',type=int,default=6);p.add_argument('--batch',type=int,default=16)
    p.add_argument('--trial-dir');p.add_argument('--data',default=str(DEFAULT_DATA))
    a=p.parse_args()
    if a.worker:return worker(a)
    if a.analyse:
        r=analyse(a.analyse,a.power_log,a.wall_csv);print(Path(a.analyse)/'BERICHT.md');return
    if not 1<=a.texts<=100000 or not 1<=a.repeats<=10 or not 0<=a.cooldown<=60 or not 1<=a.idle_seconds<=60:
        p.error('Textzahl, Wiederholungen oder Wartezeiten ausserhalb des unterstützten Bereichs.')
    # Fail before creating an incomplete measurement folder if the execution environment is absent.
    import importlib.util
    if importlib.util.find_spec('fastembed') is None:p.error('FastEmbed fehlt. Bitte die Einrichtung laut README.md verwenden.')
    out=Path(a.out) if a.out else ROOT/'laeufe'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    out.mkdir(parents=True,exist_ok=False)
    monitor=None;log=out/'powermetrics.txt';stop_file=out/'STOP_MEASUREMENT'
    run={'model':MODEL,'texts':a.texts,'repeats':a.repeats,'input_sha256':text_hash(load_texts(a.data,a.texts)),
         'hardware':{'machine':platform.machine(),'os':platform.platform(),'logical_cpus':os.cpu_count()},
         'load_average_before':list(os.getloadavg()) if hasattr(os,'getloadavg') else None,
         'variants':VARIANTS,'trials':[],'python_version':platform.python_version()}
    def stop_monitor():
        if monitor is not None and monitor.poll() is None:
            # Signal only this explicitly-created measurement process; never stop arbitrary processes.
            stop_file.touch()  # Root helper owns its child; no second sudo call/cache needed.
            try:monitor.wait(timeout=8)
            except subprocess.TimeoutExpired:raise RuntimeError('Messprozess läuft weiter. Bitte das Mess-Terminal prüfen.')
    try:
        if a.powermetrics:
            if sys.platform!='darwin' or not shutil.which('powermetrics'):raise RuntimeError('powermetrics ist nur auf macOS verfügbar.')
            subprocess.run(['sudo','-v'],check=True)
            env={**os.environ,'LC_ALL':'C'}
            monitor=subprocess.Popen(['sudo','-n','/bin/sh','-c',METER_SHELL,'digitalheat-meter',str(log.resolve()),str(stop_file.resolve())],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        print(f'Messordner: {out}',flush=True)
        print('Ausgangszustand erfassen …',flush=True)
        run['idle_start']=time.time();time.sleep(a.idle_seconds);run['idle_end']=time.time()
        if monitor is not None and monitor.poll() is not None:raise RuntimeError('powermetrics konnte nicht gestartet werden.')
        rng=random.Random(2025)
        for repeat in range(a.repeats):
            variants=list(VARIANTS)
            if repeat:rng.shuffle(variants)
            for v in variants:
                tid=f"{repeat+1:02d}_{v['id']}";folder=out/tid;folder.mkdir()
                print(f"{repeat+1}/{a.repeats}: {v['name']} · {v['threads']} Threads · Paket {v['batch']}",flush=True)
                record={'id':tid,'variant':v['id'],'repeat':repeat+1,'process_start':time.time()}
                elapsed_start=time.perf_counter()
                cmd=[sys.executable,str(Path(__file__).resolve()),'--worker','--trial-dir',str(folder.resolve()),
                     '--texts',str(a.texts),'--threads',str(v['threads']),'--batch',str(v['batch']),'--data',str(Path(a.data).resolve())]
                if a.download:cmd.append('--download')
                with (folder/'prozess.log').open('w') as log_file:
                    child=subprocess.Popen(cmd,stdout=log_file,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                    try:code=child.wait(timeout=1800)
                    except BaseException:
                        child.terminate()
                        try:child.wait(timeout=10)
                        except subprocess.TimeoutExpired:child.kill();child.wait()
                        raise
                record['process_end']=time.time();record['full_process_seconds']=time.perf_counter()-elapsed_start
                if code:raise RuntimeError(f'Durchlauf {tid} fehlgeschlagen; siehe {folder}/prozess.log. Modell gegebenenfalls mit --download bereitstellen.')
                run['trials'].append(record);write_json(out/'run.json',run)
                time.sleep(a.cooldown)
        stop_monitor();monitor=None
        result=analyse(out,log if a.powermetrics else None)
        print(f"Fertig: {out/'BERICHT.md'}",flush=True)
        for s in result['summary']:print(f"{s['name']}: {s['median_compute_seconds']:.3f} s; {s['median_texts_per_second']:.1f} Texte/s",flush=True)
        print('Energie: Chip-Schätzungen, keine Steckdosenmessung.' if a.powermetrics else 'Keine Energiewerte gemessen; keine Energieeinsparung behauptet.',flush=True)
    finally:
        stop_monitor()
        write_json(out/'run.json',run)

if __name__=='__main__':main()
