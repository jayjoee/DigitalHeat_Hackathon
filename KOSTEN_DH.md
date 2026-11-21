# Kosten und Variablen aus Sicht DigitalHeat (Recherche 21.11.2026)

**Zielgruppe:** Häuser mit **Gasheizung**, die bis 2037 umstellen müssen. Den Gaspreis und damit den Wert der Wärme liefert Joël. Bis dahin steht der Wärmeerlös hier als Variable (`p_W`). Er macht ohnehin nur wenige Prozent der Einnahmen aus.

**Grundlage:** ein Haus mit 8 kW Servern, wärmegeführt, **36'290 Server-Stunden** und **29'027 kWh genutzte Wärme** pro Jahr (Jahressimulation, Referenzhaus 2025). Server werden ausgeschaltet, wenn keine Wärme gebraucht wird.

**Einheitsserver:** 8× NVIDIA L4 (72 W) plus Host mit 2 CPUs, ≈ 1 kW. **Pro Haus 8 Server = 64 L4-Karten.**

**Qualität:** **Q** = Quelle · **CH** = Schweizer Preisliste · **D** = nur ausländische oder Branchenwerte, Offerte nötig · **A** = keine Quelle, eigene Annahme mit Spanne · **E** = Entscheid im Team

---

## 1. Die Formel

```
Gewinn pro Haus und Jahr
  = Erlös Rechnen + Erlös Wärme − Strom − Kapitalkosten − laufende Kosten − Firmenanteil

Erlös Rechnen   = H × k × p_GPU × Kurs × (1 − g)
Erlös Wärme     = Q × p_W                 p_W = Gaspreis ÷ η_Kessel × (1 − Rabatt)   ← Joël
Strom           = H × p_S  (+ Leerlauf, falls Server nicht ausgeschaltet)
Kapitalkosten   = Investition × Annuität(i, J)
laufende Kosten = Ersatzteile + Störungseinsätze + Kühl- und Hydraulikservice
                  + Monitoring + Internet + Versicherung
```

**Nötiger Mietpreis pro Karten-Stunde** (Break-even):

```
p_GPU* = (Strom + Kapitalkosten + laufende Kosten + Firmenanteil − Erlös Wärme)
         ÷ (H × k × Kurs × (1 − g))
```

## 2. Alle Variablen

### Haus und Wärme

| Symbol | Bedeutung | Wert / Spanne | Qualität | Quelle |
|---|---|---|---|---|
| Q | genutzte Serverwärme pro Jahr | 29'027 kWh | Q | Jahressimulation (Case-Formel, Basel 2025) |
| H | Server-Stunden pro Jahr (= kWh Strom) | 36'290 | Q | Jahressimulation |
| η | nutzbarer Anteil der Wärme | 0,8 | Case | Case |
| Speicher | Wärmespeicher | 35 kWh | Case | Case |
| Gaspreis | Preis pro kWh Gas | **von Joël** | – | – |
| η_Kessel | Wirkungsgrad der bisherigen Gasheizung | **von Joël** | – | – |
| Rabatt | wie viel günstiger DH die Wärme verkauft | 10–20 % | E | Vorschlag, damit der Hausbesitzer wechselt |

### Strom

| Symbol | Bedeutung | Wert / Spanne | Qualität | Quelle |
|---|---|---|---|---|
| p_S | Strompreis | 33,25 Rp./kWh | Q | ElCom 2026, IWB H4 (C2 Kleingewerbe: 32,745) |
| f_Leer | Leerlaufverbrauch eines pausierten Servers | ≈ 23 % der Last, **0 wenn ausgeschaltet** | Q | Latif et al. 2024 (1,86 kW Leerlauf, 7,92 kW Last) |

### Rechnen (Erlös)

