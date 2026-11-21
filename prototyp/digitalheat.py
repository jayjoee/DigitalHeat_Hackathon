#!/usr/bin/env python3
"""Two-device, encrypted job demo. Python standard library only; no remote code execution."""
from __future__ import annotations

import argparse
from collections import Counter
import concurrent.futures
import hashlib
import hmac
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import ssl
import subprocess
import tempfile
import threading
import time
from urllib.parse import urlsplit
import uuid
import webbrowser

ROOT = Path(__file__).resolve().parent
MAX_BODY = 300_000
MAX_TEXT = 200_000
MAX_JOBS = 30
RETENTION = 3600
TERMINAL = {"completed", "cancelled", "failed"}


class APIError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def private_write(path, data):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as f:
        f.write(data)


def init_credentials(host, directory):
    """Generate local demo TLS identity, with explicit trust material for the sender."""
    try:
        address = ipaddress.ip_address(host)
        entry = f"IP:{address}"
    except ValueError:
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?", host):
            raise ValueError("Bitte eine IP-Adresse oder einen einfachen Gerätenamen angeben.")
        entry = f"DNS:{host}"
    if not shutil.which("openssl"):
        raise ValueError("Für die Einrichtung wird OpenSSL benötigt. Siehe README.md.")
    directory = Path(directory)
    if directory.exists():
        raise ValueError("Der Zielordner existiert bereits. Bitte einen neuen Ordner wählen.")
    # Generate first, so unsuccessful certificate generation leaves no incomplete credentials.
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        config = temp / "openssl.cnf"
        sans = ",".join(dict.fromkeys([entry, "DNS:localhost", "IP:127.0.0.1"]))
        config.write_text(
            "[req]\ndistinguished_name=dn\nx509_extensions=ext\nprompt=no\n"
            "[dn]\nCN=DigitalHeat Demo\n[ext]\nbasicConstraints=critical,CA:TRUE\n"
            "keyUsage=critical,digitalSignature,keyEncipherment,keyCertSign\n"
            f"extendedKeyUsage=serverAuth\nsubjectAltName={sans}\n", encoding="utf-8")
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:3072", "-sha256",
                        "-nodes", "-days", "30", "-config", str(config),
                        "-keyout", str(temp / "worker-key.pem"),
                        "-out", str(temp / "worker-cert.pem")],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        token = secrets.token_urlsafe(48).encode()
        for role in ("worker", "sender"):
            dest = directory / role
            dest.mkdir(parents=True, mode=0o700)
            private_write(dest / "worker-cert.pem", (temp / "worker-cert.pem").read_bytes())
            private_write(dest / "token.txt", token)
        private_write(directory / "worker" / "worker-key.pem", (temp / "worker-key.pem").read_bytes())


