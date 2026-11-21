# Kosten und Wirtschaftlichkeit aus Sicht DigitalHeat – finale Fassung (21.11.2026)

Säule «Firma». Ergänzt Joëls Kundensicht (`CustomerView_Joel.md`) und die Pharma-Sicht (`PHARMA_SICHT.md`). Frühere Zwischenstände stehen in der Git-Historie.

## Kurzfassung

| | Referenzhaus (31'231 kWh) | Durchschnitts-EFH (17'000 kWh) |
|---|---|---|
| Server (kW) | **8** | **4** (Team-Ziel 93 %) oder 5 (Joël, 99,6 %) |
| Wärmedeckung | 92,95 % | 93,6 % / 99,6 % |
| Investition DH | **290'100 CHF** | 151'100 / 185'800 CHF |
| Wärme an den Haushalt | gratis | gratis |
| Ergebnis DH pro Jahr (Vertragspreis 0,50 $, 60 % fest gebucht) | **+8'800 CHF** | +5'000 / +300 CHF |
| **Nötiger Vertragspreis (Break-even)** | **0,43 $ pro L4-Stunde** | 0,43 / 0,50 $ |
| Was Pharma heute in der Cloud zahlt | 0,63–0,65 $ (fester Vertrag), 0,71–0,80 $ (auf Abruf) | gleich |

**In einem Satz:** Mit einem Pharma-Vertrag zu 0,50 $ pro L4-Stunde, von dem 60 % fest gebucht sind, verdient DH beim Referenzhaus rund 8'800 CHF pro Jahr und kann dem Haushalt die Wärme gratis geben. Die Grenze liegt bei 0,43 $ (Spanne 0,31–0,66 $), die Cloud verlangt für dasselbe 0,63–0,80 $.

Ergebnis = Gewinn nach Steuern, Jahresmittel über 5 Jahre (abgezinst), mit Preisverfall, Garantie, Restwert und Preissteigerung.

---

## 1. Die Formel

```
Gewinn pro Haus und Jahr = Erlös Rechnen + Erlös Wärme − Strom − laufende Kosten − Steuern
                           − (Investition − Restwert) verteilt auf 5 Jahre inkl. Zins

Erlös Rechnen = Server-Stunden × 8 Karten × Kurs × (1 − Plattform) × Verfügbarkeit
                × [Anteil fest gebucht × Vertragspreis + Rest × Spot-Preis]

Break-even    = der Vertragspreis, bei dem der Gewinn genau 0 ist
```

## 2. Finale Annahmen

**Qualität:** **Q** = Quelle · **CH** = Schweizer Preisliste · **D** = ausländische oder Branchenwerte · **S** = Schätzung aus Vergleichswerten (Herleitung in Abschnitt 2b) · **E** = Entscheid im Team

### Haus und Betrieb

| Variable | Final | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| Server-Stunden Referenzhaus | 36'290 h | – | Q | Jahressimulation Basel 2025 |
| Genutzte Wärme | 29'027 kWh | – | Q | Jahressimulation |
| Server ausschalten statt pausieren | ja | – | E | sonst +23 % Leerlaufstrom (Latif et al. 2024) |
| Strompreis | 33,25 Rp./kWh | – | Q | ElCom 2026, IWB H4 |
| Wärme an den Haushalt | **gratis** | 0–7 Rp./kWh | E | Joëls Pilot-Modell |
| Verfügbarkeit | 99,3 % | – | Q | arXiv 2503.11901 |

### Investition (einmalig)

