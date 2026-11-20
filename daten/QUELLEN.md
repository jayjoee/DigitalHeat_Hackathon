# Datenquellen (abgerufen 20.11.2026)

## Wetter Basel 2025 – Open-Meteo Historical Weather API
- Datei: `roh/openmeteo/basel_2025.csv` (8'760 Stunden)
- Abruf: `https://archive-api.open-meteo.com/v1/archive?latitude=47.56&longitude=7.59&start_date=2025-01-01&end_date=2025-12-31&hourly=temperature_2m,shortwave_radiation,direct_radiation,diffuse_radiation&timezone=Europe%2FZurich&format=csv`
- Open-Meteo liefert den Gitterpunkt 47.557 N, 7.549 E, 247 m ü. M.
- Abgeleitet: `referenzprofil_2025.csv` über `src/referenzprofil.py`
  - 206 Heiztage, kälteste Stunde −5,6 °C, Spitze 10,0 kW
  - Heizbedarf 26'851 kWh, Warmwasser 4'380 kWh (12 kWh/Tag, gleichmässig 0,5 kW), total 31'231 kWh
  - Stimmt mit dem Case überein (≈ 27'000 kWh, 206 Tage). Mit dem offiziellen CSV des Case abgleichen, sobald es vorliegt.

## Strompreis – ElCom 2026, IWB Basel, Kategorie H4
- Datei: `roh/elcom/iwb_h4_2026.json`
- Abruf: GraphQL `https://www.strompreis.elcom.admin.ch/api/graphql`, `observations`, Filter period 2026, category H4, operator 624 (IWB Industrielle Werke Basel)
- Rp./kWh: **Total 33,25** = Energie 10,892 + Netznutzung 11,414 + Abgaben 7,443 + Netzzuschlag 2,3 + Rest 1,2 (vermutlich Messtarif, nicht abgefragt)
- Gleicher Preis für Basel, Riehen und Bettingen
- Wärmewert nach Case: 33,25 ÷ 2,5 = **13,3 Rp./kWh**
- Offen: Ob der Total-Preis die MwSt. enthält, ist auf der ElCom-Seite zu prüfen.

## MLPerf Inference (MLCommons) – Leistungsmessungen
- Dateien: `roh/mlperf/summary_results_v5.0.json`, `_v5.1.json`, `_v6.0.json` (aus `https://raw.githubusercontent.com/mlcommons/inference_results_vX/main/summary_results.json`, wegen der Grösse nicht im Repository, der Auszug schon)
- Auszug: `mlperf_power_datacenter.csv` mit 31 Datacenter-Ergebnissen mit Leistungsmessung (v6.0 enthält keine)
- Brauchbar für Jobtypen, Offline-Szenario:
  - Whisper (Transkription): 8× B200, 43'699 Samples/s bei 7'636 W (v5.1, Lenovo)
  - RetinaNet (Bilderkennung): 8× H100 NVL, 11'106 Samples/s bei 4'849 W (v5.0, Fujitsu)
  - Llama 3.1 8B (Text): 8× B200, 146'960 Tokens/s bei 9'436 W (v5.1)
  - Stable Diffusion XL (Bilderzeugung): 8× B200, 32 Samples/s bei 9'514 W (v5.1)
- Achtung: ganze 8-GPU-Systeme mit 5–10 kW, auf den 1-kW-Referenzserver skalieren.

## Alibaba PAI GPU Cluster Trace 2020
- Dateien: `roh/alibaba/` – job, task, group_tag, machine_spec, sensor (CSV ohne Kopfzeile, Spalten im README des Repos)
- Quelle: `https://aliopentrace.oss-cn-beijing.aliyuncs.com/v2020GPUTraces/`, SHA-256 gegen das README geprüft, alle fünf stimmen
- Auswertung: `ALIBABA_AUSWERTUNG.md` (Skript `src/alibaba_analyse.py`)
- Nicht geladen: instance (663 MB), machine_metric (198 MB), nur bei Bedarf nachladen
- Zweck laut Case: Inspiration für Jobdauern und Ressourcenanfragen
- Zitieren: Weng et al., «MLaaS in the Wild», NSDI ’22

## Noch offen
- Offizielles Referenzprofil-CSV von DigitalHeat
- Cloud-Preise siehe `PREISE.md` (Hardwarekosten und Wechselkurs noch offen)
- Gaspreise (Quelle in NOTIZEN.md abgeschnitten)
