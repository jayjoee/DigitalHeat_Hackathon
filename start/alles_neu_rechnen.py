#!/usr/bin/env python3
"""Alle Ergebnisdateien, Wirtschaftszahlen und Dashboard-Daten neu erzeugen.

Nach jeder Änderung an src/scheduler/annahmen.py ausführen. Braucht nur Python, keine Zusatzpakete.
Die Flotte dauert am längsten (einige Minuten); mit --ohne-flotte wird sie übersprungen.

Nicht enthalten (eigene Umgebungen bzw. echte Läufe): ML-Untersuchung (start/ml_start.py),
Strategievergleich (start/vergleich_start.py), Serviceplanung (start/service_start.py), Live-Läufe.

Aufruf:
  python3 start/alles_neu_rechnen.py
  python3 start/alles_neu_rechnen.py --ohne-flotte
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERG = "daten/ergebnisse"

# (Beschreibung, Befehl, Datei für die Standardausgabe oder None). Reihenfolge zählt:
# kosten_dh liest zusage_8_spot.json, die Dashboards lesen die Ergebnisdateien.
SCHRITTE = [
    ("Referenzhaus 8 Server", ["src/scheduler/jahr.py", "--server", "8", "--stunden", f"{ERG}/stunden_8_spot.csv"],
     f"{ERG}/bilanz_8_spot.json"),
    ("Serverzahl 1–13, beide Nachfrageszenarien", ["src/scheduler/jahr.py"], None),
    ("Leerlauf und Abschalten", ["-m", "src.scheduler.serverbetrieb", "--ausgabe", f"{ERG}/serverbetrieb.json"], None),
    ("Zusage am Vortag", ["src/scheduler/zusage.py"], None),
    ("Flotte im Abschaltmodell", ["src/scheduler/flotte.py", "--abschalten"], None),
    ("Flotte im Idealmodell", ["src/scheduler/flotte.py"], None),
    ("Zahlen für KOSTEN_DH.md", ["src/kosten_dh.py"], None),
    ("Firmenrechnung", ["src/firma.py"], None),
    ("Ressourcen-Warteschlange", ["start/queue_start.py"], None),
    ("Dashboard-Daten", ["src/dashboard_daten.py"], None),
    ("Dashboard als Einzeldatei", ["src/artifact_bauen.py"], None),
    ("3D-Dashboard-Daten", ["src/dashboard3d_daten.py"], None),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ohne-flotte", action="store_true", help="Flottenläufe überspringen (dauern am längsten)")
    args = ap.parse_args()
    fehler = []
    for name, befehl, ausgabe in SCHRITTE:
        if args.ohne_flotte and "flotte.py" in befehl[0]:
            print(f"übersprungen  {name}")
            continue
        t0 = time.time()
        print(f"läuft        {name} …", flush=True)
        r = subprocess.run([sys.executable, *befehl], cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0 and ausgabe:
            (ROOT / ausgabe).write_text(r.stdout, encoding="utf-8")
        status = "fertig" if r.returncode == 0 else "FEHLER"
        print(f"{status:12s} {name} ({time.time() - t0:.0f} s)", flush=True)
        if r.returncode:
            fehler.append(name)
            print((r.stderr or r.stdout).strip()[-2000:], file=sys.stderr)
    print()
    if fehler:
        print("Fehlgeschlagen: " + ", ".join(fehler))
        sys.exit(1)
    print("Alles neu erzeugt. Danach prüfen:")
    print("  python3 -m unittest discover -s tests")
    print("Ändern sich Preise oder Kosten, schlagen die Geld-Referenzwerte in tests/test_scheduler.py und")
    print("tests/referenz_haus8.json fehl. Sie sind dann nachzuführen; die simulierten Stunden bleiben gleich.")
    print("Die Texte in docs/wirtschaft/KOSTEN_DH.md und docs/ergebnisse/ERGEBNISSE.md von Hand abgleichen")
    print(f"(Zahlen in {ERG}/kosten_dh.json).")


if __name__ == "__main__":
    main()