| Variable | Final | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| **Server mit 8 L4 inkl. CPU, RAM, SSD** | **38'400 $ = 32'200 CHF** | ±15 % | Q | Konfigurierter Preis Gigabyte G293-Z43: 16× L4, 2× EPYC 9335, 12× 32 GB, **76'774 $** (avadirect.com) → halbes System pro 8 L4 |
| Flüssigkühlung | 3'000 $ pro kW | 1'500–4'500 $ | D | introl.com, servnetuk.com, stlpartners.com |
| **Einbau** (Wärmetauscher, Hydraulik, Elektro) | **9'000 CHF** | 6'400–12'800 | S | 30–60 h × 143,80 CHF/h (SAK) + Material 2'000–4'000 CHF |
| Pufferspeicher | 1'800 CHF | 1'200–2'500 | D | 900–1'110 € Gerät (klimaworld.com) plus Einbau |
| Netzwerk (Firewall, Switch) | 1'200 CHF | 800–1'600 | Q/S | FortiGate 40F 441 CHF (boll.ch) |
| Abschreibung | 5 Jahre | – | E | Hyperscaler 5–6 Jahre |
| Restwert nach 5 Jahren | 20 % | 15–30 % | Q/S | Tesla T4 nach ≈ 7 Jahren 22–25 % des Neupreises (amcompute.com) |
| **Zins** | **4,5 %** | 3,5–5,5 % | S | SARON ≈ 0 % + Bankmarge; siehe Abschnitt 2b |

### Laufende Kosten (pro Jahr, Referenzhaus)

| Variable | Final | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| Strom | 12'066 CHF | – | Q | 36'290 kWh × 33,25 Rp. |
| GPU-Ersatz (ab Jahr 4, vorher Garantie) | 4,5 % der Karten pro Jahr | 3–6,1 % | Q | Meta Llama 3: 6,1 %/Jahr bei 24/7-Training; L4 3 Jahre Garantie (shi.com) |
| Host-Reparaturen (ab Jahr 2) | 3,5 % des Hostwerts | 2–5 % | S | Supermicro: 1 Jahr Teile, 3 Jahre Arbeit |
| Störungseinsätze | 2'600 CHF | 1'100–4'200 | CH | SAK: 281 CHF Pauschale, 143,80 CHF/h, 1,60 CHF/km |
| Service Kühlung + Hydraulik | 520 CHF | 400–630 | CH/D | SAK-Serviceabo; 20 $/kW Kühlservice |
| Monitoring | 1'200 CHF | 0–1'450 | Q | Datadog 15–18 $ pro Server und Monat |
| Internet | 1'600 CHF | 800–2'460 | CH | Init7, Swisscom Business |
| **Versicherung** | **0,6 % des Hardwarewerts + 5 % Stempel = 1'600 CHF** | 0,3–1,0 % | S | siehe Abschnitt 2b |
| Netzwerk-Lizenz | 450 CHF | 300–600 | Q | boll.ch |
| Firmenanteil (Personal, Vertrieb, ISO 27001, Haftpflicht) | 1'200 CHF | 500–2'000 | S/D | ISO 27001: 25'000–60'000 € im 1. Jahr, danach 8'000–20'000 € (orbiqhq.com); Haftpflicht 200–1'500 CHF/Jahr (hellosafe.ch) |
| Preissteigerung laufende Kosten | 4,5 % pro Jahr | 3–6 % | D | servnetuk.com |
| Gewinnsteuer | 13,04 % | – | Q | Basel-Stadt (KPMG 2026) |

### Erlös (aus `PHARMA_SICHT.md`)

| Variable | Final | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| **Vertragspreis Pharma** | **0,50 $ pro L4-Stunde** | 0,45–0,55 $ | Q/E | 15–20 % unter Cloud mit festem Vertrag (Google Cloud L4 1 Jahr 0,65 $, 3 Jahre 0,63 $; AWS L4 auf Abruf 0,80 $) |
| **Fest gebuchter Anteil** | **60 %** | 42–80 % | S | siehe Abschnitt 2b |
| Restliche Stunden als Füllauftrag | 0,35 $, sinkt 10 % pro Jahr | 0,35–0,45 $ | Q | Spot-Preis L4 |
| Plattformkosten | 5 % | 0–5 % | E | Direktvertrag statt Marktplatz (15–30 %) |
| Preis im Vertrag | fest über die Laufzeit | – | E | Mehrjährige Verträge mit Abnahmepflicht sind im GPU-Markt Standard (2–5 Jahre) |
| Wechselkurs | 0,84 CHF/$ | – | Q | Mitte November 2026 |

## 2b. Wie die vier unsicheren Werte geschätzt sind

