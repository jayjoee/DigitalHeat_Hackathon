"""Stundenprofil des Referenzhauses nach Case-Definition (DigitalHeat).

Heizbedarf pro Stunde = max(0, 10 kW * (20 - T) / 25.6), nur an Heiztagen.
Heiztag = lokaler Kalendertag (Europe/Zurich) mit Tagesmittel der Stundenwerte < 12 °C.
Warmwasser = 12 kWh pro Tag, gleichmässig auf 24 Stunden verteilt (0.5 kW).

Aufruf: python src/referenzprofil.py  -> daten/referenzprofil_2025.csv
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROH = ROOT / "daten" / "roh" / "openmeteo" / "basel_2025.csv"
AUS = ROOT / "daten" / "referenzprofil_2025.csv"

AUSLEGUNG_KW = 10.0
INNEN_C = 20.0
KONSTANTE = 25.6
HEIZGRENZE_C = 12.0
WARMWASSER_KWH_TAG = 12.0


def lesen():
    with ROH.open() as f:
        zeilen = f.read().splitlines()
    start = next(i for i, z in enumerate(zeilen) if z.startswith("time,"))
    leser = csv.DictReader(zeilen[start:])
    daten = []
    for r in leser:
        daten.append({
            "zeit": r["time"],
            "temp_c": float(r["temperature_2m (°C)"]),
            "globalstrahlung_wm2": float(r["shortwave_radiation (W/m²)"]),
        })
    return daten


def main():
    daten = lesen()
    pro_tag = defaultdict(list)
    for d in daten:
        pro_tag[d["zeit"][:10]].append(d["temp_c"])
    heiztag = {tag: sum(t) / len(t) < HEIZGRENZE_C for tag, t in pro_tag.items()}

    for d in daten:
        tag = d["zeit"][:10]
        d["heiztag"] = int(heiztag[tag])
        d["heizbedarf_kwh"] = (
            max(0.0, AUSLEGUNG_KW * (INNEN_C - d["temp_c"]) / KONSTANTE) if heiztag[tag] else 0.0
        )
        d["warmwasser_kwh"] = WARMWASSER_KWH_TAG / len(pro_tag[tag])

    AUS.parent.mkdir(parents=True, exist_ok=True)
    with AUS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(daten[0].keys()))
        w.writeheader()
        for d in daten:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()})

    heiz = sum(d["heizbedarf_kwh"] for d in daten)
    ww = sum(d["warmwasser_kwh"] for d in daten)
    print(f"Stunden: {len(daten)}, Tage: {len(pro_tag)}")
    print(f"Heiztage: {sum(heiztag.values())}")
    print(f"Kälteste Stunde: {min(d['temp_c'] for d in daten)} °C")
    print(f"Heizbedarf: {heiz:,.0f} kWh, Warmwasser: {ww:,.0f} kWh, total {heiz + ww:,.0f} kWh")
    print(f"Max. Heizleistung: {max(d['heizbedarf_kwh'] for d in daten):.2f} kW")


if __name__ == "__main__":
    main()
