"""Docking auf zwei Leinwänden mit TLS-Checkpoint-Übergabe (wie blister_demo.py, aber virtuelles Screening).

Jedes «Stück» ist ein Molekül (Schlüssel), das an die Abl-Kinase (Schloss) gedockt wird. Die Bindungsenergien
stammen aus einem echten AutoDock-Vina-Lauf (daten/docking/ergebnis.json, exhaustiveness 8) und werden Molekül
für Molekül abgespielt; mit --live und installiertem Vina wird jedes Molekül stattdessen live gedockt.

Übergabe, Paarung, TLS und Wärmeverlauf sind identisch mit der Blister-Demo. Nur das gerechnete Stück und die
Leinwand unterscheiden sich.
"""
import argparse
from collections import deque
import csv
import hmac
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
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
from src.referenzprofil import INNEN_C  # noqa: E402
from src.scheduler.annahmen import wert  # noqa: E402

DOCKING = ROOT / "daten" / "docking"
STATIC = Path(__file__).with_name("docking")
STEPS_PER_HOUR = 2
TRACE = ROOT / "daten/ergebnisse/live_flotte_2025-05-25.json"
FORWARD_C = 55  # Illustrativer Vorlauf, nicht im Router-Modell.
RETURN_TANK_KWH = 32.0
STARK_KCAL = -10.0  # ab dieser Bindungsenergie gilt ein Molekül als starker Treffer

with (DOCKING / "molekuele.csv").open(encoding="utf-8") as _f:
    MOLEKUELE = [(z["name"], z["gruppe"]) for z in csv.DictReader(_f)]
TOTAL = len(MOLEKUELE)
_tab = json.loads((DOCKING / "ergebnis.json").read_text(encoding="utf-8"))["moleküle"]
ENERGIEN = [round(_tab[name]["energie_kcal_mol"], 1) for name, _ in MOLEKUELE]


def heat_profile():
    """Erste aufgezeichnete Übergabe behalten, danach entnimmt das Haus Wärme aus dem Speicher."""
    hours = json.loads(TRACE.read_text())["stunden"]
    switch = next(i for i, hour in enumerate(hours) if hour["standort_typ"] == "bad")
    capacity = wert("speicher_kwh")
    server_heat = wert("server_kw") * wert("waermerueckgewinnung")
    tank = capacity
    returned = False
    for hour in hours[switch:]:
        returned = returned or tank <= RETURN_TANK_KWH
        hour["haus_speicher_kwh"] = round(tank, 3)
        if returned:
            hour["standort_typ"] = "haus"
            hour["anteil_echter_server"] = 1.0
        tank = min(capacity, max(0, tank - hour["haus_bedarf_kwh"] + (server_heat if returned else 0)))
    return hours[max(0, switch - 4):]


class LiveVina:
    """Dockt ein Molekül live mit dem Vina-Python-Paket (nur mit --live und installiertem Paket)."""
    def __init__(self):
        from vina import Vina
        self.v = Vina(sf_name="vina", cpu=0, seed=1, verbosity=0)
        self.v.set_receptor(str(DOCKING / "1iep_receptor.pdbqt"))
        self.v.compute_vina_maps(center=[15.190, 53.903, 16.917], box_size=[20, 20, 20])

    def energie(self, index):
        name = MOLEKUELE[index][0]
        self.v.set_ligand_from_file(str(DOCKING / "liganden" / f"{name}.pdbqt"))
        self.v.dock(exhaustiveness=8, n_poses=1)
        return round(float(self.v.energies(n_poses=1)[0][0]), 1)


def dock(index, vina=None):
    name, gruppe = MOLEKUELE[index]
    energie = vina.energie(index) if vina else ENERGIEN[index]
    return {"index": index, "name": name, "gruppe": gruppe, "energie": energie, "stark": energie <= STARK_KCAL}


def valid_checkpoint(data):
    return (isinstance(data, dict) and set(data) == {"id", "next", "rejects", "heat_step"}
            and isinstance(data["id"], str) and len(data["id"]) == 32
            and type(data["next"]) is int and type(data["rejects"]) is int
            and 0 <= data["rejects"] <= data["next"] <= TOTAL
            and type(data["heat_step"]) is int and data["heat_step"] >= 0)