class Store:
    def __init__(self, workers=1):
        self.lock = threading.RLock()
        self.jobs = {}
        self.stopping = threading.Event()
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        self.workers = workers
        self.heat_enabled = True
        self.cleaner = threading.Thread(target=self._clean_loop, daemon=True)
        self.cleaner.start()

    def _prune(self):
        cutoff = time.time() - RETENTION
        for jid in list(self.jobs):
            job = self.jobs[jid]
            if job["state"] in TERMINAL and job["updated_at"] < cutoff:
                del self.jobs[jid]

    def _clean_loop(self):
        while not self.stopping.wait(30):
            with self.lock:
                self._prune()

    def snapshot(self, job):
        return {k: v for k, v in job.items() if not k.startswith("_")}

    def list(self):
        with self.lock:
            self._prune()
            return [self.snapshot(j) for j in reversed(list(self.jobs.values()))]

    def get(self, jid):
        with self.lock:
            if jid not in self.jobs:
                raise APIError(404, "Auftrag nicht gefunden oder bereits entfernt.")
            return self.snapshot(self.jobs[jid])

    def submit(self, data):
        if not isinstance(data, dict):
            raise APIError(400, "Ein JSON-Objekt wird erwartet.")
        task_type = data.get("task_type", "text_analysis")
        if task_type not in ("text_analysis", "virtual_screening", "microscopy", "literature"):
            raise APIError(400, "Unbekannte Auftragsvorlage.")
        count, target = data.get("sample_count", 1000), data.get("target", "Öffentliches Demo-Target")
        if task_type in ("virtual_screening", "microscopy"):
            if type(count) is not int or not 1 <= count <= 1_000_000:
                raise APIError(400, "Die Anzahl muss zwischen 1 und 1'000'000 liegen.")
            if not isinstance(target, str) or not 1 <= len(target.strip()) <= 80:
                raise APIError(400, "Die Bezeichnung muss 1 bis 80 Zeichen enthalten.")
        text, title, duration = data.get("text", f"{task_type}: {count} / {target}" if task_type in ("virtual_screening", "microscopy") else None), data.get("title", "Textanalyse"), data.get("duration", 10)
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
            raise APIError(400, "Bitte Text mit 1 bis 200'000 Zeichen angeben.")
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80:
            raise APIError(400, "Der Titel muss 1 bis 80 Zeichen enthalten.")
        if type(duration) is not int or not 2 <= duration <= 60:
            raise APIError(400, "Die Simulationsdauer muss zwischen 2 und 60 Sekunden liegen.")
        with self.lock:
            self._prune()
            if len(self.jobs) >= MAX_JOBS:
                raise APIError(429, "30 Aufträge gespeichert. Bitte abgeschlossene Aufträge entfernen.")
            jid = str(uuid.uuid4())
            now = time.time()
            job = dict(id=jid, title=title.strip(), state="queued", progress=0,
                       created_at=now, updated_at=now, duration=duration, active_seconds=0,
                       task_type=task_type, sample_count=count if task_type in ("virtual_screening", "microscopy") else None,
                       target=target if task_type in ("virtual_screening", "microscopy") else None,
                       characters=len(text), receiver=socket.gethostname(), result=None,
                       _text=text, _pause=False, _cancel=False)
            self.jobs[jid] = job
            self.pool.submit(self._run, jid)
            return self.snapshot(job)

    def control(self, jid, action):
        with self.lock:
            self.get(jid)
            job = self.jobs[jid]
            if action == "delete":
                if job["state"] not in TERMINAL:
                    raise APIError(409, "Laufenden Auftrag zuerst abbrechen.")
                del self.jobs[jid]
                return {"deleted": True}
            if job["state"] in TERMINAL:
                raise APIError(409, "Dieser Auftrag ist bereits beendet.")
            if action == "pause":
                job["_pause"] = True
                job["state"] = "paused"
            elif action == "resume":
                job["_pause"] = False
                job["state"] = ("running" if job.get("_started") else "queued") if self.heat_enabled else "paused"
            elif action == "cancel":
                job["_cancel"] = True
                job["_text"] = None
                job["state"] = "cancelled"
            else:
                raise APIError(404, "Unbekannte Aktion.")
            job["updated_at"] = time.time()
            return self.snapshot(job)

    def _run(self, jid):
        try:
            self._process(jid)
        except Exception:
            # Do not put payloads or exception details into logs or API responses.
            with self.lock:
                if jid in self.jobs:
                    self.jobs[jid].update(state="failed", _text=None, updated_at=time.time())
            print(f"Auftrag {jid[:8]}: Verarbeitung fehlgeschlagen.", flush=True)

    def _process(self, jid):
        active, digest, text = 0.0, b"digitalheat-demo", None
        print(f"Auftrag {jid[:8]} empfangen. Verarbeitung auf {socket.gethostname()}.", flush=True)
        last_log = -1
        try:
            while not self.stopping.is_set():
                with self.lock:
                    job = self.jobs.get(jid)
                    if not job or job["_cancel"]:
                        return
                    paused = job["_pause"] or not self.heat_enabled
                    if paused:
                        job["state"] = "paused"
                    if not paused:
                        job.update(state="running", _started=True)
                        duration = job["duration"]
                        if text is None:
                            text = job["_text"]
                            job["_text"] = None
                if paused:
                    self.stopping.wait(0.1)
                    continue
                # Real CPU work, deliberately independent of any medical or AI claim.
                start = time.perf_counter()
                digest = hashlib.pbkdf2_hmac("sha256", digest, b"DigitalHeat CPU demo", 20_000)
                active += time.perf_counter() - start
                with self.lock:
                    job = self.jobs.get(jid)
                    if not job or job["_cancel"]:
                        return
                    job.update(progress=min(99, int(active / duration * 100)),
                               active_seconds=round(active, 2), updated_at=time.time())
                    step = job["progress"] // 25
                    if step != last_log:
                        print(f"Auftrag {jid[:8]}: {job['progress']} %", flush=True)
                        last_log = step
                    if active < duration or job["_pause"] or not self.heat_enabled:
                        continue
                    # Bounded text analysis; no shell, uploaded program or evaluation.
                    words = re.findall(r"[^\W\d_]+", text.lower(), re.UNICODE)
                    result = {
                        "words": len(words), "unique_words": len(set(words)),
                        "characters": len(text),
                        "top_words": [{"word": word, "count": count}
                                      for word, count in Counter(words).most_common(12)],
                        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                        "description": "Textstatistik plus simulierte CPU-Rechenlast. Kein KI- oder Pharma-Modell.",
                    }
                    if job["task_type"] == "virtual_screening":
                        # Deterministic synthetic scores. No molecular model or affinity prediction.
                        seed = hashlib.sha256(text.encode()).digest()
                        result = {"description": "Synthetisches Screening: keine Docking-Berechnung, keine Bindungsaffinität.",
                                  "simulated": True, "sample_count": job["sample_count"],
                                  "ranking": [{"compound": f"DEMO-{i+1:04d}", "demo_score": round(1 - (seed[i] / 255) * .3 - i * .01, 3)} for i in range(min(5, job["sample_count"]))]}
                        result["ranking"].sort(key=lambda r: r["demo_score"], reverse=True)
                    elif job["task_type"] == "microscopy":
                        result = {"description": "Synthetisches Cell-Painting-Ergebnis. Keine Bilder analysiert, kein trainiertes Modell.",
                                  "simulated": True, "images": job["sample_count"],
                                  "demo_cells": job["sample_count"] * 42, "demo_quality_percent": 96.4}
                    elif job["task_type"] == "literature":
                        result["description"] = "Tatsächliche Textstatistik mit simulierter CPU-Last. Keine Embeddings, keine wissenschaftliche Bewertung."
                    job.update(state="completed", progress=100, result=result,
                               updated_at=time.time(), _text=None)
                    print(f"Auftrag {jid[:8]}: abgeschlossen; Ergebnis bereit.", flush=True)
                    return
        finally:
            # Discard references. Python does not guarantee cryptographic RAM zeroization.
            text = None

    def set_heat(self, enabled):
        if type(enabled) is not bool:
            raise APIError(400, "Wärmebedarf muss ein Wahrheitswert sein.")
        with self.lock:
            self.heat_enabled = enabled
            for job in self.jobs.values():
                if job["state"] not in TERMINAL:
                    job["state"] = "paused" if not enabled or job["_pause"] else ("running" if job.get("_started") else "queued")
            return self.host_status()

    def host_status(self):
        # Explicit projection: never disclose customer names, titles, payloads or results.
        with self.lock:
            self._prune()
            jobs = list(self.jobs.values())
            return {"heat_enabled": self.heat_enabled, "running": sum(j["state"] == "running" for j in jobs),
                    "waiting": sum(j["state"] in ("queued", "paused") for j in jobs),
                    "completed": sum(j["state"] == "completed" for j in jobs),
                    "processing": "CPU-Simulation", "connected": True}

    def close(self):
        self.stopping.set()
        with self.lock:
            for job in self.jobs.values():
                job["_cancel"] = True
                job["_text"] = None
        self.pool.shutdown(wait=True, cancel_futures=True)
        self.cleaner.join(timeout=2)
        with self.lock:
            self.jobs.clear()


