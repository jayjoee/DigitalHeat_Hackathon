"""Alle Annahmen an einem Ort, jede mit Herkunft. Die Ergebnisdateien enthalten diese Liste."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_jobs = json.loads((ROOT / "daten" / "jobtypen.json").read_text())
_typ = {t["id"]: t for t in _jobs["typen"]}

ANNAHMEN = {
    # --- Server und Haus (Case) ---
    "server_kw": (1.0, "Case: 1 kW Strom pro Rack-Server"),
    "waermerueckgewinnung": (0.8, "Case: 80 % der Wärme ins Wassersystem"),
    "speicher_kwh": (35.0, "Case: 1'000 l, 30 K Spreizung, verlustfrei"),
    "profil": ("daten/referenzprofil_2025.csv", "Case-Formel, Open-Meteo Basel 2025, src/referenzprofil.py"),
    # --- Preise ---
    "strompreis_chf_kwh": (0.3325, "ElCom 2026, IWB Basel, H4, Total (daten/roh/elcom/iwb_h4_2026.json)"),
    "waermewert_chf_kwh": (0.3325 / 2.5, "Case: Strompreis ÷ 2,5 (ersetzt Wärmepumpe mit JAZ 2,5)"),
    "usd_chf": (0.84, "Angabe Joël, 20.11.2026: 1 USD = 0,84 CHF"),
    "rechenpreis_usd_server_h": (1.26, "Spot H100 0,79 $/GPU-h × 1,6 GPU pro kW (daten/PREISE.md), untere Spanne"),
    # --- Jobs ---
    "job_a_kwh": (_typ["A"]["energie_kwh"], _typ["A"]["quelle_energie"]),
    "job_a_frist_h": (_typ["A"]["frist_h"], _typ["A"]["quelle_frist"]),
    "job_b_kwh": (_typ["B"]["energie_kwh"], _typ["B"]["quelle_energie"]),
    "job_b_frist_h": (_typ["B"]["frist_h"], _typ["B"]["quelle_frist"]),
    # --- Nachfrage (Alibaba-Trace, daten/ALIBABA_AUSWERTUNG.md) ---
    "nachfrage_server_h_pro_server_tag": (
        10.1, "Alibaba: 68'083 GPU-h/Tag auf 6'742 GPUs = 10,1 h pro GPU und Tag (42 % der Kapazität); "
              "1 Server ≈ 1,6 GPU, gleiche Auslastung angenommen"),
    "anteil_kurze_jobs_gpu_h": (0.06, "Alibaba: Jobs < 1 h tragen 6 % der GPU-Stunden → Typ B"),
    "ankunft_stundenprofil": ("Alibaba UTC+8, unverändert als Tagesform übernommen",
                              "daten/alibaba_auswertung.json, ankunft_stunde_utc8_anteil"),
    "zufallssaat": (2025, "fest, damit jeder Lauf dieselben Ankünfte erzeugt"),
}


def wert(name):
    return ANNAHMEN[name][0]


def als_liste():
    return {k: {"wert": v, "quelle": q} for k, (v, q) in ANNAHMEN.items()}


def stundenprofil():
    p = json.loads((ROOT / "daten" / "alibaba_auswertung.json").read_text())["ankunft_stunde_utc8_anteil"]
    werte = [p[f"{h}.0"] if f"{h}.0" in p else p[str(h)] for h in range(24)]
    s = sum(werte)
    return [w / s for w in werte]