class Batch:
    def __init__(self, site, interval, link=None, vina=None):
        self.site, self.interval, self.vina = site, interval, vina
        self.lock = threading.Lock()
        self.job = None
        self.state = "bereit"
        self.item = None
        self.received = None
        self.history = deque(maxlen=4)
        self.local_ranges = []
        self.link = link
        self.local_site = "haus" if link else "bad"
        self.heat_hours = heat_profile()
        self.heat_step = -1
        self.return_at = None
        self.remote_view = None
        self.sync_pending = False
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while not self.stop.wait(self.interval):
            with self.lock:
                if self.state == "übergeben":
                    action = self.follow_pool
                elif self.state == "rechnet":
                    action = self.tick()
                else:
                    continue
            if action is not None:
                action()

    def tick(self):
        self.heat_step += 1
        self.remote_view = None
        hour = self.heat_hour(self.heat_step)
        if hour["standort_typ"] != self.local_site:
            if self.link:
                self.state = "Übergabe läuft"
                return self.send_checkpoint
            self.return_at = self.job["next"] + 1
            self.state = "zurückgegeben"
            return None
        if hour["anteil_echter_server"] > 0 and self.job["next"] < TOTAL:
            index = self.job["next"]
            # Docking (echt oder abgespielt) ausserhalb der Sperre: die Leinwand bleibt flüssig.
            self.lock.release()
            try:
                item = dock(index, self.vina)
            finally:
                self.lock.acquire()
            self.item = item
            self.job["next"] += 1
            self.job["rejects"] += int(item["stark"])
            number = self.job["next"]
            self.history.append(number)
            if self.local_ranges and self.local_ranges[-1][1] == number - 1:
                self.local_ranges[-1][1] = number
            else:
                self.local_ranges.append([number, number])
            if number == TOTAL:
                self.state = "fertig"
        if self.link and self.return_at is not None:
            return self.publish_progress
        return None

    def heat_hour(self, step):
        return self.heat_hours[min(len(self.heat_hours) - 1, step // STEPS_PER_HOUR)]

    def heat_snapshot(self, display_step):
        initial_step = self.received["heat_step"] if self.received else 0
        hour = self.heat_hour(max(initial_step, display_step))
        working = self.state == "rechnet" and hour["standort_typ"] == self.local_site
        heat_kw = (wert("server_kw") * wert("waermerueckgewinnung") * hour["anteil_echter_server"]
                   if working else 0)
        return {"time": hour["zeit"], "outside_c": hour["temp_c"], "room_target_c": INNEN_C,
                "tank_kwh": hour["haus_speicher_kwh"], "tank_max_kwh": wert("speicher_kwh"),
                "heat_kw": round(heat_kw, 3), "forward_c": FORWARD_C if heat_kw else None,
                "scheduled_pause": working and heat_kw == 0}

    def snapshot(self):
        with self.lock:
            view = self.remote_view or self.job
            display_step = self.remote_view["heat_step"] if self.remote_view else self.heat_step
            job = {key: view[key] for key in ("id", "next", "rejects")} if view else None
            return {"site": self.site, "state": self.state, "job": job,
                    "item": self.item, "recent": list(self.history), "total": TOTAL,
                    "local_ranges": [span.copy() for span in self.local_ranges],
                    "resumed_after": self.received["next"] if self.received else 0,
                    "return_at": self.return_at, "sync_pending": self.sync_pending,
                    "schloss": "Abl-Kinase (Leukämie-Ziel)", "stark_kcal": STARK_KCAL,
                    "molekuele": [{"name": n, "gruppe": g, "energie": e}
                                  for (n, g), e in zip(MOLEKUELE, ENERGIEN)],
                    "heat": self.heat_snapshot(display_step)}

    def start(self):
        with self.lock:
            if self.state != "bereit":
                raise APIError(409, "Der Docking-Lauf wurde bereits gestartet.")
            self.job = {"id": uuid.uuid4().hex, "next": 0, "rejects": 0}
            self.state = "rechnet"

    def retry_transfer(self):
        with self.lock:
            if self.state != "Übergabe offen":
                raise APIError(409, "Es gibt keine offene Übergabe.")
            self.state = "Übergabe läuft"
        if not self.send_checkpoint():
            raise APIError(502, "Übergabe unbestätigt. Das Haus bleibt pausiert.")

    def send_checkpoint(self):
        with self.lock:
            checkpoint = {**self.job, "heat_step": self.heat_step}
        try:
            if self.link.request("POST", "/checkpoint", checkpoint) != {"accepted": True}:
                raise ValueError("Checkpoint nicht bestätigt")
        except (OSError, ValueError, http.client.HTTPException):
            with self.lock:
                self.state = "Übergabe offen"
            return False
        with self.lock:
            self.state = "übergeben"
        return True

    def receive(self, data):
        if (not valid_checkpoint(data) or not 0 < data["next"] < TOTAL
                or data["heat_step"] >= len(self.heat_hours) * STEPS_PER_HOUR
                or self.heat_hour(data["heat_step"])["standort_typ"] != "bad"):
            raise APIError(400, "Ungültiger Checkpoint.")
        with self.lock:
            if data == self.received:
                return
            if self.state != "bereit":
                raise APIError(409, "Auf diesem Empfänger läuft bereits ein Lauf.")
            self.received = dict(data)
            self.job = {key: data[key] for key in ("id", "next", "rejects")}
            self.heat_step = data["heat_step"] - 1
            self.state = "rechnet"

    def pool_progress(self):
        with self.lock:
            checkpoint = {**self.job, "heat_step": self.heat_step} if self.job else None
            if self.received and self.heat_step < self.received["heat_step"]:
                checkpoint["heat_step"] = self.received["heat_step"]
            return {"checkpoint": checkpoint, "returned": self.state == "zurückgegeben"}

    def follow_pool(self):
        try:
            response = self.link.request("GET", "/checkpoint")
            checkpoint = response.get("checkpoint") if isinstance(response, dict) else None
            if not valid_checkpoint(checkpoint) or checkpoint["id"] != self.job["id"]:
                raise ValueError("Prüfstand nicht verfügbar")
            with self.lock:
                previous = self.remote_view or {**self.job, "heat_step": self.heat_step}
                if checkpoint["heat_step"] < previous["heat_step"] or checkpoint["next"] < previous["next"]:
                    raise ValueError("Prüfstand ist älter als der letzte Empfang")
                self.sync_pending = False
                self.remote_view = checkpoint
                if (response.get("returned") is True and checkpoint["next"] < TOTAL
                        and self.heat_hour(checkpoint["heat_step"])["standort_typ"] == "haus"):
                    self.return_at = checkpoint["next"] + 1
                    self.job = {key: checkpoint[key] for key in ("id", "next", "rejects")}
                    self.heat_step = checkpoint["heat_step"] - 1
                    self.state = "rechnet"
        except (OSError, ValueError, http.client.HTTPException):
            with self.lock:
                self.sync_pending = True

    def publish_progress(self):
        with self.lock:
            progress = {**self.job, "heat_step": self.heat_step}
        try:
            self.link.request("POST", "/progress", progress, timeout=.4)
        except (OSError, ValueError, http.client.HTTPException):
            pass

    def observe_house(self, data):
        if not valid_checkpoint(data):
            raise APIError(400, "Ungültiger Prüfstand.")
        with self.lock:
            current = self.remote_view or {**(self.job or {}), "heat_step": self.heat_step}
            if (self.state != "zurückgegeben" or data["id"] != self.job["id"]
                    or data["next"] < current["next"] or data["heat_step"] < current["heat_step"]):
                raise APIError(409, "Meldung passt nicht zum zurückgegebenen Lauf.")
            self.remote_view = data


class PoolLink:
    def __init__(self, target, tls, token):
        self.target, self.tls, self.token = target, tls, token

    def request(self, method, path, data=None, *, timeout=4):
        conn = http.client.HTTPSConnection(self.target.hostname, self.target.port or 443,
                                           context=self.tls, timeout=timeout)
        try:
            body = json.dumps(data) if data is not None else None
            conn.request(method, path, body, {"Authorization": "Bearer " + self.token,
                                              "Content-Type": "application/json"})
            response = conn.getresponse()
            if response.status != 200:
                raise ValueError("Prüfstand nicht bestätigt")
            return json.loads(response.read(4096))
        finally:
            conn.close()


class TransferHandler(Handler):
    def route(self, method):
        if not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + self.server.token):
            raise APIError(401, "Ungültiger Zugangsschlüssel.")
        batch = self.server.batch
        if method == "GET" and self.path == "/checkpoint":
            return self.reply(200, batch.pool_progress())
        if method == "POST" and self.path == "/checkpoint":
            batch.receive(self.body())
            return self.reply(200, {"accepted": True})
        if method == "POST" and self.path == "/progress":
            batch.observe_house(self.body())
            return self.reply(200, {"accepted": True})
        raise APIError(404, "Endpunkt nicht gefunden.")


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


def local_demo(open_browser, vina, sender_port=8083, host_port=8093, worker_port=8446):
    ports = (sender_port, host_port, worker_port)
    if len(set(ports)) != 3 or any(not 1 <= port <= 65535 for port in ports):
        raise ValueError("Die Demo benötigt drei verschiedene Ports zwischen 1 und 65535.")
    with tempfile.TemporaryDirectory() as folder:
        credentials = Path(folder) / "docking"
        init_credentials("127.0.0.1", credentials)
        processes = []
        try:
            for role, screen_port, options in (
                ("worker", host_port, ["--bind", "127.0.0.1", "--port", str(worker_port)]),
                ("sender", sender_port, ["--target", f"https://127.0.0.1:{worker_port}"]),
            ):
                command = [sys.executable, str(Path(__file__).resolve()), role,
                           "--credentials", str(credentials / role), "--screen-port", str(screen_port), *options]
                if vina:
                    command.append("--live")
                process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
                processes.append(process)
                ready = process.stdout.readline()
                if not ready:
                    raise SystemExit(f"{role} konnte nicht starten. Prüfe die Ports {ports}.")
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
    parser.add_argument("--port", type=int, default=8446)
    parser.add_argument("--screen-port", type=int)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--target")
    parser.add_argument("--interval", type=float, default=1.6)
    parser.add_argument("--live", action="store_true", help="Jedes Molekül live mit Vina docken (statt abspielen)")
    parser.add_argument("--open", action="store_true", help="Lokale Demo in zwei Browser-Tabs öffnen")
    args = parser.parse_args()
    vina = None
    if args.live:
        try:
            vina = LiveVina()
        except ImportError:
            parser.error("--live braucht das Vina-Python-Paket (pip install -r requirements/docking.txt). "
                         "Ohne --live spielt die Demo die echten Ergebnisse aus daten/docking/ergebnis.json ab.")
    if args.role == "demo":
        return local_demo(args.open, vina)
    if args.credentials is None:
        parser.error("--credentials ist für sender und worker erforderlich.")
    if args.open:
        parser.error("--open ist für demo vorgesehen.")
    target = urlsplit(args.target or "")
    if args.role == "sender" and (target.scheme != "https" or not target.hostname
                                  or target.path not in ("", "/") or target.username
                                  or target.password or target.query or target.fragment):
        parser.error("Sender benötigt --target https://EMPFÄNGER:8446")
    if not 0.05 <= args.interval <= 60:
        parser.error("--interval muss zwischen 0.05 und 60 Sekunden liegen.")
    cert = str(args.credentials / "worker-cert.pem")
    token = (args.credentials / "token.txt").read_text().strip()
    if len(token) < 40:
        parser.error("Der Zugangsschlüssel ist ungültig.")
    sender = args.role == "sender"
    screen_port = args.screen_port or (8083 if sender else 8093)
    tls = tls_context(cert) if sender else tls_context(cert, str(args.credentials / "worker-key.pem"))
    link = PoolLink(target, tls, token) if sender else None
    batch = Batch("Haus · Laptop A" if sender else "Sportbad · Laptop B", args.interval, link, vina)
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
