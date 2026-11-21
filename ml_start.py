#!/usr/bin/env python3
"""Local operator UI and CLI for the ML-assisted energy experiment."""
import argparse
from dataclasses import fields
import json
import mimetypes
from pathlib import Path
import secrets
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from src.ml_system.config import Config
from src.ml_system.experiment import compare,save,ROOT

class State:
    def __init__(self):
        self.lock=threading.Lock();self.running=False;self.progress='Bereit';self.error=None;self.report=None;self.version=''
    def launch(self,config,days,start):
        with self.lock:
            if self.running:return False
            self.running=True;self.error=None;self.progress='Berechnung vorbereiten'
        def work():
            try:
                result=compare(config,days,start,self.update)
                report=save(result)
                with self.lock:self.report=report;self.version=str(uuid.uuid4())
            except Exception as e:
                # Numerical failures are visible; no credentials or uploaded data involved.
                with self.lock:self.error='Berechnung fehlgeschlagen: '+str(e)
            finally:
                with self.lock:self.running=False
        threading.Thread(target=work,daemon=True).start();return True
    def update(self,text):
        with self.lock:self.progress=text

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def setup(self):super().setup();self.connection.settimeout(10)
    def reply(self,code,data,kind='application/json; charset=utf-8'):
        body=json.dumps(data,ensure_ascii=False,allow_nan=False).encode() if isinstance(data,(dict,list)) else data
        self.send_response(code)
        for k,v in {'Content-Type':kind,'Content-Length':str(len(body)),'Cache-Control':'no-store',
                    'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
                    'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"}.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
    def do_GET(self):self.dispatch(False)
    def do_POST(self):self.dispatch(True)
    def dispatch(self,post):
        try:
            origin=f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host')!=origin[7:] or self.headers.get('Origin') not in (None,origin):
                return self.reply(403,{'error':'Nur lokaler Zugriff über 127.0.0.1 erlaubt.'})
            state=self.server.state
            if post:
                if self.path!='/api/run':return self.reply(404,{'error':'Nicht gefunden.'})
                if not secrets.compare_digest(self.headers.get('X-DigitalHeat-CSRF',''),self.server.csrf):
                    return self.reply(403,{'error':'Sitzung ungültig. Seite neu laden.'})
                if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length',[]))!=1:
                    return self.reply(400,{'error':'Ungültige Anfrage.'})
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.reply(415,{'error':'JSON erwartet.'})
                size=int(self.headers['Content-Length'])
                if not 0<size<=8000:return self.reply(413,{'error':'Anfrage zu gross.'})
                raw=self.rfile.read(size)
                if len(raw)!=size:return self.reply(400,{'error':'Unvollständige Anfrage.'})
                data=json.loads(raw)
                if not isinstance(data,dict) or not isinstance(data.get('config',{}),dict):raise ValueError('Ungültige Einstellungen.')
                config=Config(**data.get('config',{}));days=data.get('days',30);start=data.get('start','2025-07-01')
                # Validate date bounds before starting a costly background run.
                from datetime import datetime,timedelta
                if type(days) is not int or not 1<=days<=184:raise ValueError('1 bis 184 Tage wählen.')
                begin=datetime.strptime(start,'%Y-%m-%d')
                if begin<datetime(2025,7,1) or begin+timedelta(days=days)>datetime(2026,1,1):raise ValueError('Zeitraum vollständig in Juli–Dezember 2025 wählen.')
                if not state.launch(config,days,start):return self.reply(409,{'error':'Ein Vergleich wird bereits berechnet.'})
                return self.reply(202,{'started':True})
            if self.path=='/api/session':return self.reply(200,{'csrf':self.server.csrf})
            if self.path=='/api/status':
                with state.lock:return self.reply(200,{'running':state.running,'progress':state.progress,'error':state.error,'version':state.version})
            if self.path=='/api/report':
                with state.lock:
                    if state.report is None:return self.reply(404,{'error':'Noch kein Ergebnis.'})
                    return self.reply(200,state.report)
            files={'/':ROOT/'dashboard/ml/index.html','/app.js':ROOT/'dashboard/ml/app.js',
                   '/style.css':ROOT/'dashboard/ml/style.css','/wallpaper.svg':ROOT/'dashboard/ml/wallpaper.svg',
                   '/daten/ergebnisse/ml/vergleich.json':ROOT/'daten/ergebnisse/ml/vergleich.json',
                   '/daten/ergebnisse/ml/tage.csv':ROOT/'daten/ergebnisse/ml/tage.csv',
                   '/daten/ergebnisse/ml/stunden.csv':ROOT/'daten/ergebnisse/ml/stunden.csv',
                   '/docs/ML_SYSTEM.md':ROOT/'docs/ML_SYSTEM.md'}
            path=files.get(self.path)
            if path is None:return self.reply(404,{'error':'Nicht gefunden.'})
            if not path.exists():
                if self.path=='/':return self.reply(200,(ROOT/'dashboard/ml/template.html').read_bytes(),'text/html; charset=utf-8')
                return self.reply(404,{'error':'Noch nicht berechnet.'})
            kind=mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
            return self.reply(200,path.read_bytes(),kind+'; charset=utf-8')
        except (ValueError,TypeError,KeyError,OverflowError):self.reply(400,{'error':'Ungültige Einstellungen. Zahlen und Zeitraum prüfen.'})
        except (BrokenPipeError,ConnectionResetError,TimeoutError):pass
        except Exception:self.reply(500,{'error':'Interner Fehler.'})

def make_server(port=18100):
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.state=State();server.csrf=secrets.token_urlsafe(32)
    return server

def main():
    p=argparse.ArgumentParser(description='DigitalHeat: echter ML-Vergleich mit Energie- und Kostenbilanz')
    p.add_argument('--port',type=int,default=18100);p.add_argument('--open',action='store_true')
    p.add_argument('--days',type=int,default=184);p.add_argument('--start',default='2025-07-01')
    p.add_argument('--servers',type=int,default=8);p.add_argument('--compute-only',action='store_true')
    args=p.parse_args();config=Config(servers=args.servers)
    if args.compute_only:
        result=compare(config,args.days,args.start,print);save(result)
        print(json.dumps(result['comparison'],ensure_ascii=False,indent=2));return
    server=make_server(args.port)
    server.state.launch(config,args.days,args.start)
    url=f'http://127.0.0.1:{server.server_port}'
    print(f'ML-Energieplanung: {url}',flush=True)
    if args.open:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
