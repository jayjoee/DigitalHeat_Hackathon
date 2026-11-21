"""Two-screen inspection demo with a TLS checkpoint handoff."""
import argparse
import base64
from collections import deque
from functools import partial
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.scheduler.annahmen import wert  # noqa: E402

WIDTH, HEIGHT, TOTAL = 240, 144, 30
POCKETS = [(x, y) for y in (43, 101) for x in (42, 94, 146, 198)]
# Known defects in the synthetic batch, indexed by pack and pocket from zero.
MISSING_POCKETS = {2: (5,), 6: (2,), 10: (0, 7), 15: (4,), 21: (1,), 27: (6,)}
STATIC = Path(__file__).with_name("blister")
STEPS_PER_HOUR = 2
TRACE = ROOT / "daten/ergebnisse/live_flotte_2025-05-25.json"
FORWARD_C = 55  # Illustrative water supply temperature, absent from the router model.


def heat_profile():
    """Play the recorded routing decision around the first house-to-pool migration."""
    hours = json.loads(TRACE.read_text())["stunden"]
    switch = next(i for i, hour in enumerate(hours) if hour["standort_typ"] == "bad")
    return hours[max(0, switch - 4):]


def camera_frame(index):
    """Render a synthetic foil pack under slightly varying light and alignment."""
    rng = random.Random(87291 + index)
    offset_x, offset_y = rng.randint(-2, 2), rng.randint(-2, 2)
    exposure = rng.randint(-13, 13)
    missing = MISSING_POCKETS.get(index, ())
    pixels = bytearray(rng.randrange(24, 33) for _ in range(WIDTH * HEIGHT))
    for y in range(15, 132):
        for x in range(12, 228):
            corner_x = max(21 - x, x - 218, 0)
            corner_y = max(24 - y, y - 122, 0)
            radius2 = corner_x ** 2 + corner_y ** 2
            if radius2 <= 81:
                texture = (x % 3 == 0) * 7 + (y % 4 == 0) * 5
                bevel = 19 if radius2 > 45 and y < 75 else 0
                pixels[y * WIDTH + x] = 124 + exposure + (x - y) // 9 + texture + bevel + rng.randint(-5, 5)
    for pocket, (cx, cy) in enumerate(POCKETS):
        for y in range(cy - 21, cy + 22):
            for x in range(cx - 19, cx + 20):
                dx, dy = x - cx - offset_x, y - cy - offset_y
                well = (dx / 17) ** 2 + (dy / 19) ** 2
                if well > 1:
                    continue
                capsule = dx ** 2 + max(abs(dy) - 4, 0) ** 2
                level = 176 - dy * 2 if well > .75 else 78 + dy
                if pocket not in missing and capsule <= 121:
                    level = 213 - (dx + dy) // 2 - (26 if capsule > 92 else 0)
                pixels[y * WIDTH + x] = level + exposure + rng.randint(-5, 5)
    return pixels


def detect_missing(pixels):
    """Compare each pocket's center with its surrounding foil background."""
    boxes = []
    for x, y in POCKETS:
        patch = [pixels[row * WIDTH + col] for row in range(y - 4, y + 5)
                 for col in range(x - 4, x + 5)]
        foil = [pixels[row * WIDTH + col] for row in range(y - 4, y + 5)
                for col in (x - 21, x + 21)]
        boxes.append([x, y, sum(patch) / len(patch) < sum(foil) / len(foil) + 20])
    return boxes


def inspect(index):
    pixels = camera_frame(index)
    boxes = detect_missing(pixels)
    return {"index": index, "pixels": base64.b64encode(pixels).decode(), "boxes": boxes}