Für diese Posten gibt es keine öffentliche Zahl, weil sie pro Firma oder pro Objekt festgelegt werden. Sie sind deshalb aus Vergleichswerten geschätzt. Eine Offerte ersetzt die Schätzung später.

| Posten | Vergleichswert | Schätzung | Begründung |
|---|---|---|---|
| **Versicherung** | Hausrat Schweiz: Mobiliar 91,80 CHF für 110'000 CHF Summe ≈ **0,8 ‰** (hellosafe.ch); Hausrat ab 150 CHF/Jahr (comparis.ch) | **0,3–1,0 %, final 0,6 %** des Hardwarewerts, plus 5 % Stempelabgabe | Server in fremden Kellern mit Flüssigkühlung haben ein höheres Risiko als normaler Hausrat (Wasser, Überspannung, Diebstahl), dazu kommt eine Elektronikdeckung. Angesetzt: etwa das 4- bis 12-Fache des Hausratsatzes |
| **Einbau** | Schweizer Servicetechniker 143,80 CHF/h, Fahrt 1,60 CHF/km (SAK-Preisblatt); Installation einer Wärmepumpe ohne Gerät 5'000–12'000 € (Deutschland) | **6'400–12'800 CHF, final 9'000 CHF** | 30–60 Arbeitsstunden für Wärmetauscher, Hydraulik und eigenen Stromanschluss, plus 2'000–4'000 CHF Material |
| **Kreditzins** | SNB-Leitzins 0 %, SARON ≈ 0 %; gewerbliche SARON-Kredite = SARON + individuelle Marge (SGKB, BCF, Raiffeisen); Hypothekenmarge ab 1,0 % (PostFinance); Unternehmenskredite Euroraum 3,8 % (Bundesbank) | **3,5–5,5 %, final 4,5 %** | Ein ungesicherter Kredit für Server ist riskanter als eine Hypothek, die Marge liegt deshalb deutlich über 1 % |
| **Fest gebuchter Anteil** | Cloud-Kunden binden im Median **42 %** ihrer Rechenzeit vertraglich, die besten 25 % über **65 %**, Ziel vieler Firmen **70–80 %** (FinOps-Vergleiche); GPU-Anbieter wie CoreWeave machen 96–98 % ihres Umsatzes mit Mehrjahresverträgen | **42–80 %, final 60 %** | Ein neuer, kleiner Anbieter mit Winterkontingent bekommt eher weniger feste Buchungen als ein grosser GPU-Anbieter, aber mehr als der Median über alle Cloud-Kunden |

**Wirkung des fest gebuchten Anteils (Referenzhaus, 0,50 $):**

| Fest gebucht | 42 % (Median) | **60 % (final)** | 80 % (Zielwert) |
|---|---|---|---|
| Ergebnis pro Jahr | +1'200 CHF | **+8'800 CHF** | +17'300 CHF |
| Break-even | 0,49 $ | **0,43 $** | 0,39 $ |

## 3. Ergebnis pro Haus

| | Referenzhaus 8 kW | EFH 17'000 kWh, 4 kW | EFH 17'000 kWh, 5 kW |
|---|---|---|---|
| Wärmedeckung | 92,95 % | 93,6 % | 99,6 % |
| Hardware | 258'000 CHF | 129'000 CHF | 161'200 CHF |
| **Investition gesamt** | **290'100 CHF** | **151'100 CHF** | **185'800 CHF** |
| Rechenerlös im 1. Jahr | 101'200 CHF | 55'500 CHF | 59'000 CHF |
| Laufende Kosten im 1. Jahr (ohne Strom) | 9'200 CHF | 6'400 CHF | 7'100 CHF |
| **Ergebnis pro Jahr bei 0,50 $** | **+8'800 CHF** | **+5'000 CHF** | **+300 CHF** |
| **Break-even** | **0,43 $** | **0,43 $** | **0,50 $** |

Beim Durchschnitts-EFH sind **4 kW für DH klar besser** als 5 kW. Mit 5 kW verdient DH bei 0,50 $ praktisch nichts.

## 4. Bandbreite (Referenzhaus)

