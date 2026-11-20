"""Bereitet alle Zahlen fürs Dashboard auf → dashboard/daten.js (window.DATEN = …).

Rechnet jede Kombination aus Serverzahl (1–13), Nachfrage (spot, alibaba) und Regel
(rechnen, abgeben) mit derselben Jahressimulation wie die Bilanz und speichert:
Jahreskennzahlen, Monatswerte und die Stundenwerte von zwei Beispieltagen.

Aufruf: python3 src/dashboard_daten.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.jahr import Haus, profil_laden  # noqa: E402

ROOT = A.ROOT
TAGE = {"januar": "2025-01-15", "juli": "2025-07-15"}


def main():
    profil = profil_laden()
    laeufe = {}
    for sz in ("spot", "alibaba"):
        for regel in ("rechnen", "abgeben"):
            for n in range(1, 14):
                haus = Haus(n, sz, regel, profil)
                monate = defaultdict(lambda: defaultdict(float))
                tage = {k: [] for k in TAGE}
                for h in range(len(profil)):
                    z = haus.schritt(h)
                    m = monate[z["zeit"][:7]]
                    for k in ("bedarf_kwh", "genutzt_kwh", "backup_kwh", "abgefuehrt_kwh", "strom_kwh"):
                        m[k] += z[k]
                    m["stunden"] += 1
                    for name, tag in TAGE.items():
                        if z["zeit"].startswith(tag):
                            tage[name].append({k: z[k] for k in (
                                "zeit", "temp_c", "bedarf_kwh", "heizung_kwh", "warmwasser_kwh",
                                "waerme_kwh", "genutzt_kwh", "speicher_kwh", "abgefuehrt_kwh",
                                "backup_kwh", "server_laufend")})
                b = haus.bilanz()
                b["strom_kwh"] = round(haus.z["strom"], 1)
                b["genutzt_kwh_genau"] = round(haus.z["genutzt"], 1)
                laeufe[f"{sz}|{regel}|{n}"] = {
                    "bilanz": b,
                    "monate": [{"monat": k, **{kk: round(vv, 1) for kk, vv in v.items()}}
                               for k, v in sorted(monate.items())],
                    "tage": tage,
                }
    daten = {"erzeugt": "python3 src/dashboard_daten.py", "annahmen": A.als_liste(),
             "tage": TAGE, "laeufe": laeufe}
    aus = ROOT / "dashboard" / "daten.js"
    aus.write_text("window.DATEN = " + json.dumps(daten, ensure_ascii=False) + ";\n")
    print(f"{aus.relative_to(ROOT)}: {len(laeufe)} Läufe, {aus.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