class Batch:
    def __init__(self, site, interval, handoff=None):
        self.site, self.interval = site, interval
        self.lock = threading.Lock()
        self.job = None
        self.state = "bereit"
        self.frame = None
        self.received = None
        self.history = deque(maxlen=4)
        self.handoff = handoff
        self.heat_hours = heat_profile()
        self.heat_step = -1
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while not self.stop.wait(self.interval):
            with self.lock:
                if self.state != "rechnet":
                    continue
                self.heat_step += 1
                hour = self.heat_hour(self.heat_step)
                move = self.handoff is not None and hour["standort_typ"] == "bad"
                if move:
                    self.state = "Übergabe läuft"
                elif hour["anteil_echter_server"] > 0:
                    self.frame = inspect(self.job["next"])
                    self.job["next"] += 1
                    self.job["rejects"] += int(any(box[2] for box in self.frame["boxes"]))
                    self.history.append(self.frame["index"] + 1)
                    if self.job["next"] == TOTAL:
                        self.state = "fertig"
            if move:
                try:
                    self.send_checkpoint()
                except APIError:
                    pass  # The sender stays paused and offers a retry.

    def heat_hour(self, step):
        return self.heat_hours[min(len(self.heat_hours) - 1, step // STEPS_PER_HOUR)]

    def heat_snapshot(self):
        initial_step = self.received["heat_step"] if self.received else 0
        hour = self.heat_hour(max(initial_step, self.heat_step))
        local_site = "haus" if self.handoff else "bad"
        eligible = hour["standort_typ"] == local_site
        working = self.state == "rechnet" and eligible
        heat_kw = (wert("server_kw") * wert("waermerueckgewinnung") * hour["anteil_echter_server"]
                   if working else 0)
        return {"time": hour["zeit"], "outside_c": hour["temp_c"],
                "tank_kwh": hour["haus_speicher_kwh"], "tank_max_kwh": wert("speicher_kwh"),
                "heat_kw": round(heat_kw, 3), "forward_c": FORWARD_C if heat_kw else None,
                "scheduled_pause": working and heat_kw == 0}

    def snapshot(self):
        with self.lock:
            return {"site": self.site, "state": self.state, "job": dict(self.job) if self.job else None,
                    "frame": self.frame, "recent": list(self.history), "total": TOTAL,
                    "resumed_after": self.received["next"] if self.received else 0,
                    "heat": self.heat_snapshot()}

    def start(self):
        with self.lock:
            if self.state != "bereit":
                raise APIError(409, "Der Demo-Batch wurde bereits gestartet.")
            self.job = {"id": uuid.uuid4().hex, "next": 0, "rejects": 0}
            self.state = "rechnet"

    def retry_transfer(self):
        with self.lock:
            if self.state != "Übergabe offen":
                raise APIError(409, "Es gibt keine offene Übergabe.")
            self.state = "Übergabe läuft"
        self.send_checkpoint()

    def send_checkpoint(self):
        with self.lock:
            checkpoint = {**self.job, "heat_step": self.heat_step}
        try:
            self.handoff(checkpoint)
        except (OSError, ValueError, http.client.HTTPException) as error:
            with self.lock:
                self.state = "Übergabe offen"
            raise APIError(502, "Übergabe unbestätigt. Das Haus bleibt pausiert.") from error
        with self.lock:
            self.state = "übergeben"

    def receive(self, data):
        if (not isinstance(data, dict) or set(data) != {"id", "next", "rejects", "heat_step"}
                or not isinstance(data["id"], str) or len(data["id"]) != 32
                or type(data["next"]) is not int or type(data["rejects"]) is not int
                or not 0 <= data["rejects"] <= data["next"] < TOTAL or data["next"] == 0
                or type(data["heat_step"]) is not int
                or not 0 <= data["heat_step"] < len(self.heat_hours) * STEPS_PER_HOUR
                or self.heat_hour(data["heat_step"])["standort_typ"] != "bad"):
            raise APIError(400, "Ungültiger Checkpoint.")
        with self.lock:
            if data == self.received:
                return
            if self.state != "bereit":
                raise APIError(409, "Auf diesem Empfänger läuft bereits ein Batch.")
            self.received = dict(data)
            self.job = {key: data[key] for key in ("id", "next", "rejects")}
            self.heat_step = data["heat_step"] - 1
            self.state = "rechnet"


def transfer_checkpoint(target, tls, token, checkpoint):
    conn = http.client.HTTPSConnection(target.hostname, target.port or 443, context=tls, timeout=4)
    try:
        conn.request("POST", "/checkpoint", json.dumps(checkpoint),
                     {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
        response = conn.getresponse()
        if response.status != 200 or json.loads(response.read(1024)) != {"accepted": True}:
            raise ValueError("Checkpoint nicht bestätigt")
    finally:
        conn.close()


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
                self.server.batch.retry_transfer()
            return self.reply(200, {"ok": True})
        raise APIError(404, "Endpunkt nicht gefunden.")


def local_demo(open_browser, sender_port=8082, host_port=8092, worker_port=8445):
    """Start both screens with temporary localhost TLS credentials."""
    ports = (sender_port, host_port, worker_port)
    if len(set(ports)) != 3 or any(not 1 <= port <= 65535 for port in ports):
        raise ValueError("Die Demo benötigt drei verschiedene Ports zwischen 1 und 65535.")
    with tempfile.TemporaryDirectory() as folder:
        credentials = Path(folder) / "blister"
        init_credentials("127.0.0.1", credentials)
        processes = []
        try:
            for role, screen_port, options in (
                ("worker", host_port, ["--bind", "127.0.0.1", "--port", str(worker_port)]),
                ("sender", sender_port, ["--target", f"https://127.0.0.1:{worker_port}"]),
            ):
                command = [sys.executable, str(Path(__file__).resolve()), role,
                           "--credentials", str(credentials / role), "--screen-port", str(screen_port), *options]
                process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
                processes.append(process)
                ready = process.stdout.readline()
                if not ready:
                    raise SystemExit(f"{role} konnte nicht starten. Prüfe die Ports {sender_port}, {host_port} und {worker_port}.")
                print(ready.strip(), flush=True)
            if open_browser:
                for port in (sender_port, host_port):
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
    handoff = partial(transfer_checkpoint, target, tls, token) if sender else None
    batch = Batch("Haus · Laptop A" if sender else "Sportbad · Laptop B", args.interval, handoff)
    with ThreadingHTTPServer(("127.0.0.1", screen_port), ScreenHandler) as screen:
        screen.batch = batch
        screen.csrf = secrets.token_urlsafe(32)
        screen.target = target if sender else None
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
