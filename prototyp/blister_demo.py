"""Two-screen inspection demo with a TLS checkpoint handoff."""
import argparse
import base64
from collections import deque
import hmac
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import random
import secrets
import subprocess
import sys
import tempfile
import time
import threading
import uuid
from urllib.parse import urlsplit
import webbrowser

from digitalheat import APIError, Handler, init_credentials, tls_context

WIDTH, HEIGHT, TOTAL = 240, 144, 30
POCKETS = [(x, y) for y in (43, 101) for x in (42, 94, 146, 198)]
STATIC = Path(__file__).with_name("blister")


def inspect(index):
    """Generate a clearly synthetic camera frame and classify its actual pixels."""
    rng = random.Random(87291 + index)
    pixels = bytearray(rng.randrange(53, 70) for _ in range(WIDTH * HEIGHT))
    for cx, cy in POCKETS:
        present = rng.random() > 0.14
        for y in range(cy - 20, cy + 21):
            for x in range(cx - 20, cx + 21):
                radius2 = (x - cx) ** 2 + (y - cy) ** 2
                if radius2 <= 400:
                    level = 208 if present and radius2 <= 196 else 89 if radius2 < 320 else 136
                    pixels[y * WIDTH + x] = level + rng.randrange(-12, 13)
    boxes = []
    for x, y in POCKETS:
        patch = [pixels[row * WIDTH + col] for row in range(y - 8, y + 9)
                 for col in range(x - 8, x + 9)]
        boxes.append([x, y, sum(patch) / len(patch) < 145])
    return {"index": index, "pixels": base64.b64encode(pixels).decode(), "boxes": boxes}


class Batch:
    def __init__(self, site, interval):
        self.site, self.interval = site, interval
        self.lock = threading.Lock()
        self.job = None
        self.state = "bereit"
        self.frame = None
        self.received = None
        self.history = deque(maxlen=4)
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while not self.stop.wait(self.interval):
            with self.lock:
                if self.state != "rechnet":
                    continue
                self.frame = inspect(self.job["next"])
                self.job["next"] += 1
                self.job["rejects"] += int(any(box[2] for box in self.frame["boxes"]))
                self.history.append(self.frame["index"] + 1)
                if self.job["next"] == TOTAL:
                    self.state = "fertig"

    def snapshot(self):
        with self.lock:
            return {"site": self.site, "state": self.state, "job": dict(self.job) if self.job else None,
                    "frame": self.frame, "recent": list(self.history), "total": TOTAL}

    def start(self):
        with self.lock:
            if self.state != "bereit":
                raise APIError(409, "Der Demo-Batch wurde bereits gestartet.")
            self.job = {"id": uuid.uuid4().hex, "next": 0, "rejects": 0}
            self.state = "rechnet"

    def checkpoint(self):
        with self.lock:
            if self.state not in ("rechnet", "Übergabe läuft", "Übergabe offen"):
                raise APIError(409, "Nur ein laufender Batch kann wechseln.")
            if not 0 < self.job["next"] < TOTAL:
                raise APIError(409, "Der Wechsel braucht mindestens ein geprüftes Bild.")
            self.state = "Übergabe läuft"
            return dict(self.job)

    def receive(self, data):
        if (not isinstance(data, dict) or set(data) != {"id", "next", "rejects"}
                or not isinstance(data["id"], str) or len(data["id"]) != 32
                or type(data["next"]) is not int or type(data["rejects"]) is not int
                or not 0 <= data["rejects"] <= data["next"] < TOTAL or data["next"] == 0):
            raise APIError(400, "Ungültiger Checkpoint.")
        with self.lock:
            if data == self.received:
                return
            if self.state != "bereit":
                raise APIError(409, "Auf diesem Empfänger läuft bereits ein Batch.")
            self.received = dict(data)
            self.job = dict(data)
            self.state = "rechnet"


class TransferHandler(Handler):
    def route(self, method):
        if not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + self.server.token):
            raise APIError(401, "Ungültiger Zugangsschlüssel.")
        if method != "POST" or self.path != "/checkpoint":
            raise APIError(404, "Endpunkt nicht gefunden.")
        self.server.batch.receive(self.body())
        self.reply(200, {"accepted": True})


