"""Echter Rechenjob: Text-Embeddings auf der CPU, pausierbar und mit Checkpoints.

- Modell: BAAI/bge-small-en-v1.5 (384 Dimensionen) über fastembed/ONNX Runtime
- Daten: AG News Testset (7'600 Nachrichtentexte), daten/agnews_test.jsonl
- Arbeitet in Blöcken. Nach jedem Block werden Vektoren und Stand gespeichert.
- Steuerung von aussen:
    SIGSTOP / SIGCONT  -> Pause und Weiterlauf (Prozess bleibt im Speicher)
    SIGTERM            -> Block fertig rechnen, Checkpoint schreiben, beenden
  Ein neuer Start mit demselben --arbeitsordner macht beim Checkpoint weiter.
- Misst pro Block: Wandzeit, CPU-Zeit des Prozesses, Anzahl Texte.

Aufruf:
  .venv/bin/python src/jobs/embedding_job.py --arbeitsordner messungen/lauf1 [--anzahl 7600] [--block 256]
"""
import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATEN = ROOT / "daten" / "agnews_test.jsonl"
MODELL = "BAAI/bge-small-en-v1.5"

aufhoeren = False


def _sigterm(_sig, _frame):
    global aufhoeren
    aufhoeren = True


def texte_laden(anzahl):
    with DATEN.open() as f:
        t = [json.loads(z)["text"] for z in f]
    while len(t) < anzahl:  # für längere Jobs den Datensatz wiederholen
        t = t + t
    return t[:anzahl]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arbeitsordner", required=True)
    ap.add_argument("--anzahl", type=int, default=7600)
    ap.add_argument("--block", type=int, default=128, help="Texte pro Checkpoint")
    ap.add_argument("--batch", type=int, default=16, help="Texte pro Modellaufruf (16 war am schnellsten)")
    ap.add_argument("--threads", type=int, default=6, help="6 = Leistungskerne des M1 Pro")
    a = ap.parse_args()

    signal.signal(signal.SIGTERM, _sigterm)
    ordner = Path(a.arbeitsordner)
    ordner.mkdir(parents=True, exist_ok=True)
    stand_pfad = ordner / "stand.json"
    stand = json.loads(stand_pfad.read_text()) if stand_pfad.exists() else {
        "modell": MODELL, "anzahl": a.anzahl, "block": a.block, "batch": a.batch,
        "threads": a.threads, "naechster": 0,
        "bloecke": [], "starts": [],
    }
    stand["starts"].append({"zeit": time.time(), "pid": os.getpid(), "ab": stand["naechster"],
                            "systemlast_1min": round(os.getloadavg()[0], 2)})

    from fastembed import TextEmbedding
    t0 = time.perf_counter()
    modell = TextEmbedding(MODELL, threads=a.threads or None)
    stand["starts"][-1]["modell_laden_s"] = round(time.perf_counter() - t0, 3)

    texte = texte_laden(stand["anzahl"])
    print(f"[job {os.getpid()}] start bei {stand['naechster']}/{stand['anzahl']}", flush=True)

    while stand["naechster"] < stand["anzahl"]:
        i = stand["naechster"]
        teil = texte[i:i + stand["block"]]
        w0, c0 = time.perf_counter(), time.process_time()
        vek = np.array(list(modell.embed(teil, batch_size=stand.get("batch", 16))), dtype=np.float32)
        w1, c1 = time.perf_counter(), time.process_time()
        np.save(ordner / f"vektoren_{i:07d}.npy", vek)
        stand["naechster"] = i + len(teil)
        stand["bloecke"].append({
            "ab": i, "texte": len(teil), "ende_unix": time.time(),
            "wand_s": round(w1 - w0, 4), "cpu_s": round(c1 - c0, 4),
        })
        tmp = stand_pfad.with_suffix(".tmp")
        tmp.write_text(json.dumps(stand, indent=1))
        tmp.replace(stand_pfad)  # atomar: Checkpoint ist nie halb geschrieben
        print(f"[job {os.getpid()}] {stand['naechster']}/{stand['anzahl']} "
              f"({len(teil) / (w1 - w0):.0f} Texte/s)", flush=True)
        if aufhoeren:
            print(f"[job {os.getpid()}] Checkpoint bei {stand['naechster']}, beendet", flush=True)
            sys.exit(3)  # 3 = angehalten, nicht fertig

    stand["fertig_unix"] = time.time()
    stand_pfad.write_text(json.dumps(stand, indent=1))
    print(f"[job {os.getpid()}] fertig", flush=True)


if __name__ == "__main__":
    main()
