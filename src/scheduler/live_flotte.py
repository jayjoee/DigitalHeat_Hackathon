"""Live-Demo im Flottenmodus: Der Wärme-Router steuert einen echten Prozess, der vom Haus ins Sportbad wandert.

- Standortpaar (Design-Doc, Baustein 9): Haus 01 (Referenzhaus, 8 Server) + sein Anteil am Sportbad
  St. Jakob. Die Bilanz hat 50 Bad-Server für 20 Häuser, also 2,5 pro Haus → 3 Server. Derselbe Router-Code
  wie in der Flottenbilanz, Szenario «Nur Jobs mit Frist», Regel «abgeben», Vorrang der Häuser. Mit 20
  gleichen Häusern wandert der Job meist zuerst zwischen Häusern; das Paar zeigt den Weg Haus → Bad lesbar.
- Der echte Embedding-Job ist ein **markierter Job** im Pool: unbegrenzter Typ A ohne Frist, Startstandort
  Haus 01. Seine Laufmenge pro Stunde (`Flotte.zuteilung`) steuert Rechnen und Pause (SIGCONT/SIGSTOP).
- Wechselt der Router seinen Standort, ist das eine **Migration**: SIGTERM (Block fertig, Checkpoint), dann
  Neustart als neuer Prozess im selben Arbeitsordner. Der Neustart ist echt, der Ortswechsel simuliert.
- **Demo-Tag aus dem Router, keine Sonderlogik:** Ein Trockenlauf über das Jahr sucht den Tag, an dem der
  markierte Job vom Haus ins Bad wandert (mit möglichst vielen Stunden an beiden Orten).

Aufruf:
  .venv/bin/python src/scheduler/live.py --flotte                     # Demo-Tag automatisch
  .venv/bin/python src/scheduler/live.py --flotte --tag 2025-05-20 --sekunden 3
Ergebnis: dashboard/live.json (laufend) und daten/ergebnisse/live_flotte_<tag>.json (Aufzeichnung)
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.flotte import bad_profil, baue, serverzahl_haus  # noqa: E402
from src.scheduler.jahr import profil_laden  # noqa: E402
from src.scheduler.serverbetrieb import Leistungsprofil  # noqa: E402

ROOT = A.ROOT
PY = ROOT / ".venv" / "bin" / "python"
STATUS = ROOT / "dashboard" / "live.json"
SZENARIO, REGEL = "alibaba", "abgeben"


def n_bad_aus_bilanz():
    p = ROOT / "daten" / "ergebnisse" / "flotte.json"
    return json.loads(p.read_text())["server_bad_nach_nachfrage"] if p.exists() else 50


def bad_anteil(n_bad_flotte):
    import math
    return math.ceil(n_bad_flotte / A.wert("flotte_haeuser"))


def neue_flotte(profil, n_bad, leistung=None):
    f, _ = baue(1, serverzahl_haus(profil), SZENARIO, REGEL, profil, bad_profil(profil), n_bad, leistung=leistung)
    j = f.markierter_job(standort=0)
    return f, j


def trockenlauf(profil, n_bad, leistung=None):
    """Ganzes Jahr mit markiertem Job; gibt pro Stunde (Standort, kWh) des Jobs."""
    f, j = neue_flotte(profil, n_bad, leistung)
    spur = []
    for h in range(len(profil)):
        f.schritt(h)
        spur.append(f.zuteilung.get(j.id, (None, 0.0)))
    return f, spur


def demo_tag(profil, f, spur):
    """Tag mit Migration Haus → Bad und möglichst vielen Stunden an beiden Orten (erst Haus, dann Bad)."""
    typ = [s.typ for s in f.st]
    tage = {}
    for h, p in enumerate(profil):
        tage.setdefault(p["zeit"][:10], []).append(h)
    best, best_wert = None, -1
    for tag, hs in tage.items():
        orte = [spur[h][0] for h in hs if spur[h][1] > 1e-9]
        wechsel = [(a, b) for a, b in zip(orte, orte[1:]) if a != b]
        # lesbare Demo: genau ein Haus und genau ein Wechsel, und zwar vom Haus ins Bad
        if len(wechsel) != 1 or typ[wechsel[0][0]] != "haus" or typ[wechsel[0][1]] != "bad":
            continue
        n_haus = sum(1 for o in orte if typ[o] == "haus")
        n_bad = sum(1 for o in orte if typ[o] == "bad")
        wert = min(n_haus, n_bad) * 100 + len(orte)
        if wert > best_wert:
            best, best_wert = tag, wert
    return best


def fortschritt(ordner):
    try:
        return json.loads((ordner / "stand.json").read_text())["naechster"]
    except Exception:
        return 0


def status_schreiben(d):
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False))
    tmp.replace(STATUS)


def starten(ordner, log):
    return subprocess.Popen([str(PY), str(ROOT / "src/jobs/embedding_job.py"), "--arbeitsordner", str(ordner),
                             "--anzahl", "500000"], stdout=log, stderr=log)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--flotte", action="store_true")
    ap.add_argument("--abschalten", action="store_true", help="Ein/Aus-Zustände der Standorte mit simulieren")
    ap.add_argument("--tag", help="JJJJ-MM-TT; Standard: Demo-Tag aus dem Trockenlauf")
    ap.add_argument("--sekunden", type=float, default=3.0, help="Echtzeit pro simulierter Stunde")
    ap.add_argument("--arbeitsordner", default="messungen/live_job_flotte")
    ap.add_argument("--nur-tag", action="store_true", help="nur den Demo-Tag bestimmen und ausgeben")
    a = ap.parse_args(argv)
    leistung = Leistungsprofil(230) if a.abschalten else None

    profil = profil_laden()
    n_bad = bad_anteil(n_bad_aus_bilanz())
    print(f"Trockenlauf: Haus 01 + Sportbad ({n_bad} Server, Anteil eines Hauses), «Nur Jobs mit Frist» …", flush=True)
    f_probe, spur = trockenlauf(profil, n_bad, leistung)
    tag = a.tag or demo_tag(profil, f_probe, spur)
    if tag is None:
        raise SystemExit("Kein Tag mit Migration Haus → Bad gefunden")
    h0 = next(h for h, p in enumerate(profil) if p["zeit"].startswith(tag))
    namen = [s.name for s in f_probe.st]
    plan = [(p["zeit"][11:16], namen[spur[h][0]] if spur[h][0] is not None else "–", round(spur[h][1], 2))
            for h, p in ((h, profil[h]) for h in range(h0, h0 + 24))]
    print(f"Demo-Tag {tag}: " + ", ".join(f"{z} {o} {m:.0%}" for z, o, m in plan if m > 0), flush=True)
    if a.nur_tag:
        return

    # 1) Dieselbe Flotte bis zum Tag vorrechnen (deterministisch, gleicher Zustand wie im Trockenlauf)
    f, j = neue_flotte(profil, n_bad, leistung)
    for h in range(h0):
        f.schritt(h)
    ort = j.standort
    i_bad = next(i for i, s in enumerate(f.st) if s.typ == "bad")

    # 2) Echten Job starten
    ordner = ROOT / a.arbeitsordner
    log = open(ROOT / "messungen" / "live_job.log", "a")
    job = starten(ordner, log)
    time.sleep(1.5)
    os.kill(job.pid, signal.SIGSTOP)
    laeuft = False
    protokoll, migrationen = [], []
    kopf = {"modus": "flotte", "tag": tag, "server": f.st[0].n, "szenario": SZENARIO, "sekunden_pro_stunde": a.sekunden,
            "standort_start": namen[0], "bad": namen[i_bad], "server_bad": n_bad, "echter_server": "markierter Job"}
    print(f"Echter Job PID {job.pid}, startet in {namen[ort]}. 1 h = {a.sekunden:g} s")
    print("Zeit   Temp  Standort             Anteil  Bedarf Haus  Speicher Haus  Bedarf Bad  Texte")

    def melden(z, x, phase, aktiv=True):
        status_schreiben({**kopf, "aktiv": aktiv, "phase": phase, "anteil": round(x, 3), "pid": job.pid,
                          "prozess": "läuft" if laeuft else ("pausiert" if aktiv else "beendet"),
                          "standort": namen[ort], "texte_fertig": fortschritt(ordner), "jetzt": z,
                          "stunden": protokoll, "migrationen": migrationen, "aktualisiert": time.time()})

    try:
        for h in range(h0, h0 + 24):
            r = f.schritt(h)
            i, m = f.zuteilung.get(j.id, (None, 0.0))
            x = max(0.0, min(1.0, m / A.wert("server_kw")))
            if i is not None and i != ort:
                # Migration: Checkpoint am alten Standort, Neustart am neuen
                t0 = time.time()
                if not laeuft:
                    os.kill(job.pid, signal.SIGCONT)
                job.send_signal(signal.SIGTERM)
                job.wait(timeout=60)
                job = starten(ordner, log)
                laeuft = True
                migrationen.append({"zeit": r["zeit"], "von": namen[ort], "nach": namen[i],
                                    "checkpoint_texte": fortschritt(ordner), "dauer_s": round(time.time() - t0, 2),
                                    "neue_pid": job.pid})
                print(f"       ↪ Migration {namen[ort]} → {namen[i]}: Checkpoint bei {fortschritt(ordner):,} Texten, "
                      f"neuer Prozess PID {job.pid}", flush=True)
                ort = i
            zs = r["standorte"]
            z = {"zeit": r["zeit"], "temp_c": zs[0]["temp_c"], "standort": namen[ort],
                 "standort_typ": f.st[ort].typ, "anteil_echter_server": round(x, 3),
                 "bedarf_kwh": zs[ort]["bedarf_kwh"], "speicher_kwh": zs[ort]["speicher_kwh"],
                 "server_laufend": zs[ort]["server_laufend"],
                 "haus_bedarf_kwh": zs[0]["bedarf_kwh"], "haus_speicher_kwh": zs[0]["speicher_kwh"],
                 "haus_server_laufend": zs[0]["server_laufend"], "bad_bedarf_kwh": zs[i_bad]["bedarf_kwh"],
                 "bad_server_laufend": zs[i_bad]["server_laufend"]}
            if leistung is not None:
                z.update(haus_server_eingeschaltet=zs[0]["server_eingeschaltet"],
                         bad_server_eingeschaltet=zs[i_bad]["server_eingeschaltet"],
                         haus_server_standby=zs[0]["server_standby"], bad_server_standby=zs[i_bad]["server_standby"])
            ein_s = x * a.sekunden
            t_start = time.time()
            if ein_s > 0.05:
                os.kill(job.pid, signal.SIGCONT)
                laeuft = True
                melden(z, x, "rechnet")
                time.sleep(ein_s)
            if a.sekunden - ein_s > 0.05:
                os.kill(job.pid, signal.SIGSTOP)
                laeuft = False
                melden(z, x, "pausiert")
                time.sleep(max(0, a.sekunden - (time.time() - t_start)))
            z["texte_fertig"] = fortschritt(ordner)
            print(f"{z['zeit'][11:16]}  {z['temp_c']:5.1f}  {z['standort']:20s} {x:5.0%}   {z['haus_bedarf_kwh']:6.2f}"
                  f"       {z['haus_speicher_kwh']:6.1f}      {z['bad_bedarf_kwh']:7.1f}   {z['texte_fertig']:,}",
                  flush=True)
            protokoll.append(z)
    finally:
        if not laeuft:
            os.kill(job.pid, signal.SIGCONT)
        job.send_signal(signal.SIGTERM)
        job.wait(timeout=60)
        log.close()
        laeuft = False
        ende = {**kopf, "aktiv": False, "phase": "Checkpoint gespeichert", "prozess": "beendet", "pid": job.pid,
                "standort": namen[ort], "texte_fertig": fortschritt(ordner), "stunden": protokoll,
                "migrationen": migrationen, "aktualisiert": time.time()}
        status_schreiben(ende)
    zusatz = "_abschalten" if leistung is not None else ""
    aus = ROOT / "daten" / "ergebnisse" / f"live_flotte_{tag}{zusatz}.json"
    aus.write_text(json.dumps(ende, indent=1, ensure_ascii=False))
    print(f"Checkpoint bei {fortschritt(ordner):,} Texten, {len(migrationen)} Migration(en). "
          f"Protokoll: {aus.relative_to(ROOT)}, Dashboard: dashboard/live.json")


if __name__ == "__main__":
    main()
