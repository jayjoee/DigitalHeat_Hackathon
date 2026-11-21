"""Blister-Demo auf zwei Laptops ohne Handarbeit.

Laptop B:  python3 prototyp/schwimmbad.py   → zeigt einen 6-stelligen Code
Laptop A:  python3 prototyp/haus.py         → findet das Schwimmbad im WLAN, fragt nach dem Code, los

Ablauf:
- Das Schwimmbad erzeugt bei jedem Start frische Zugangsdaten (Zertifikat für seine WLAN-Adresse und
  Token) in einem temporären Ordner. Nichts landet im Repo, beim Beenden ist alles weg.
- Es ruft jede Sekunde «hier bin ich» ins lokale Netz (UDP-Broadcast, Port 8447).
- Das Haus hört zu, nimmt das gefundene Schwimmbad und holt mit dem Code einmal Zertifikat und Token
  ab (TLS 1.3, Port 8446). Nach 10 falschen Codes sperrt das Schwimmbad die Paarung.
- Danach laufen die bestehenden Prozesse aus blister_demo.py: Empfänger im Bad, Sender im Haus.

Grenze: Die Paarung prüft den Code, aber das Haus kennt das Zertifikat vorher nicht (wie beim ersten
Bluetooth-Pairing). Gegen jemanden, der im selben WLAN genau im Moment der Paarung aktiv dazwischen-
geht, schützt das nicht. Für die Demo mit synthetischen Bildern reicht das; für echte Daten nicht.
"""
import argparse
import hmac
import http.client
import json
import secrets
import signal
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digitalheat import APIError, Handler, init_credentials, private_write, tls_context  # noqa: E402

DEMO = Path(__file__).resolve().with_name("blister_demo.py")
PORT_UEBERGABE, PORT_PAARUNG, PORT_SUCHE = 8445, 8446, 8447
BILDSCHIRM_HAUS, BILDSCHIRM_BAD = 8082, 8092
KENNUNG = b"DIGITALHEAT-SCHWIMMBAD"