| Symbol | Bedeutung | Wert / Spanne | Qualität | Quelle |
|---|---|---|---|---|
| k | Karten pro Server | 8 | Q/A | 8 × 72 W = 576 W GPU (NVIDIA), mit Host ≈ 1 kW |
| p_GPU | Mietpreis pro L4-Stunde | 0,35–0,87 $ | Q | AWS Spot g6 (Joëls Preisliste), Median On-Demand 0,87 $ (getdeploying.com) |
| Kurs | CHF pro $ | 0,84 | Q | Mitte November 2026 ≈ 0,839 |
| g | Marktplatzgebühr | 15–30 % | D | Vast.ai: widersprüchliche Angaben (miningboard.com, deploybase.ai) |

### Investition pro Haus (einmalig)

| Posten | Wert / Spanne | Qualität | Quelle |
|---|---|---|---|
| L4-Karte | 2'000–3'000 $ × 64 | Q | jarvislabs.ai, gpupoet.com |
| Host pro Server | 10'000–20'000 $ × 8 | D/A | Barebone 6'438–9'527 $ (sabrepc.com, newegg.com), CPUs, RAM und SSD angenommen |
| Flüssigkühlung | 1'500–4'500 $ pro kW × 8 | D | introl.com, servnetuk.com, stlpartners.com |
| Pufferspeicher 1'000 l | ≈ 900–1'110 € (Gerät) | D | klimaworld.com |
| Einbau (Wärmetauscher, Hydraulik, Elektro, Planung) | 5'000–10'000 CHF | A | 30–60 h, kein Schweizer Stundensatz gefunden |
| Hausanschluss verstärken (falls nötig) | 1'000–3'000 € | D | adac.de. Einfamilienhaus meist 24–43 kW, 8 kW passen meist |
| Lecksensoren (2–3 Stück) | ≈ 24 CHF pro Stück | CH | hornbach.ch |
| J | Abschreibung | 5 Jahre | E | Hyperscaler 5–6 Jahre |
| i | Zins | 3–6 % | A | SNB-Leitzins 0 % (24.09.2026), KMU-Kreditzins nicht gefunden |

### Laufende Kosten pro Haus (jedes Jahr)