class ScreenHandler(Handler):
    def route(self, method):
        host = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != host or self.headers.get("Origin") not in (None, f"http://{host}"):
            raise APIError(403, "Diese Ansicht ist lokal.")
        if method == "GET":
            files = {"/": ("index.html", "text/html"), "/screen.js": ("screen.js", "text/javascript"),
                     "/screen.css": ("screen.css", "text/css")}
            if self.path in files:
                file, mime = files[self.path]
                return self.reply(200, (STATIC / file).read_bytes(), mime + "; charset=utf-8")
            if self.path == "/status":
                return self.reply(200, {**self.server.batch.snapshot(), "control": bool(self.server.target),
                                        "csrf": self.server.csrf})
        if method == "POST" and self.server.target and self.path in ("/start", "/move"):
            if not hmac.compare_digest(self.headers.get("X-DigitalHeat-CSRF", ""), self.server.csrf):
                raise APIError(403, "Sitzung ungültig.")
            self.body()
            if self.path == "/start":
                self.server.batch.start()
            else:
                self.move()
            return self.reply(200, {"ok": True})
        raise APIError(404, "Endpunkt nicht gefunden.")

    def move(self):
        batch = self.server.batch
        with self.server.transfer_lock:
            checkpoint = batch.checkpoint()
            target = self.server.target
            conn = http.client.HTTPSConnection(target.hostname, target.port or 443,
                                               context=self.server.tls, timeout=4)
            try:
                conn.request("POST", "/checkpoint", json.dumps(checkpoint),
                             {"Authorization": "Bearer " + self.server.token,
                              "Content-Type": "application/json"})
                response = conn.getresponse()
                if response.status != 200 or json.loads(response.read(1024)) != {"accepted": True}:
                    raise ValueError("Checkpoint nicht bestätigt")
            except (OSError, ValueError, http.client.HTTPException):
                with batch.lock:
                    batch.state = "Übergabe offen"
                raise APIError(502, "Übergabe unbestätigt. Den Wechsel erneut drücken.")
            finally:
                conn.close()
            with batch.lock:
                batch.state = "übergeben"


def local_demo(open_browser):
    """Start both screens with temporary localhost TLS credentials."""
    with tempfile.TemporaryDirectory() as folder:
        credentials = Path(folder) / "blister"
        init_credentials("127.0.0.1", credentials)
        processes = []
        try:
            for role, options in (
                ("worker", ["--bind", "127.0.0.1"]),
                ("sender", ["--target", "https://127.0.0.1:8445"]),
            ):
                command = [sys.executable, str(Path(__file__).resolve()), role,
                           "--credentials", str(credentials / role), *options]
                process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
                processes.append(process)
                ready = process.stdout.readline()
                if not ready:
                    raise SystemExit(f"{role} konnte nicht starten. Prüfe die Ports 8082, 8092 und 8445.")
                print(ready.strip(), flush=True)
            if open_browser:
                for port in (8082, 8092):
                    webbrowser.open_new_tab(f"http://127.0.0.1:{port}")
            while all(process.poll() is None for process in processes):
                time.sleep(0.25)
        except KeyboardInterrupt:
            pass
        finally:
            for process in processes:
                if process.poll() is None:
                    process.terminate()
            for process in processes:
                process.wait()
                process.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("sender", "worker", "demo"))
    parser.add_argument("--credentials", type=Path)
    parser.add_argument("--port", type=int, default=8445)
    parser.add_argument("--screen-port", type=int)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--target")
    parser.add_argument("--interval", type=float, default=1.6)
    parser.add_argument("--open", action="store_true", help="Lokale Demo in zwei Browser-Tabs öffnen")
    args = parser.parse_args()
    if args.role == "demo":
        return local_demo(args.open)
    if args.credentials is None:
        parser.error("--credentials ist für sender und worker erforderlich.")
    if args.open:
        parser.error("--open ist für demo vorgesehen.")
    target = urlsplit(args.target or "")
    if args.role == "sender" and (target.scheme != "https" or not target.hostname
                                  or target.path not in ("", "/") or target.username
                                  or target.password or target.query or target.fragment):
        parser.error("Sender benötigt --target https://EMPFÄNGER:8445")
    if not 0.05 <= args.interval <= 60:
        parser.error("--interval muss zwischen 0.05 und 60 Sekunden liegen.")
    cert = str(args.credentials / "worker-cert.pem")
    token = (args.credentials / "token.txt").read_text().strip()
    if len(token) < 40:
        parser.error("Der Zugangsschlüssel ist ungültig.")
    sender = args.role == "sender"
    screen_port = args.screen_port or (8082 if sender else 8092)
    tls = tls_context(cert) if sender else tls_context(cert, str(args.credentials / "worker-key.pem"))
    batch = Batch("Haus · Laptop A" if sender else "Sportbad · Laptop B", args.interval)
    with ThreadingHTTPServer(("127.0.0.1", screen_port), ScreenHandler) as screen:
        screen.batch, screen.token, screen.tls = batch, token, tls
        screen.csrf = secrets.token_urlsafe(32)
        screen.target = target if sender else None
        screen.transfer_lock = threading.Lock()
        transfer = None
        if not sender:
            transfer = ThreadingHTTPServer((args.bind, args.port), TransferHandler)
            transfer.batch, transfer.token = batch, token
            transfer.socket = tls.wrap_socket(transfer.socket, server_side=True)
            threading.Thread(target=transfer.serve_forever, daemon=True).start()
        print(f"{batch.site}: http://127.0.0.1:{screen.server_port}", flush=True)
        try:
            screen.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            batch.stop.set()
            batch.thread.join()
            if transfer:
                transfer.shutdown()
                transfer.server_close()


if __name__ == "__main__":
    main()
