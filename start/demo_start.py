#!/usr/bin/env python3
"""Guided main-case demonstration: annual reference + actual heat-controlled embedding job."""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # Repo-Wurzel, damit «src» gefunden wird
import argparse
from datetime import datetime,timezone
import importlib.util
import json
import mimetypes
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from src.scheduler.jahr import Haus
from src.scheduler.live import anteil,waehle_server

ROOT=Path(__file__).resolve().parents[1]
DAYS=[('2025-01-15','Winter: Wärme wird gebraucht'),('2025-07-15','Sommer: nur Warmwasser'),('2025-03-07','Speicher voll: Auftrag pausiert')]

def build_case():
    house=Haus(8,'spot','rechnen');days={date:[] for date,_ in DAYS}
    for h,p in enumerate(house.profil):
        row=house.schritt(h)
        if p['zeit'][:10] in days:days[p['zeit'][:10]].append(row)
    segments=[]
    for date,title in DAYS:
        rows=days[date];k=waehle_server(rows,8)
        segments.append({'date':date,'title':title,'slot':k+1,
                         'hours':[{**r,'duty':anteil(r['strom_kwh'],k)} for r in rows]})
    result={'year':house.bilanz(),'segments':segments,
            'assumptions':['Basel 2025, Referenzhaus, acht 1-kW-Server, 80 % Wärmerückgewinnung, 35-kWh-Speicher ohne Verluste.',
                'Spot-Szenario: unbegrenzt flexible Aufträge, kurze Aufträge nach Alibaba-Muster. Keine bewiesene Kundenabnahme.',
                'Rechenlast und Preis sind Annahmen. NVIDIA-L4-Hardware und nutzbare Heiztemperatur sind nicht gemessen.',
                'Die Live-Demo nutzt dieselbe Funktion Haus.schritt → kern.entscheide wie die Jahresbilanz.',
                'Ein repräsentativer modellierter Serverplatz steuert einen echten CPU-Prozess. Häuser und Wärme sind simuliert.',
                'Zeit wird beschleunigt. Der Job pausiert, der Rechner wird nicht ausgeschaltet. Keine Energiemessung in der Demo.',
                'Pharma-Daten werden nicht verarbeitet: öffentlicher Nachrichtentext, allgemeines Embedding-Modell.'],
            'explanation':'Ein echter Suchindex-Auftrag läuft dann, wenn der modellierte Serverplatz Wärme liefern soll.'}
    return result

def find_python():
    options=[os.environ.get('DIGITALHEAT_PYTHON'),ROOT/'.venv/bin/python',
             Path.home()/'Desktop/Smithers/DigitalHeat_Hackathon/.venv/bin/python',sys.executable]
    for candidate in options:
        if not candidate or not Path(candidate).exists():continue
        r=subprocess.run([str(candidate),'-c',"import importlib.util; raise SystemExit(0 if importlib.util.find_spec('fastembed') else 1)"],capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        if r.returncode==0:return str(candidate)
    raise ValueError('FastEmbed-Umgebung fehlt. Siehe docs/technik/GESAMTDEMO.md.')

def atomic(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=1));tmp.replace(path)