| Posten | Wie gerechnet | Spanne pro Jahr | Qualität | Quelle |
|---|---|---|---|---|
| **GPU-Ersatz** | Ausfallrate × 64 Karten × Kartenpreis | 3,8k–11,5k $ | Q | Meta Llama 3 (16'384 H100, 54 Tage): 148 defekte GPUs → **6,1 % pro Jahr**, alle GPU-Gründe 10,8 %. Bei DH (halbe Laufzeit, Inferenz) vermutlich weniger: 3–6,1 % angesetzt |
| **Host-Reparaturen** | 2–5 % des Hostwerts | 1,6k–8k $ | A | kein Wert gefunden |
| **Störungseinsätze** | Anzahl × (Pauschale + Stunden + Fahrt) | 1'100–4'200 CHF | CH | SAK-Preisblatt: Einsatz 281 CHF, 143,80 CHF/h, 1,60 CHF/km. Annahme 2–5 Einsätze, 1,5–3 h, 20–40 km |
| **Service Flüssigkühlung** | ≈ 20 $ pro kW | ≈ 130 CHF | D | DC Market Insights via servnetuk.com: 20'000 $ pro MW und Jahr, jährlicher Labortest der Kühlflüssigkeit |
| **Service Hydraulik/Wärme** | Serviceabo wie bei einer Wärmepumpe | 275–500 CHF | CH | SAK Serviceverträge Wärmepumpe |
| **Monitoring** | Software pro Server | 0–1'450 CHF | Q | Datadog Pro 15–18 $ pro Host und Monat, oder Gratis-Software (0) |
| **Internet** | Geschäftsanschluss | 800–2'460 CHF | CH | Init7 Fiber7 777 CHF/Jahr, Swisscom Business 150–205 CHF/Mt. |
| **Versicherung** (Feuer, Wasser, Diebstahl, Elektronik) | Satz × Neuwert + 5 % Stempelabgabe | 900–4'700 CHF | A | Versicherer veröffentlichen keine Sätze (Zurich, AXA, Mobiliar). Annahme 0,5–1,5 % des Neuwerts. Stempelabgabe 5 % (mobiliar.ch) |
| *Alternative: Wartungsvertrag beim Hersteller* | 5–15 % des Hardwarewerts | 8,7k–44k CHF | D | OEM 8–15 %, nach Jahr 5 bis 30 % (icd3s.com), Drittanbieter 30–40 % günstiger (parkplacetechnologies.com) |

### Firmenkosten von DH (auf alle Häuser verteilt)

| Posten | Spanne | Qualität | Quelle |
|---|---|---|---|
| Betriebshaftpflicht | keine KMU-Zahl gefunden. Berufshaftpflicht als Untergrenze: 200–1'500 CHF/Jahr | D | hellosafe.ch. AXA: Prämie hängt von Umsatz und Versicherungssumme ab, **Offerte nötig** |
| Cyberversicherung | keine Schweizer Zahl gefunden | – | Nur 5–10 % der Schweizer KMU haben eine (SVV, Presse). VZ-Studie Oktober 2026 prüfen |
| ISO 27001 | Jahr 1: 25'000–60'000 €, danach 8'000–20'000 €/Jahr | D | orbiqhq.com, secjur.com |
| Personal, Vertrieb, Plattform | 500–2'000 CHF pro Haus | A | hängt von der Zahl der Häuser ab |

## 3. Was ein Haus pro Jahr kostet (ohne Wärmeerlös)

| | Günstig | Teuer |
|---|---|---|
| Hardwarewert (64 L4 + 8 Hosts) | 174'700 CHF | 295'700 CHF |
| Investition gesamt (mit Kühlung, Speicher, Einbau) | 191'000 CHF | 338'000 CHF |
| Strom | 12'100 | 12'100 |
| Kapitalkosten (5 Jahre, 3 % bzw. 6 %) | 41'700 | 80'300 |
| GPU-Ersatz und Host-Reparaturen | 4'600 | 16'600 |
| Störungseinsätze | 1'100 | 4'200 |
| Service Kühlung und Hydraulik | 400 | 600 |
| Monitoring | 0 | 1'500 |
| Internet | 800 | 2'500 |
| Versicherung | 900 | 4'700 |
| Firmenanteil | 500 | 2'000 |
| **Kosten pro Haus und Jahr** | **≈ 62'100 CHF** | **≈ 124'400 CHF** |
| Marktplatzgebühr | 15 % | 30 % |
| **Nötiger Mietpreis pro L4-Stunde** (ohne Wärmeerlös) | **0,30 $** | **0,73 $** |

Selbst warten mit eigenem Ersatzteillager ist deutlich günstiger als ein Herstellervertrag: 7'800–30'000 CHF statt 10'900–53'600 CHF pro Haus und Jahr.

**Der Markt zahlt heute 0,35–0,87 $ pro L4-Stunde.** Im günstigen Fall geht es auf, im teuren nicht. Der Wärmeerlös aus Gas senkt den nötigen Preis noch etwas, sobald Joëls Zahlen da sind.

## 4. Was am meisten bewegt (in dieser Reihenfolge)

1. **Mietpreis pro GPU-Stunde und Marktplatzgebühr**: bis 120'000 CHF Unterschied pro Haus und Jahr zwischen den Szenarien.
2. **Hardwarepreis und Zins**: Die Kapitalkosten liegen bei 41'700–80'300 CHF pro Jahr.
3. **Wartungsmodell**: selbst warten oder Herstellervertrag, bis zu 23'000 CHF Unterschied.
4. **Versicherung**: 900–4'700 CHF, ohne Offerte nicht genauer.
5. **Strom**: mit 12'100 CHF fix, solange die Server ausgeschaltet werden.
6. **Wärmeerlös (Gas)**: vermutlich einige tausend Franken, entscheidet nicht.

## 5. Offerten, die die Zahlen genau machen

| Was | Bei wem |
|---|---|
| Komplette Server-Konfiguration 8× L4 | Supermicro- oder Dell-Partner (Broadberry, Sabre PC) |
| Einbau Wärmetauscher und Hydraulik | Heizungsinstallateur in Basel |
| Inventar- und Elektronikversicherung, Betriebshaftpflicht | Zurich, Mobiliar, AXA, Helvetia |
| Cyberversicherung | dieselben, plus VZ-Studie Oktober 2026 |
| Business-Internet | Init7, Swisscom |
| Kreditzins | Hausbank |

## Quellen

- Leerlauf: https://arxiv.org/html/2412.08602v2
- GPU-Ausfälle: Meta, The Llama 3 Herd of Models, https://arxiv.org/pdf/2407.21783 (Tabelle 5), Zusammenfassung https://www.tomshardware.com/tech-industry/artificial-intelligence/faulty-nvidia-h100-gpus-and-hbm3-memory-caused-half-of-the-failures-during-llama-3-training-one-failure-every-three-hours-for-metas-16384-gpu-training-cluster; Verfügbarkeit A100/H100: https://arxiv.org/html/2503.11901v4
- Wartungsverträge: https://icd3s.com/blog/third-party-server-maintenance-vs-oem-contracts-cost-savings/, https://www.parkplacetechnologies.com/third-party-maintenance/server-maintenance/, https://www.verifiedmarketresearch.com/blog/how-much-does-thirdparty-maintenance-cost-for-servers-and-storage/
- Flüssigkühlung: https://www.servnetuk.com/insights/liquid-cooling-maintenance-requirements, https://introl.com/blog/direct-to-chip-cooling-pue-below-12-implementation, https://www.servnetuk.com/learn/direct-to-chip-liquid-cooling-explained, https://stlpartners.com/press/liquid-cooling-retrofits-can-cost-roughly-80-less/
- Service und Einsätze: https://www.sak.ch/downloads/waerme/wartung-und-service/sak_preisblatt-wartung_waermepumpen_01_06.pdf
- Monitoring: https://www.datadoghq.com/pricing/list/
- Versicherung: https://www.zurich.ch/de/firmenkunden/sach-cyber/sachversicherung/technische-versicherung/maschinenversicherung-und-elektronikversicherung, https://www.mobiliar.ch/ratgeber/richtige-versicherungssumme-im-kmu, https://www.axa.ch/de/unternehmenskunden/angebote/haftung/betriebshaftpflichtversicherung.html, https://hellosafe.ch/de/berufshaftpflichtversicherung/kosten, https://www.netzwoche.ch/news/2026-04-14/markt-fuer-cyberversicherungen-boomt
- Lecksensor: https://www.hornbach.ch/de/p/aeotec-wasser-leck-sensor-kompatibel-mit-smart-home-by-hornbach/10470627/
- L4: https://jarvislabs.ai/blog/l4-gpu-price, https://gpupoet.com/gpu/learn/price/july-2026/nvidia-l4, https://getdeploying.com/gpus/nvidia-l4, https://www.nvidia.com/en-us/data-center/l4/
- Server-Barebone: https://www.newegg.com/p/N82E16816139439, https://www.sabrepc.com/SYS-421GE-TNRT3-Supermicro-S148070641
- Pufferspeicher: https://www.klimaworld.com/products/schichten-pufferspeicher-klimaworld-1000-liter
- Hausanschluss: https://www.adac.de/rund-ums-haus/energie/versorgung/stromanschluss-beantragen/, https://www.photovoltaik.info/hausanschluss-pv-speicher-wallbox-waermepumpe/
- Internet: https://www.swisscom.ch/de/business/kmu/internet-festnetz-fernsehen/angebote/business-internet-services.html, https://www.init7.net/en/offer/business-internet
- Marktplatzgebühr: https://miningboard.com/guides/vast-runpod-io-net-comparison, https://deploybase.ai/articles/vast-ai-pricing
- ISO 27001: https://www.orbiqhq.com/de/compliance-automatisierung/iso-27001-zertifizierung-kosten, https://www.secjur.com/blog/iso-27001-kosten
- Leitzins: https://www.snb.ch/de/publications/communication/press-releases-restricted/pre_20260924
