"""Live-Demo: Derselbe Scheduler (Haus.schritt → kern.entscheide) steuert einen echten Prozess.

- Das Jahresmodell läuft bis zum gewählten Tag vor (gleicher Zustand wie in der Jahresbilanz).
- Danach wird der Tag Stunde für Stunde gerechnet, jede Stunde dauert --sekunden Echtzeit.
- Einer der Server im Keller ist der echte Embedding-Job (src/jobs/embedding_job.py).
  Rechnet der Scheduler für diesen Server einen Anteil x der Stunde, läuft der Prozess x der Zeit
  und wird danach mit SIGSTOP angehalten. SIGCONT setzt ihn fort.
- Am Ende: SIGTERM → Checkpoint. Ein späterer Lauf macht dort weiter.
- Mit --job docking ist der echte Prozess ein virtuelles Screening (src/jobs/docking_job.py, AutoDock Vina):
  Moleküle werden an die Abl-Kinase gedockt. Pause und Weiterlauf gelten für die ganze Prozessgruppe,
  also auch für ein Vina-Programm, das der Auftrag startet.

Flottenmodus (Wärme-Router, Job wandert vom Haus ins Sportbad): siehe src/scheduler/live_flotte.py
  .venv/bin/python src/scheduler/live.py --flotte

Aufruf:
  .venv/bin/python src/scheduler/live.py --tag 2025-01-15 --server 8
  .venv/bin/python src/scheduler/live.py --tag 2025-07-15 --server 8 --sekunden 4
  python3 src/scheduler/live.py --tag 2025-03-07 --server 8 --sekunden 3 --job docking
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
from src.scheduler.jahr import Haus  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PY = ROOT / ".venv" / "bin" / "python"


def stunde_von(profil, tag):
    for h, p in enumerate(profil):
        if p["zeit"].startswith(tag):
            return h
    raise SystemExit(f"Tag {tag} nicht im Profil")


def anteil(strom_kwh, k, server_kw=1.0):
    """Anteil der Stunde, den Server k (0-basiert) rechnet, wenn Server der Reihe nach belegt werden."""
    return max(0.0, min(1.0, strom_kwh / server_kw - k))


def waehle_server(zeilen, n):
    """Den Server nehmen, dessen Laufzeit über den Tag am stärksten schwankt (zeigt Pause und Weiterlauf)."""
    def streuung(k):
        a = [anteil(z["strom_kwh"], k) for z in zeilen]
        m = sum(a) / len(a)
        return sum((x - m) ** 2 for x in a)
    return max(range(n), key=streuung)


JOBS = {  # Skript, Einheit, Startargumente, Arbeitsordner, Wartezeit beim Beenden (s)
    "embedding": ("src/jobs/embedding_job.py", "Texte", ["--anzahl", "500000"], "messungen/live_job", 30),
    "docking": ("src/jobs/docking_job.py", "Moleküle", ["--anzahl", "100000"], "messungen/docking_job", 300),
}


def gruppe(job, sig):
    """Signal an die ganze Prozessgruppe des Auftrags (auch an Kindprozesse wie das Vina-Programm)."""
    try:
        os.killpg(job.pid, sig)
    except ProcessLookupError:
        pass


def fortschritt(ordner):
    try:
        s = json.loads((ordner / "stand.json").read_text())
        return s["naechster"]
    except Exception:
        return 0


STATUS = ROOT / "dashboard" / "live.json"


def status_schreiben(d):
    """Für das Dashboard: aktueller Stand, atomar geschrieben."""
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False))
    tmp.replace(STATUS)


def prozess_status(pid):
    try:
        st = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
        return "pausiert" if st.startswith("T") else ("läuft" if st else "beendet")
    except Exception:
        return "unbekannt"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="JJJJ-MM-TT, z. B. 2025-01-15 oder 2025-07-15")
    ap.add_argument("--server", type=int, default=8)
    ap.add_argument("--szenario", default="spot", choices=["spot", "alibaba"])
    ap.add_argument("--sekunden", type=float, default=5.0, help="Echtzeit pro simulierter Stunde")
    ap.add_argument("--echter-server", type=int, help="Index 0..N-1, Standard: automatisch")
    ap.add_argument("--job", default="embedding", choices=sorted(JOBS), help="echter Prozess: Text-Embedding oder Docking")
    ap.add_argument("--arbeitsordner", help="Standard je nach Auftrag (messungen/live_job bzw. messungen/docking_job)")
    a = ap.parse_args()
    skript, einheit, job_args, ordner_standard, warten_s = JOBS[a.job]

    # 1) Jahresmodell bis zum Tag vorrechnen, dann den Tag trocken rechnen, um den Server zu wählen
    haus = Haus(a.server, a.szenario)
    h0 = stunde_von(haus.profil, a.tag)
    for h in range(h0):
        haus.schritt(h)
    probe = Haus(a.server, a.szenario)
    for h in range(h0):
        probe.schritt(h)
    k = a.echter_server if a.echter_server is not None else waehle_server(
        [probe.schritt(h) for h in range(h0, h0 + 24)], a.server)

    # 2) Echten Job starten (läuft lange, damit er den Tag nicht vorzeitig beendet)
    ordner = ROOT / (a.arbeitsordner or ordner_standard)
    log = open(ROOT / "messungen" / f"live_{a.job}.log", "a")
    python = str(PY) if PY.exists() else sys.executable
    job = subprocess.Popen([python, str(ROOT / skript), "--arbeitsordner", str(ordner), *job_args],
                           stdout=log, stderr=log, start_new_session=True)  # eigene Prozessgruppe
    time.sleep(1.5)  # Modell bzw. Bindetasche laden
    gruppe(job, signal.SIGSTOP)
    laeuft = False
    protokoll = []
    print(f"Tag {a.tag}, {a.server} Server, echter Job = Server {k + 1} (PID {job.pid}), "
          f"1 h = {a.sekunden:g} s")
    print("Zeit   Temp   Bedarf  Speicher  Server an   Server " f"{k + 1}  Job     {einheit}")
    kopf = {"tag": a.tag, "server": a.server, "szenario": a.szenario, "echter_server": k + 1,
            "pid": job.pid, "sekunden_pro_stunde": a.sekunden, "auftrag": a.job, "einheit": einheit}

    def melden(z, x, phase, stunden):
        status_schreiben({**kopf, "aktiv": True, "phase": phase, "anteil": round(x, 3),
                          "prozess": prozess_status(job.pid), "texte_fertig": fortschritt(ordner),
                          "jetzt": z, "stunden": stunden, "aktualisiert": time.time()})

    try:
        for h in range(h0, h0 + 24):
            z = haus.schritt(h)
            x = anteil(z["strom_kwh"], k)
            ein_s = x * a.sekunden
            t_start = time.time()
            if ein_s > 0.05:
                gruppe(job, signal.SIGCONT)
                laeuft = True
                melden(z, x, "rechnet", protokoll)
                time.sleep(ein_s)
            if a.sekunden - ein_s > 0.05:
                gruppe(job, signal.SIGSTOP)
                laeuft = False
                melden(z, x, "pausiert", protokoll)
                time.sleep(max(0, a.sekunden - (time.time() - t_start)))
            n_texte = fortschritt(ordner)
            zustand = "läuft" if x >= 0.99 else ("pausiert" if x <= 0.01 else f"{x:.0%} an")
            print(f"{z['zeit'][11:16]}  {z['temp_c']:5.1f}  {z['bedarf_kwh']:5.2f}   {z['speicher_kwh']:6.1f}"
                  f"    {z['server_laufend']:5.2f}      {x:4.0%}    {zustand:8s} {n_texte:,}", flush=True)
            protokoll.append({**z, "echter_server": k + 1, "anteil_echter_server": round(x, 3),
                              "texte_fertig": n_texte, "echtzeit_ein_s": round(ein_s, 2)})
    finally:
        if not laeuft:
            gruppe(job, signal.SIGCONT)
        job.send_signal(signal.SIGTERM)  # Block bzw. Molekül fertig, Checkpoint, Ende
        job.wait(timeout=warten_s)
        log.close()
        status_schreiben({**kopf, "aktiv": False, "phase": "Checkpoint gespeichert", "prozess": "beendet",
                          "texte_fertig": fortschritt(ordner), "stunden": protokoll,
                          "aktualisiert": time.time()})
    aus = ROOT / "daten" / "ergebnisse" / (f"live_{a.tag}.json" if a.job == "embedding" else f"live_{a.job}_{a.tag}.json")
    aus.parent.mkdir(parents=True, exist_ok=True)
    aus.write_text(json.dumps({"tag": a.tag, "server": a.server, "szenario": a.szenario, "auftrag": a.job,
                               "echter_server": k + 1, "pid": job.pid, "stunden": protokoll},
                              indent=1, ensure_ascii=False))
    print(f"Checkpoint bei {fortschritt(ordner):,} {einheit}n, Exit {job.returncode}. Protokoll: {aus.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--flotte" in sys.argv:
        from src.scheduler.live_flotte import main as flotte_main
        flotte_main()
    else:
        main()