class Handler(BaseHTTPRequestHandler):
    server_version = "DigitalHeatDemo"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *_):
        pass

    def reply(self, status, data, content_type="application/json; charset=utf-8"):
        body = json.dumps(data, ensure_ascii=False).encode() if isinstance(data, (dict, list)) else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        if self.headers.get("Transfer-Encoding"):
            raise APIError(400, "Transfer-Encoding wird nicht unterstützt.")
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            raise APIError(415, "Content-Type application/json ist erforderlich.")
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1:
            raise APIError(400, "Eine eindeutige Content-Length ist erforderlich.")
        try:
            size = int(lengths[0])
            if not 0 < size <= MAX_BODY:
                raise APIError(413, "Die Anfrage ist zu gross.")
            raw = self.rfile.read(size)
            if len(raw) != size:
                raise APIError(400, "Unvollständige Anfrage.")
            return json.loads(raw)
        except (ValueError, UnicodeError):
            raise APIError(400, "Ungültige JSON-Daten.")

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def dispatch(self, method):
        try:
            self.route(method)
        except APIError as e:
            self.reply(e.status, {"error": e.message})
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass
        except Exception:
            self.reply(500, {"error": "Interner Fehler. Keine Auftragsdaten wurden protokolliert."})


class WorkerHandler(Handler):
    def route(self, method):
        if not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + self.server.token):
            raise APIError(401, "Ungültiger Zugangsschlüssel.")
        path = self.path
        store = self.server.store
        if method == "GET" and path == "/v1/status":
            jobs = store.list()
            return self.reply(200, dict(connected=True, receiver=socket.gethostname(),
                                      workers=store.workers, jobs=jobs, tls="TLS 1.3",
                                      processing="CPU-Simulation", retention_seconds=RETENTION))
        if path == "/v1/jobs" and method == "POST":
            return self.reply(202, store.submit(self.body()))
        match = re.fullmatch(r"/v1/jobs/([0-9a-f-]{36})(?:/(pause|resume|cancel|delete))?", path)
        if match:
            jid, action = match.groups()
            if method == "GET" and not action:
                return self.reply(200, store.get(jid))
            if method == "POST" and action:
                body = self.body()
                if not isinstance(body, dict):
                    raise APIError(400, "Ein JSON-Objekt wird erwartet.")
                return self.reply(200, store.control(jid, action))
        raise APIError(404, "Endpunkt nicht gefunden.")