| | Günstig | **Final** | Teuer |
|---|---|---|---|
| Vertragspreis / fest gebucht | 0,55 $ / 80 % | **0,50 $ / 60 %** | 0,45 $ / 42 % |
| Hardware | −15 % | **258'000 CHF** | +15 % |
| Kühlung pro kW | 1'500 $ | **3'000 $** | 4'500 $ |
| Einbau | 6'400 CHF | **9'000 CHF** | 12'800 CHF |
| Zins / Versicherung / GPU-Ausfälle | 3,5 % / 0,3 % / 3 % | **4,5 % / 0,6 % / 4,5 %** | 5,5 % / 1,0 % / 6,1 % |
| **Ergebnis pro Jahr** | **+38'000 CHF** | **+8'800 CHF** | **−18'200 CHF** |
| **Break-even** | 0,31 $ | **0,43 $** | 0,66 $ |

**Was am meisten bewegt:**
1. **Fest gebuchter Anteil.** Zwischen 42 % und 80 % liegen rund 16'000 CHF pro Jahr.
2. **Vertragspreis.** 0,05 $ pro Stunde machen rund 6'000 CHF pro Jahr aus (0,45 $: +2'800, 0,55 $: +14'800 CHF).
3. **Hardwarepreis.** ±15 % sind rund ±9'000 CHF pro Jahr.
4. **Zins und Versicherung.** Zusammen bis rund 4'000 CHF pro Jahr.
5. **Wärmepreis an den Haushalt.** Gratis oder 7 Rp. macht nur rund 1'800 CHF pro Jahr aus. Gratiswärme ist für DH tragbar.

## 5. Wann es sich nicht lohnt

- **Vertragspreis unter 0,43 $** oder **weniger als rund 40 % der Stunden fest gebucht.**
- **Nur Marktplatz statt Direktvertrag:** Mit 20 % Gebühr und Preisverfall von 10 % pro Jahr braucht es rund 0,6 $, also so viel wie die Cloud mit festem Vertrag.
- **Neue H100 statt L4:** Selbst im günstigen Fall Verlust, weil die Hardware für Dauerbetrieb gebaut ist, DH aber nur die halbe Zeit rechnet.
- **Server nur pausieren statt ausschalten:** +1'550 CHF Strom und 3'700 kWh Abwärme pro Jahr.
- **Durchschnitts-EFH mit 5 statt 4 kW:** Ergebnis fällt praktisch auf null.

## 6. Abgleich mit Joëls Kundensicht

| Joëls Frage | Antwort Säule Firma |
|---|---|
| Wer zahlt Hardware, Einbau, Strom? | DH zahlt alles, eigener Stromzähler |
| Gratiswärme möglich? | **Ja.** Kostet DH rund 1'800 CHF pro Jahr gegenüber einem Abo zu 7 Rp. |
| Einheitengrösse? | Referenzhaus 8 kW, Durchschnitts-EFH **4 kW** (93,6 %) |
| Genug flexible Aufträge? | Ja im Winter, mit Pharma-Winterkontingent (`PHARMA_SICHT.md`) |
| Anteil am Rechenerlös? | Im Pilot nicht nötig |
| Vertrag, Konkurs? | Mindestens 5 Jahre (Abschreibung), Backup-Heizung bleibt |

