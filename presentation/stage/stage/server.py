#!/usr/bin/env python3
"""Local server for the stage presentation. Python 3.9+, standard library only.

It listens on 127.0.0.1 only, serves the presentation and starts or stops the real demo job.
"""
import argparse
import fcntl
import http.server
import json
import mimetypes
import os
import re
import secrets
import shutil
import signal
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
STATUS = DEMO / "dashboard" / "live.json"
WORK = DEMO / "messungen" / "stage-run"
TOKEN = secrets.token_hex(12)


class Job:
    def __init__(self):
        self.process = None
        self.lock = threading.Lock()

    def _kill_group(self, pid):
        try:
            group = os.getpgid(pid)
            if group != os.getpgid(0):
                os.killpg(group, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    def _leftovers(self):
        # Docking jobs of this folder only. They run in a process group of their own, together with Vina.
        pattern = re.escape(str(DEMO / "src" / "jobs" / "docking_job.py"))
        found = subprocess.run(["/usr/bin/pgrep", "-f", pattern], stdout=subprocess.PIPE, universal_newlines=True).stdout
        return [int(x) for x in found.split()]

    def _stop(self):
        # Leaving the demo ends it at once. A run that ends by itself saves its checkpoint in live.py.
        p, self.process = self.process, None
        if p and p.poll() is None:
            self._kill_group(p.pid)
            p.wait()
            time.sleep(0.1)
        for pid in self._leftovers():
            self._kill_group(pid)
        STATUS.unlink(missing_ok=True)

    def stop(self):
        with self.lock:
            self._stop()

    def start(self):
        with self.lock:
            self._stop()
            shutil.rmtree(WORK, ignore_errors=True)
            WORK.parent.mkdir(exist_ok=True)
            with open(WORK.parent / "stage.log", "w") as log:
                self.process = subprocess.Popen(
                    [sys.executable, "-B", "src/scheduler/live.py", "--tag", "2025-03-07", "--server", "8",
                     "--sekunden", "1.7", "--job", "docking", "--arbeitsordner", str(WORK)],
                    cwd=str(DEMO), stdout=log, stderr=log, start_new_session=True)

    def state(self):
        p = self.process
        try:
            live = json.loads(STATUS.read_text())
        except (OSError, ValueError):
            live = None
        return {"exit": p.poll() if p else None, "live": live}


JOB = Job()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def local(self):
        return self.headers.get("Host") == "127.0.0.1:%d" % self.server.server_address[1]

    def send(self, code, body=b"", kind="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if not self.local() or self.headers.get("X-Stage") != TOKEN:
            return self.send(403)
        if self.path == "/api/start":
            JOB.start()
        elif self.path == "/api/stop":
            JOB.stop()
        else:
            return self.send(404)
        self.send(204)

    def do_GET(self):
        if not self.local():
            return self.send(403)
        path = unquote(urlsplit(self.path).path)
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/stage/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path == "/api/state":
            return self.send(200, json.dumps(JOB.state()).encode(), "application/json")
        if path == "/api/token.js":
            # Script tags from other sites must not be able to read the token.
            if self.headers.get("Sec-Fetch-Site", "same-origin") != "same-origin":
                return self.send(403)
            return self.send(200, ("window.STAGE_TOKEN = '%s';" % TOKEN).encode(), "application/javascript")
        top, _, rest = path.lstrip("/").partition("/")
        bases = {"stage": ROOT / "stage", "media": ROOT / "media", "dashboard": DEMO / "dashboard"}
        if top not in bases:
            return self.send(404)
        base = bases[top].resolve()
        f = (base / rest).resolve()
        if f != base and base not in f.parents:
            return self.send(403)
        if f.is_dir():
            f = f / "index.html"
        if not f.is_file():
            return self.send(404)
        if f == base / "3d" / "index.html" and top == "dashboard":
            html = f.read_text()
            here = ROOT / "stage"
            html = html.replace("animiere();\n</script>", (here / "hook.js").read_text(), 1)
            html = html.replace("</head>", "<style>%s</style></head>" % (here / "dashboard.css").read_text(), 1)
            return self.send(200, html.encode(), "text/html; charset=utf-8")
        self.send_file(f)

    def send_file(self, f):
        size = f.stat().st_size
        first, last, code = 0, size - 1, 200
        m = re.fullmatch(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        if m:
            first = int(m.group(1))
            last = min(int(m.group(2) or last), size - 1)
            if first > last:
                return self.send(416)
            code = 206
        kind = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
        self.send_response(code)
        self.send_header("Content-Type", kind + ("; charset=utf-8" if kind.startswith("text/") else ""))
        self.send_header("Content-Length", str(last - first + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        if code == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (first, last, size))
        self.end_headers()
        try:
            with f.open("rb") as src:
                src.seek(first)
                left = last - first + 1
                while left:
                    data = src.read(min(262144, left))
                    if not data:
                        break
                    self.wfile.write(data)
                    left -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

    def handle_error(self, request, address):
        if not isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError)):
            super().handle_error(request, address)


def show(url):
    if subprocess.call(["open", "-a", "Google Chrome", url], stderr=subprocess.DEVNULL):
        subprocess.call(["open", url])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    marker = ROOT / "stage" / ".running"
    lock = open(marker, "a+")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock.seek(0)
        url = lock.read().strip()
        print("The presentation is already running:", url, flush=True)
        if not a.no_open and url.startswith("http://127.0.0.1:"):
            show(url)
        return
    (DEMO / "messungen").mkdir(exist_ok=True)
    JOB.stop()  # removes what an interrupted earlier run left behind
    server = Server(("127.0.0.1", 0), Handler)
    url = "http://127.0.0.1:%d/stage/" % server.server_address[1]
    lock.seek(0)
    lock.truncate()
    lock.write(url)
    lock.flush()

    def finish(*_):
        raise KeyboardInterrupt

    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(sig, finish)
    print("DigitalHeat stage:", url, "\nKeep this window open. Close it after the pitch.", flush=True)
    if not a.no_open:
        show(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
            signal.signal(sig, signal.SIG_IGN)
        JOB.stop()
        server.server_close()
        lock.seek(0)
        lock.truncate()


if __name__ == "__main__":
    main()
