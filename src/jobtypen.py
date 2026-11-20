"""Jobtypen für den Scheduler, mit Herkunft jeder Zahl.

Erzeugt daten/jobtypen.json. Grundlage:
- Typ A aus der eigenen Messung (messungen/energie.json)
- Typ B aus MLPerf Inference v5.0, ID 5.0-0023 (daten/mlperf_power_datacenter.csv)
Skalierung auf den 1-kW-Referenzserver bei beiden gleich: energieproportional,
also gleiche Arbeit pro kWh wie gemessen.

Aufruf: python3 src/jobtypen.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_KW = 1.0


def typ_a():
    e = json.loads((ROOT / "messungen" / "energie.json").read_text())
    texte = 10_000_000
    kwh = texte / e["texte_pro_kwh"]
    return {
        "id": "A",
        "name": "Archiv-Embedding",
        "inhalt": f"{texte:,} Texte einbetten (Suchindex eines Dokumentenarchivs)".replace(",", "'"),
        "einheit": "Texte", "einheiten_pro_job": texte,
        "einheiten_pro_kwh": e["texte_pro_kwh"],
        "energie_kwh": round(kwh, 4),
        "laufzeit_min_1kw": round(kwh / SERVER_KW * 60, 1),
        "unterbrechbar": True,
        "unterbrechung": "Pause (SIGSTOP/SIGCONT) jederzeit, Stopp am Checkpoint alle 128 Texte",
        "frist_h": 24,
        "quelle_energie": f"eigene Messung, {e['leistung_quelle']}",
        "quelle_frist": "Annahme: nächtliche Neuberechnung; 74 % wiederkehrende Jobs im Alibaba-Trace",
        "real_lauffaehig": True,
    }


def typ_b():
    zeilen = list(csv.DictReader((ROOT / "daten" / "mlperf_power_datacenter.csv").open()))
    r = next(z for z in zeilen if z["ID"] == "5.0-0023" and z["Model"] == "retinanet"
             and z["Scenario"] == "Offline")
    bilder_s, watt = float(r["Performance_Result"]), float(r["Power_Result"])
    pro_kwh = bilder_s * 3600 / (watt / 1000)
    bilder = 1_000_000
    kwh = bilder / pro_kwh
    return {
        "id": "B",
        "name": "Bildanalyse-Batch",
        "inhalt": "1'000'000 Bilder auf Objekte prüfen (z. B. Inspektions- oder Kamerabilder eines Tages)",
        "einheit": "Bilder", "einheiten_pro_job": bilder,
        "einheiten_pro_kwh": round(pro_kwh),
        "energie_kwh": round(kwh, 4),
        "laufzeit_min_1kw": round(kwh / SERVER_KW * 60, 1),
        "unterbrechbar": False,
        "unterbrechung": "nicht innerhalb des Jobs (kurz, ohne Checkpoint), nur zwischen Jobs",
        "frist_h": 2,
        "quelle_energie": (f"MLPerf Inference v5.0, ID {r['ID']}, {r['System']}, RetinaNet Offline: "
                           f"{bilder_s:,.1f} Bilder/s bei {watt:,.0f} W (gemessen vom Einreicher)"),
        "quelle_frist": "Annahme: Ergebnisse werden am selben Morgen gebraucht",
        "real_lauffaehig": False,
    }


def main():
    typen = [typ_a(), typ_b()]
    aus = {
        "server_kw": SERVER_KW,
        "waermerueckgewinnung": 0.8,
        "skalierung": "energieproportional: Arbeit pro kWh wie gemessen bzw. wie bei MLPerf",
        "ankuenfte": "noch offen, wird im Scheduler festgelegt (Grundlage: Alibaba-Trace, "
                     "daten/ALIBABA_AUSWERTUNG.md)",
        "typen": typen,
    }
    (ROOT / "daten" / "jobtypen.json").write_text(json.dumps(aus, indent=1, ensure_ascii=False))
    for t in typen:
        print(f"{t['id']} {t['name']}: {t['energie_kwh']} kWh, {t['laufzeit_min_1kw']} min, "
              f"unterbrechbar={t['unterbrechbar']}, Frist {t['frist_h']} h, "
              f"{t['einheiten_pro_kwh']:,} {t['einheit']}/kWh")


if __name__ == "__main__":
    main()