**Hardwarekosten:** Joël nennt 142'000 CHF Hardware plus 20'000 CHF Einbau für 8 kW. Der belegte Komplettpreis (Gigabyte G293-Z43, 76'774 $ für 16 L4) ergibt **258'000 CHF für 8 kW** bzw. 161'000 CHF für 5 kW. Joëls 162'000 CHF passen also eher zu einer 5-kW-Einheit. Für die Rechnung gilt der belegte Preis.

## 7. Was Offerten noch genauer machen würden

| Was | Bei wem | Wirkung |
|---|---|---|
| Feste Buchung durch einen Pharma-Kunden | Gespräch mit einem Kunden | grösster Hebel (±16'000 CHF/Jahr) |
| Server-Konfiguration 8× L4 | Gigabyte-/Supermicro-Händler | ±9'000 CHF/Jahr |
| Kreditzins | Hausbank | ±2'000 CHF/Jahr |
| Versicherung (Inventar, Elektronik, Haftpflicht, Cyber) | Zurich, Mobiliar, AXA, Helvetia | ±1'500 CHF/Jahr |
| Einbau | Heizungsinstallateur Basel | ±1'000 CHF/Jahr |

## Quellen

- Komplettserver L4: https://www.avadirect.com (Gigabyte G293-Z43, 16× L4, 76'774 $), https://www.thinkmate.com/system/gigabyte-g293-s40-aap1
- L4-Karte und Mietpreise: https://jarvislabs.ai/blog/l4-gpu-price, https://getdeploying.com/gpus/nvidia-l4, https://www.doit.com/compute/spot/us-east-1/g6.xlarge, https://calculator.holori.com/gcp/vm/g2-standard-4
- Leerlauf: https://arxiv.org/html/2412.08602v2
- GPU-Ausfälle: https://arxiv.org/pdf/2407.21783; Verfügbarkeit: https://arxiv.org/html/2503.11901v4
- Garantie: https://www.supermicro.com/en/support/warranty, https://www.shi.com/product/46051810/NVIDIA-L4-GPU-computing-processor
- Flüssigkühlung: https://introl.com/blog/direct-to-chip-cooling-pue-below-12-implementation, https://www.servnetuk.com/learn/direct-to-chip-liquid-cooling-explained, https://stlpartners.com/press/liquid-cooling-retrofits-can-cost-roughly-80-less/, https://www.servnetuk.com/insights/liquid-cooling-maintenance-requirements
- Einbau: https://www.sak.ch/downloads/waerme/wartung-und-service/sak_preisblatt-wartung_waermepumpen_01_06.pdf, https://leospardo.de/ratgeber/waermepumpe-einbau-kosten/, https://www.raiffeisen.ch/rch/de/wissen/wohnen/kostenbeispiel-waermepumpe.html
- Pufferspeicher: https://www.klimaworld.com/products/schichten-pufferspeicher-klimaworld-1000-liter
- Monitoring: https://www.datadoghq.com/pricing/list/
- Internet: https://www.swisscom.ch/de/business/kmu/internet-festnetz-fernsehen/angebote/business-internet-services.html, https://www.init7.net/en/offer/business-internet
- Netzwerk: https://www.boll.ch/ch_de/fortinet/preise.html
- Versicherung: https://hellosafe.ch/de/hausratversicherung/mobiliar, https://www.comparis.ch/hausrat-versicherung/hausratversicherung, https://www.mobiliar.ch/ratgeber/richtige-versicherungssumme-im-kmu, https://hellosafe.ch/de/berufshaftpflichtversicherung/kosten
- ISO 27001: https://www.orbiqhq.com/de/compliance-automatisierung/iso-27001-zertifizierung-kosten
- Restwert: https://www.amcompute.com/appraisals/tesla-t4
- Zins: https://www.sgkb.ch/.dam/97ec929f-9d37-4424-9cf9-96747c67c493/sgkb-factsheet-saron-kredit.pdf, https://bcf.ch/de/firmenkunden/finanzierung/kredite-und-leasing/gewerbliches-saron-darlehen, https://www.postfinance.ch/de/thema/aktuelle-zinssaetze.html, https://www.bundesbank.de/resource/blob/1007288/4cb2afba5124a71bb1996fd5aa0def80/472B63F073F071307366337C94F8C870/2026-09-02-mfi-zinsstatistik-download.pdf
- Fest gebuchter Anteil: https://vendorbenchmark.com/blog/finops-cloud-cost-management-benchmark-guide, https://pdpspectra.com/blog/finops-reserved-instances-2026, https://electroneconomics.substack.com/p/coreweaves-contract-machine-how-a
- Steuer: https://kpmg.com/ch/de/medien/medienmitteilungen/2026/05/clarity-swiss-taxes.html
- Preissteigerung Wartung: https://www.servnetuk.com/research/oem-support-price-hike-tracker-2026
- Strompreis: ElCom-API, IWB Basel 2026