def tls_context(cert=None, key=None):
    if key:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cafile=cert)
    # Fail closed: no insecure or unverified HTTP fallback.
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    return context


def make_worker(host, port, credentials, workers=1):
    credentials = Path(credentials)
    server = ThreadingHTTPServer((host, port), WorkerHandler)
    server.token = (credentials / "token.txt").read_text().strip()
    if len(server.token) < 40:
        server.server_close()
        raise ValueError("Der Zugangsschlüssel ist ungültig.")
    try:
        context = tls_context(str(credentials / "worker-cert.pem"), str(credentials / "worker-key.pem"))
        server.socket = context.wrap_socket(server.socket, server_side=True)
    except Exception:
        server.server_close()
        raise
    server.store = Store(workers)
    return server


class SenderHandler(Handler):
    def route(self, method):
        # Reject foreign origins and DNS-rebinding hostnames, including for read operations.
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != origin.removeprefix("http://"):
            raise APIError(403, "Diese Oberfläche ist nur lokal erreichbar.")
        if self.headers.get("Origin") not in (None, origin):
            raise APIError(403, "Anfrage von einer fremden Seite abgelehnt.")
        path = self.path
        if method == "GET" and path in ("/", "/pharma.js", "/platform.css", "/wallpaper.svg"):
            file = "pharma.html" if path == "/" else path[1:]
            kind = "text/html" if file.endswith("html") else "text/javascript" if file.endswith("js") else "text/css" if file.endswith("css") else "image/svg+xml"
            return self.reply(200, (ROOT / "static" / file).read_bytes(), kind + "; charset=utf-8")
        if method == "GET" and path == "/api/session":
            return self.reply(200, {"csrf": self.server.csrf, "worker_url": self.server.worker_url})
        if path == "/api/status" and method == "GET":
            return self.proxy("GET", "/v1/status")
        if method == "POST":
            if not hmac.compare_digest(self.headers.get("X-DigitalHeat-CSRF", ""), self.server.csrf):
                raise APIError(403, "Sitzung ungültig. Bitte Seite neu laden.")
            data = self.body()
            if path == "/api/jobs":
                return self.proxy("POST", "/v1/jobs", data)
            if re.fullmatch(r"/api/jobs/[0-9a-f-]{36}/(pause|resume|cancel|delete)", path):
                return self.proxy("POST", path.replace("/api/", "/v1/", 1), data)
        raise APIError(404, "Endpunkt nicht gefunden.")

    def proxy(self, method, path, payload=None):
        target = self.server.worker_target
        connection = http.client.HTTPSConnection(target.hostname, target.port or 443,
                                                 context=self.server.client_tls, timeout=5)
        try:
            body = json.dumps(payload).encode() if payload is not None else None
            headers = {"Authorization": "Bearer " + self.server.token, "Content-Type": "application/json"}
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read(2_000_000)
            return self.reply(response.status, json.loads(raw))
        except ssl.SSLCertVerificationError:
            raise APIError(502, "Zertifikat oder Gerätename passt nicht. Bitte Sender-Zertifikat und Empfängeradresse prüfen.")
        except ssl.SSLError:
            raise APIError(502, "Verschlüsselte Verbindung fehlgeschlagen. Beide Geräte benötigen TLS 1.3.")
        except (OSError, http.client.HTTPException, ValueError):
            raise APIError(502, "Empfänger nicht erreichbar. Adresse, Netzwerk und gestarteten Empfänger prüfen.")
        finally:
            connection.close()