def wlan_adresse():
    """Eigene Adresse im lokalen Netz (es wird nichts gesendet)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def kasten(*zeilen):
    breite = max(len(z) for z in zeilen) + 4
    print("\n" + "█" * breite)
    for z in zeilen:
        print("█ " + z.ljust(breite - 4) + " █")
    print("█" * breite + "\n", flush=True)


def starte(rolle, *argumente):
    """blister_demo.py als Kindprozess starten und warten, bis er bereit ist."""
    p = subprocess.Popen([sys.executable, str(DEMO), rolle, *argumente], stdout=subprocess.PIPE, text=True)
    if not p.stdout.readline():
        raise SystemExit(f"Der {rolle} konnte nicht starten. Läuft schon eine Demo? Ports 8082/8092/8445 prüfen.")
    return p


def laufen_lassen(prozess, aufraeumen):
    try:
        prozess.wait()
    except KeyboardInterrupt:
        pass
    finally:
        aufraeumen()
        if prozess.poll() is None:
            prozess.terminate()
            prozess.wait()


# ---------- Schwimmbad (Laptop B, Empfänger) ----------

class PaarHandler(Handler):
    def route(self, method):
        if method != "POST" or self.path != "/paar":
            raise APIError(404, "Endpunkt nicht gefunden.")
        s = self.server
        with s.lock:
            if s.fehlversuche >= 10:
                raise APIError(429, "Zu viele falsche Codes. Schwimmbad neu starten.")
        daten = self.body()
        code = str(daten.get("code", "")).replace(" ", "") if isinstance(daten, dict) else ""
        if not hmac.compare_digest(code.encode(), s.code.encode()):
            with s.lock:
                s.fehlversuche += 1
            time.sleep(1)
            raise APIError(403, "Falscher Code.")
        print(f"Haus verbunden: {self.client_address[0]}", flush=True)
        self.reply(200, {"cert": s.cert, "token": s.token})


def ankuendigen(adresse, stopp):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    nachricht = KENNUNG + b" " + adresse.encode()
    while not stopp.wait(1):
        for ziel in ("<broadcast>", "127.0.0.1"):
            try:
                s.sendto(nachricht, (ziel, PORT_SUCHE))
            except OSError:
                pass
    s.close()


def schwimmbad(args):
    adresse = args.ip or wlan_adresse()
    with tempfile.TemporaryDirectory() as ordner:
        zugang = Path(ordner) / "blister"
        init_credentials(adresse, zugang)
        code = f"{secrets.randbelow(10 ** 6):06d}"
        tls = tls_context(str(zugang / "worker" / "worker-cert.pem"), str(zugang / "worker" / "worker-key.pem"))
        paar = ThreadingHTTPServer(("0.0.0.0", PORT_PAARUNG), PaarHandler)
        paar.code, paar.lock, paar.fehlversuche = code, threading.Lock(), 0
        paar.cert = (zugang / "sender" / "worker-cert.pem").read_text()
        paar.token = (zugang / "sender" / "token.txt").read_text().strip()
        paar.socket = tls.wrap_socket(paar.socket, server_side=True)
        threading.Thread(target=paar.serve_forever, daemon=True).start()
        stopp = threading.Event()
        threading.Thread(target=ankuendigen, args=(adresse, stopp), daemon=True).start()

        prozess = starte("worker", "--credentials", str(zugang / "worker"))
        kasten("SCHWIMMBAD bereit (Laptop B)",
               f"Code für das Haus:   {code[:3]} {code[3:]}",
               f"Adresse:             {adresse}",
               f"Leinwand:            http://127.0.0.1:{BILDSCHIRM_BAD}",
               "Beenden mit Ctrl+C")
        if not args.kein_browser:
            webbrowser.open(f"http://127.0.0.1:{BILDSCHIRM_BAD}")

        def aufraeumen():
            stopp.set()
            paar.shutdown()
            paar.server_close()
        laufen_lassen(prozess, aufraeumen)


# ---------- Haus (Laptop A, Sender) ----------

def suche_schwimmbad(sekunden):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(("", PORT_SUCHE))
    s.settimeout(0.5)
    gefunden, start = {}, time.time()
    print("Suche das Schwimmbad im WLAN …", flush=True)
    while time.time() - start < sekunden and not (gefunden and time.time() - start > 3):
        try:
            daten, (absender, _) = s.recvfrom(256)
        except socket.timeout:
            continue
        if daten.startswith(KENNUNG):
            gemeldet = daten.split(b" ", 1)[-1].decode(errors="ignore")
            # Die gemeldete Adresse zählt nur, wenn sie zum Absender passt (oder es derselbe Rechner ist).
            gefunden[gemeldet if absender in (gemeldet, "127.0.0.1") else absender] = True
    s.close()
    return list(gefunden)


def waehle(adressen):
    if len(adressen) == 1:
        return adressen[0]
    print("Mehrere Schwimmbäder gefunden:")
    for n, a in enumerate(adressen, 1):
        print(f"  {n}) {a}")
    while True:
        wahl = input("Nummer wählen (Adresse steht auf dem Schwimmbad-Laptop): ").strip()
        if wahl.isdigit() and 1 <= int(wahl) <= len(adressen):
            return adressen[int(wahl) - 1]


def paaren(adresse, code):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE  # Zertifikat erst nach dem Code bekannt
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    conn = http.client.HTTPSConnection(adresse, PORT_PAARUNG, context=ctx, timeout=10)
    try:
        conn.request("POST", "/paar", json.dumps({"code": code}), {"Content-Type": "application/json"})
        vorgezeigt = conn.sock.getpeercert(binary_form=True)
        antwort = conn.getresponse()
        daten = json.loads(antwort.read(65536) or b"{}")
    except (OSError, ValueError, http.client.HTTPException) as e:
        raise SystemExit(f"Schwimmbad unter {adresse} nicht erreichbar ({e}). Gleiches WLAN? Firewall?")
    finally:
        conn.close()
    if antwort.status != 200:
        raise SystemExit("Paarung abgelehnt: " + daten.get("error", f"HTTP {antwort.status}"))
    if ssl.PEM_cert_to_DER_cert(daten["cert"]) != vorgezeigt:
        raise SystemExit("Das Zertifikat passt nicht zum Gerät. Abbruch.")
    return daten


def haus(args):
    adressen = [args.bad] if args.bad else suche_schwimmbad(args.suchzeit)
    if not adressen:
        raise SystemExit("Kein Schwimmbad gefunden. Läuft schwimmbad.py auf dem anderen Laptop?\n"
                         "Beide im selben WLAN? Viele Gast-WLANs trennen Geräte, dann Handy-Hotspot nehmen.\n"
                         "Oder die Adresse direkt angeben: python3 prototyp/haus.py --bad 192.168.1.42")
    adresse = waehle(adressen)
    print(f"Schwimmbad gefunden: {adresse}", flush=True)
    code = (args.code or input("Code vom Schwimmbad-Laptop: ")).replace(" ", "").strip()
    daten = paaren(adresse, code)

    with tempfile.TemporaryDirectory() as ordner:
        zugang = Path(ordner) / "sender"
        zugang.mkdir(mode=0o700)
        private_write(zugang / "worker-cert.pem", daten["cert"].encode())
        private_write(zugang / "token.txt", daten["token"].encode())
        prozess = starte("sender", "--credentials", str(zugang),
                         "--target", f"https://{adresse}:{PORT_UEBERGABE}")
        kasten("HAUS bereit (Laptop A)",
               f"Verbunden mit Schwimmbad {adresse}",
               f"Leinwand: http://127.0.0.1:{BILDSCHIRM_HAUS}",
               "Dort «Batch starten», dann «Zum Sportbad wechseln»",
               "Beenden mit Ctrl+C")
        if not args.kein_browser:
            webbrowser.open(f"http://127.0.0.1:{BILDSCHIRM_HAUS}")
        laufen_lassen(prozess, lambda: None)


def main(rolle=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    if rolle is None:
        p.add_argument("rolle", choices=("haus", "schwimmbad"))
    p.add_argument("--kein-browser", action="store_true", help="Leinwand nicht automatisch öffnen")
    if rolle in (None, "haus"):
        p.add_argument("--bad", help="Adresse des Schwimmbads, falls die Suche nichts findet")
        p.add_argument("--code", help="Code vom Schwimmbad-Laptop (sonst wird gefragt)")
        p.add_argument("--suchzeit", type=float, default=10, help="Sekunden für die Suche")
    if rolle in (None, "schwimmbad"):
        p.add_argument("--ip", help="eigene WLAN-Adresse, falls sie falsch erkannt wird")
    args = p.parse_args()
    rolle = rolle or args.rolle

    def beenden(*_):
        raise KeyboardInterrupt
    # Terminalfenster schliessen oder kill: Kindprozesse trotzdem sauber beenden.
    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, beenden)
    try:
        (haus if rolle == "haus" else schwimmbad)(args)
    except ValueError as e:
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
