"""Gleiches Ergebnis nach Migration: echter Embedding-Job einmal ohne Unterbruch, einmal mit Migration.

Migration = SIGTERM (Block fertig, Checkpoint), dann Neustart als neuer Prozess im selben Arbeitsordner
(«am Zielstandort»; der Standortwechsel ist simuliert, der Neustart echt). Erfolgskriterium Design-Doc:
maximale Abweichung der Vektoren < 1e-6. Läuft mit 1 Thread, damit ONNX Runtime deterministisch rechnet.

Aufruf (dauert einige Minuten, braucht .venv mit fastembed):
  .venv/bin/python messwerkzeug/vektorvergleich.py [--anzahl 5000]
Ergebnis: messungen/vektorvergleich.json
"""
import argparse
import json
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "src" / "jobs" / "embedding_job.py"


def starten(ordner, anzahl):
    return subprocess.Popen([sys.executable, str(JOB), "--arbeitsordner", str(ordner), "--anzahl", str(anzahl),
                             "--threads", "1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def vektoren(ordner):
    teile = sorted(ordner.glob("vektoren_*.npy"))
    return np.concatenate([np.load(t) for t in teile])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anzahl", type=int, default=5000)
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp(prefix="dh_vergleich_"))
    ohne, mit = tmp / "ohne", tmp / "mit"

    t0 = time.time()
    p = starten(ohne, a.anzahl)
    p.communicate()
    dauer_ohne = time.time() - t0

    p = starten(mit, a.anzahl)
    while not (mit / "stand.json").exists() or json.loads((mit / "stand.json").read_text())["naechster"] < a.anzahl // 2:
        time.sleep(0.2)
    t_term = time.time()
    p.send_signal(signal.SIGTERM)
    p.communicate()
    stand = json.loads((mit / "stand.json").read_text())
    checkpoint = stand["naechster"]
    t_neu = time.time()
    p = starten(mit, a.anzahl)  # neuer Prozess, macht beim Checkpoint weiter
    p.communicate()
    stand = json.loads((mit / "stand.json").read_text())

    v1, v2 = vektoren(ohne), vektoren(mit)
    abw = float(np.max(np.abs(v1 - v2))) if v1.shape == v2.shape else None
    r = {"texte": a.anzahl, "threads": 1, "checkpoint_bei": checkpoint, "starts": len(stand["starts"]),
         "form_ohne": list(v1.shape), "form_mit": list(v2.shape), "max_abweichung": abw,
         "bestanden": abw is not None and abw < 1e-6,
         "sigterm_bis_beendet_s": round(t_neu - t_term, 2),
         "neustart_modell_laden_s": stand["starts"][-1].get("modell_laden_s"),
         "dauer_ohne_unterbruch_s": round(dauer_ohne, 1), "zeit": time.strftime("%Y-%m-%d %H:%M")}
    (ROOT / "messungen" / "vektorvergleich.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
    print(json.dumps(r, indent=1, ensure_ascii=False))
    shutil.rmtree(tmp)
    sys.exit(0 if r["bestanden"] else 1)


if __name__ == "__main__":
    main()
