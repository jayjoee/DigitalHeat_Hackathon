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
    "usd_chf": (0.84, "Mitte November 2026 ≈ 0,839 (tradingeconomics.com, therighttrader.com)"),
    # --- Wirtschaftlichkeit DigitalHeat (KOSTEN_DH.md, finale Fassung) ---
    "karten_pro_server": (8, "Einheitsserver: 8× NVIDIA L4 (72 W) + Host ≈ 1 kW"),
    "server_preis_chf": (32245, "Gigabyte G293-Z43 mit 16× L4, 2× EPYC 9335, 12× 32 GB: 76'774 $ (avadirect.com) "
                                "→ halbes System pro Server mit 8 L4, × 0,84 CHF/$"),
    "kuehlung_chf_pro_kw": (2520, "Flüssigkühlung 1'500–4'500 $/kW = 1'260–3'780 CHF (introl.com, servnetuk.com, stlpartners.com)"),
    "einbau_chf": (9000, "Schätzung: 30–60 h × 143,80 CHF/h (SAK) + Material 2'000–4'000 CHF"),
    "speicher_chf": (1800, "Pufferspeicher 900–1'110 € (klimaworld.com) plus Einbau"),
    "netzwerk_chf": (1200, "Firewall FortiGate 40F 441 CHF (boll.ch) plus Switch"),
    "abschreibung_jahre": (5, "Amazon 5 Jahre, Microsoft/Alphabet 6 Jahre für Server; 5 Jahre, weil GPUs schneller veralten"),
    "restwert_anteil": (0.20, "Tesla T4 nach ≈ 7 Jahren 22–25 % des Neupreises (amcompute.com)"),
    "zins": (0.045, "Schätzung: SARON ≈ 0 % + Bankmarge; Unternehmenskredite Euroraum 3,8 % (Bundesbank)"),
    "vertragspreis_chf_karte_h": (0.60, "Schweizer Cloud für Kunden mit Datenstandort Schweiz (Pharma, Banken, Spitäler): "
                                        "rund 12 % unter Schweizer GPU-Clouds (Hikube ≈ 0,68 CHF, Everyware 2,13 CHF pro L4-h); "
                                        "vorsichtiger Fall 0,50 CHF (PHARMA_SICHT.md, KOSTEN_DH.md)"),
    "anteil_fest_gebucht": (0.60, "Schätzung: Cloud-Kunden binden im Median 42 %, Ziel 70–80 % (FinOps-Vergleiche)"),
    "spotpreis_chf_karte_h": (0.294, "Füllaufträge zum L4-Spot-Preis (AWS g6 Spot 0,35–0,45 $ = 0,29–0,38 CHF)"),
    "spot_preisverfall": (0.10, "Annahme: Spot-Preis sinkt 10 % pro Jahr; H100-Index −23 % in einem Jahr (Silicon Data)"),
    "plattform_anteil": (0.05, "Direktvertrag mit eigener Plattform statt Marktplatz (15–30 %)"),
    "verfuegbarkeit": (0.993, "A100/H100-Knoten 99,3–99,4 % verfügbar (arXiv 2503.11901)"),
    "waermepreis_haushalt_chf_kwh": (0.0, "Gratiswärme im Öl-Pilot (CustomerView_Joel.md)"),
    "gpu_preis_chf": (2100, "L4 einzeln 2'000–3'000 $ = 1'680–2'520 CHF (jarvislabs.ai), für Ersatzteile"),
    "gpu_ausfall": (0.045, "Meta Llama 3: 6,1 %/Jahr bei 24/7-Training; bei halber Laufzeit 3–6,1 %; L4 3 Jahre Garantie"),
    "host_reparatur": (0.035, "Schätzung 2–5 % pro Jahr auf den Host-Anteil (35 % der Hardware), ab Jahr 2"),
    "einsaetze_chf_pro_8_server": (2600, "SAK: 281 CHF Einsatz, 143,80 CHF/h, 1,60 CHF/km; 2–5 Einsätze"),
    "service_hydraulik_chf": (390, "SAK-Serviceabo 275–500 CHF"),
    "kuehlservice_chf_pro_kw": (16.8, "20'000 $ pro MW und Jahr = 16,80 CHF pro kW (DC Market Insights via servnetuk.com)"),
    "monitoring_chf_pro_server_monat": (12.6, "Datadog Infrastructure Pro 15–18 $ = 12,60–15,10 CHF"),
    "internet_chf": (1600, "Init7 777 CHF/Jahr bis Swisscom Business 205 CHF/Monat"),
    "versicherung_anteil": (0.006, "Schätzung aus Hausratsätzen (≈ 0,8 ‰) mit Risikozuschlag; + 5 % Stempelabgabe"),
    "lizenz_chf": (450, "FortiGate-Schutzlizenz (boll.ch)"),
    "firmenanteil_chf": (1200, "Schätzung pro Haus bei rund 100 Häusern (ISO 27001, Personal, Haftpflicht)"),
    "kostensteigerung": (0.045, "Wartungsverträge 3–6 % pro Jahr (servnetuk.com)"),
    "gewinnsteuer": (0.1304, "Basel-Stadt, Gewinne unter 50 Mio. CHF (KPMG 2026)"),
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