class HostHandler(Handler):
    def route(self, method):
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != origin.removeprefix("http://") or self.headers.get("Origin") not in (None, origin):
            raise APIError(403, "Diese Oberfläche ist nur lokal erreichbar.")
        if method == "GET" and self.path in ("/", "/host.js", "/platform.css", "/wallpaper.svg"):
            file = "host.html" if self.path == "/" else self.path[1:]
            kind = "text/html" if file.endswith("html") else "text/javascript" if file.endswith("js") else "text/css" if file.endswith("css") else "image/svg+xml"
            return self.reply(200, (ROOT / "static" / file).read_bytes(), kind + "; charset=utf-8")
        if method == "GET" and self.path == "/api/host/session":
            return self.reply(200, {"csrf": self.server.csrf})
        if method == "GET" and self.path == "/api/host/status":
            return self.reply(200, self.server.host_store.host_status())
        if method == "POST" and self.path == "/api/host/heat":
            if not hmac.compare_digest(self.headers.get("X-DigitalHeat-CSRF", ""), self.server.csrf):
                raise APIError(403, "Sitzung ungültig. Bitte Seite neu laden.")
            data = self.body()
            if not isinstance(data, dict):
                raise APIError(400, "Ein JSON-Objekt wird erwartet.")
            return self.reply(200, self.server.host_store.set_heat(data.get("enabled")))
        raise APIError(404, "Endpunkt nicht gefunden.")


def make_host(port, store):
    server = ThreadingHTTPServer(("127.0.0.1", port), HostHandler)
    server.host_store, server.csrf = store, secrets.token_urlsafe(32)
    return server


def make_sender(port, worker_url, credentials):
    target = urlsplit(worker_url)
    if target.scheme != "https" or not target.hostname or target.path not in ("", "/") or target.query or target.fragment or target.username or target.password:
        raise ValueError("Bitte eine HTTPS-Adresse ohne Pfad oder Zugangsdaten angeben.")
    credentials = Path(credentials)
    context = tls_context(str(credentials / "worker-cert.pem"))
    token = (credentials / "token.txt").read_text().strip()
    if len(token) < 40:
        raise ValueError("Der Zugangsschlüssel ist ungültig.")
    server = ThreadingHTTPServer(("127.0.0.1", port), SenderHandler)
    server.worker_url, server.worker_target = worker_url, target
    server.client_tls, server.token, server.csrf = context, token, secrets.token_urlsafe(32)
    return server


def serve(server):
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nDemo wird beendet.")
    finally:
        server.server_close()
        if hasattr(server, "store"):
            server.store.close()