class Demo:
    def __init__(self,case,seconds=1.2):
        self.case=case;self.seconds=seconds;self.lock=threading.RLock();self.stop=threading.Event();self.thread=None
        self.state={'active':False,'stage':'Bereit','process':'Noch nicht gestartet','texts':0,'completed':False,'events':[], 'current':None,'error':None}
    def snapshot(self):
        with self.lock:return json.loads(json.dumps(self.state))
    def update(self,**kwargs):
        with self.lock:self.state.update(**kwargs)
    def launch(self):
        with self.lock:
            if self.state['active']:return False
            self.stop.clear();self.state={'active':True,'stage':'Modell vorbereiten','process':'Wird geladen','texts':0,'completed':False,'events':[],'current':None,'error':None}
            self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start();return True
    def run(self):
        job=None;log=None;folder=ROOT/'messungen'/'gesamtdemo'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
        events=[];paused=True;stopped=False
        def progress():
            try:return json.loads((folder/'stand.json').read_text())['naechster']
            except (FileNotFoundError,ValueError):return 0
        def emit(action,**extra):
            events.append({'action':action,'real_time':time.time(),**extra})
            self.update(events=list(events))
        def pause():
            nonlocal paused
            if paused:return
            job.send_signal(signal.SIGSTOP)
            deadline=time.monotonic()+3
            while time.monotonic()<deadline:
                pid,status=os.waitpid(job.pid,os.WUNTRACED|os.WNOHANG)
                if pid and os.WIFSTOPPED(status):paused=True;return
                if pid and os.WIFEXITED(status):raise RuntimeError('Rechenprozess unerwartet beendet.')
                time.sleep(.01)
            raise RuntimeError('Pause konnte nicht bestätigt werden.')
        def resume():
            nonlocal paused
            if paused:job.send_signal(signal.SIGCONT);paused=False
        try:
            python=find_python();folder.mkdir(parents=True,exist_ok=False);ready=folder/'ready.json'
            log=(folder/'prozess.log').open('w')
            job=subprocess.Popen([python,str(ROOT/'src/jobs/embedding_job.py'),'--arbeitsordner',str(folder),
                                  '--anzahl','100000','--block','64','--batch','16','--threads','6',
                                  '--offline','--ready-file',str(ready),'--start-paused'],stdout=log,stderr=log,
                                  env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            deadline=time.monotonic()+30
            while True:
                pid,status=os.waitpid(job.pid,os.WUNTRACED|os.WNOHANG)
                if pid and os.WIFSTOPPED(status):break
                if pid and (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                    raise RuntimeError('Modellstart fehlgeschlagen. Vorhandenen Modellcache und Prozessprotokoll prüfen.')
                if time.monotonic()>deadline or self.stop.wait(.05):raise RuntimeError('Modellstart abgebrochen oder Zeitlimit erreicht.')
            if not ready.exists():raise RuntimeError('Bereitschaftsmeldung fehlt.')
            emit('ready',pid=job.pid,model='BAAI/bge-small-en-v1.5')
            self.update(pid=job.pid,process='Pausiert',run_folder=str(folder.relative_to(ROOT)))
            for segment in self.case['segments']:
                pause();self.update(stage=segment['title'],segment_date=segment['date'],slot=segment['slot'])
                emit('segment',date=segment['date'])
                for row in segment['hours']:
                    if self.stop.is_set():break
                    duty=row['duty'];active=duty*self.seconds;rest=self.seconds-active
                    current={**row,'date':segment['date'],'slot':segment['slot']}
                    if active>1e-6:
                        resume();self.update(process='Rechnet',current=current,texts=progress())
                        emit('compute',model_time=row['zeit'],duty=duty,texts=progress())
                        if self.stop.wait(active):break
                    if rest>1e-6:
                        pause();before=progress();self.update(process='Pausiert',current=current,texts=before)
                        emit('pause',model_time=row['zeit'],reason='Modellierter Serverplatz wird nicht benötigt',texts=before)
                        if self.stop.wait(rest):break
                        after=progress()
                        if after!=before:raise RuntimeError('Während bestätigter Pause hat sich der Checkpoint verändert.')
                        emit('pause_verified',model_time=row['zeit'],texts=after,duration_seconds=rest)
                    self.update(current=current,texts=progress())
                if self.stop.is_set():break
            stopped=self.stop.is_set()
        except Exception as exc:
            self.update(error=str(exc));stopped=True
        finally:
            if job is not None:
                try:
                    # Resume first so an outstanding block can finish and save its checkpoint.
                    job.send_signal(signal.SIGCONT);job.send_signal(signal.SIGTERM)
                    code=job.wait(timeout=30)
                    if code not in (0,3):self.update(error='Rechenprozess mit Fehler beendet. Prozessprotokoll prüfen.')
                except ProcessLookupError:pass
                except subprocess.TimeoutExpired:
                    job.kill();job.wait();self.update(error='Rechenprozess musste nach Zeitlimit beendet werden.')
            if log is not None:log.close()
            final_texts=progress();self.update(active=False,completed=not stopped and not self.state.get('error'),
                   process='Checkpoint gespeichert',stage='Demo abgeschlossen' if not stopped else 'Demo beendet',texts=final_texts)
            if folder.exists():atomic(folder/'demo.json',self.snapshot())

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def setup(self):super().setup();self.connection.settimeout(10)
    def reply(self,status,data,kind='application/json; charset=utf-8'):
        body=json.dumps(data,ensure_ascii=False).encode() if isinstance(data,dict) else data
        self.send_response(status)
        for k,v in {'Content-Type':kind,'Content-Length':str(len(body)),'Cache-Control':'no-store',
            'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
            'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"}.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
    def do_GET(self):self.dispatch(False)
    def do_POST(self):self.dispatch(True)
    def dispatch(self,post):
        try:
            origin=f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host')!=origin[7:] or self.headers.get('Origin') not in (None,origin):return self.reply(403,{'error':'Nur lokaler Zugriff erlaubt.'})
            if post:
                if not secrets.compare_digest(self.headers.get('X-DigitalHeat-CSRF',''),self.server.csrf):return self.reply(403,{'error':'Seite neu laden.'})
                if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length',[]))!=1:return self.reply(400,{'error':'Ungültige Anfrage.'})
                size=int(self.headers['Content-Length'])
                if not 0<size<=1024:return self.reply(413,{'error':'Anfrage zu gross.'})
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.reply(415,{'error':'JSON erwartet.'})
                body=self.rfile.read(size)
                if len(body)!=size or not isinstance(json.loads(body),dict):return self.reply(400,{'error':'Ungültige Anfrage.'})
                if self.path=='/api/start':return self.reply(202 if self.server.demo.launch() else 409,{'accepted':True})
                if self.path=='/api/stop':self.server.demo.stop.set();return self.reply(200,{'stopping':True})
                return self.reply(404,{'error':'Nicht gefunden.'})
            if self.path=='/api/session':return self.reply(200,{'csrf':self.server.csrf})
            if self.path=='/api/case':return self.reply(200,self.server.demo.case)
            if self.path=='/api/live':return self.reply(200,self.server.demo.snapshot())
            files={'/':ROOT/'dashboard/gesamt/index.html','/app.js':ROOT/'dashboard/gesamt/app.js',
                   '/style.css':ROOT/'dashboard/gesamt/style.css','/wallpaper.svg':ROOT/'dashboard/gesamt/wallpaper.svg'}
            p=files.get(self.path)
            if p is None:return self.reply(404,{'error':'Nicht gefunden.'})
            return self.reply(200,p.read_bytes(),(mimetypes.guess_type(str(p))[0] or 'application/octet-stream')+'; charset=utf-8')
        except (ValueError,TypeError):self.reply(400,{'error':'Ungültige Anfrage.'})
        except (BrokenPipeError,ConnectionResetError,TimeoutError):pass
        except Exception:self.reply(500,{'error':'Interner Fehler.'})

def make_server(port=18200,seconds=1.2):
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.demo=Demo(build_case(),seconds);server.csrf=secrets.token_urlsafe(32);return server

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=18200);p.add_argument('--seconds',type=float,default=1.2);p.add_argument('--open',action='store_true');a=p.parse_args()
    if not .1<=a.seconds<=10:p.error('0,1 bis 10 Sekunden pro Modellstunde wählen.')
    server=make_server(a.port,a.seconds);url=f'http://127.0.0.1:{server.server_port}';print(f'Gesamtdemo: {url}',flush=True)
    if a.open:
        import webbrowser
        webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:
        server.demo.stop.set()
        if server.demo.thread:server.demo.thread.join(timeout=35)
        server.server_close()

if __name__=='__main__':main()