def main():
    parser = argparse.ArgumentParser(description="DigitalHeat: Aufträge zwischen zwei Geräten senden")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Zertifikat und Zugang für zwei Geräte erstellen")
    init.add_argument("--host", required=True, help="IP-Adresse oder Name des Empfängergeräts")
    init.add_argument("--out", default="credentials")
    worker = commands.add_parser("worker", help="Verarbeitung auf dem Empfänger starten")
    worker.add_argument("--bind", default="0.0.0.0")
    worker.add_argument("--port", type=int, default=8443)
    worker.add_argument("--credentials", default="credentials/worker")
    worker.add_argument("--host-port", type=int, default=8090)
    worker.add_argument("--workers", type=int, choices=range(1, 5), default=1)
    sender = commands.add_parser("sender", help="Lokale Kundenseite auf dem Sender starten")
    sender.add_argument("--worker", required=True, help="https://EMPFÄNGER-IP:8443")
    sender.add_argument("--port", type=int, default=8080)
    sender.add_argument("--credentials", default="credentials/sender")
    sender.add_argument("--open", action="store_true", help="Kundenseite im Browser öffnen")
    demo = commands.add_parser("demo", help="Animierte Blisterprüfung lokal starten")
    demo.add_argument("--pharma", action="store_true", help="Klassischen Pharma-Prototyp öffnen")
    demo.add_argument("--host-port", type=int, default=8090)
    demo.add_argument("--worker-port", type=int, default=8443)
    demo.add_argument("--port", type=int, default=8080)
    demo.add_argument("--credentials", default="demo-credentials")
    demo.add_argument("--open", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "init":
            init_credentials(args.host, args.out)
            print(f"Einrichtung bereit: {args.out}/worker und {args.out}/sender")
            print("Nur den Sender-Ordner sicher zum Sendergerät übertragen. Den privaten Worker-Schlüssel nicht teilen.")
        elif args.command == "worker":
            server = make_worker(args.bind, args.port, args.credentials, args.workers)
            print(f"Empfänger bereit auf Port {server.server_port}. TLS 1.3, {args.workers} Rechenplatz/Rechenplätze.", flush=True)
            host = make_host(args.host_port, server.store)
            host_thread = threading.Thread(target=host.serve_forever, daemon=True)
            host_thread.start()
            print(f"Serverhalter: http://127.0.0.1:{host.server_port}", flush=True)
            try:
                serve(server)
            finally:
                host.shutdown()
                host.server_close()
                host_thread.join(timeout=2)
        elif args.command == "sender":
            server = make_sender(args.port, args.worker, args.credentials)
            url = f"http://127.0.0.1:{server.server_port}"
            print(f"Kundenseite: {url}\nEmpfänger: {args.worker}", flush=True)
            if args.open:
                webbrowser.open(url)
            serve(server)
        elif not args.pharma:
            from blister_demo import local_demo
            local_demo(args.open, args.port, args.host_port, args.worker_port)
        else:
            directory = Path(args.credentials)
            if not directory.exists():
                init_credentials("127.0.0.1", directory)
            worker = make_worker("127.0.0.1", args.worker_port, directory / "worker")
            thread = threading.Thread(target=worker.serve_forever, daemon=True)
            thread.start()
            host = None
            try:
                host = make_host(args.host_port, worker.store)
                host_thread = threading.Thread(target=host.serve_forever, daemon=True)
                host_thread.start()
                sender = make_sender(args.port, f"https://127.0.0.1:{worker.server_port}", directory / "sender")
                url = f"http://127.0.0.1:{sender.server_port}"
                print(f"Pharma: {url}\nServerhalter: http://127.0.0.1:{host.server_port}\nZwei getrennte Oberflächen auf diesem Gerät.", flush=True)
                if args.open:
                    webbrowser.open(url)
                serve(sender)
            finally:
                if host:
                    host.shutdown()
                    host.server_close()
                    host_thread.join(timeout=2)
                worker.shutdown()
                worker.server_close()
                worker.store.close()
                thread.join(timeout=2)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Start nicht möglich: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
