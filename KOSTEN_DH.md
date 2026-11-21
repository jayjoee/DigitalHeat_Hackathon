# Kosten und Wirtschaftlichkeit aus Sicht DigitalHeat – finale Fassung (21.11.2026)

Säule «Firma». Ergänzt Joëls Kundensicht (`CustomerView_Joel.md`) und die Pharma-Sicht (`PHARMA_SICHT.md`). **Alle Beträge in CHF.** Dollar- und Euro-Quellen sind mit 0,84 CHF/$ und 0,92 CHF/€ umgerechnet (Mitte November 2026). Gerechnet wird mit `src/wirtschaft.py`; das Dashboard rechnet dieselbe Formel.

## Kurzfassung

| | Referenzhaus (31'231 kWh) | Durchschnitts-EFH (17'000 kWh) |
|---|---|---|
| Server (kW) | **8** | **4** (Team-Ziel 93 %) oder 5 (Joël, 99,6 %) |
| Wärmedeckung | 92,95 % | 93,6 % / 99,6 % |
| Investition DH | **290'100 CHF** | 151'100 / 185'800 CHF |
| Wärme an den Haushalt | gratis | gratis |
| Ergebnis DH pro Jahr (Vertragspreis 0,60 CHF, 60 % fest gebucht) | **+34'500 CHF** | +19'000 / +15'300 CHF |
| Vorsichtiger Fall (0,50 CHF) | +20'300 CHF | +11'200 / +6'900 CHF |
| Investition zurück nach | **3,0 Jahren** | 2,9 / 3,4 Jahren |
| **Nötiger Vertragspreis (Break-even)** | **0,36 CHF pro L4-Stunde** (= 2,87 CHF pro Server-Stunde) | 0,36 / 0,42 CHF |
| Was Kunden mit Datenstandort Schweiz heute zahlen | Schweizer GPU-Clouds ab ≈ 0,68 CHF (Hikube) bis 2,13 CHF (Everyware) | gleich |

**In einem Satz:** DigitalHeat ist eine Schweizer Cloud für Kunden, deren Daten in der Schweiz bleiben müssen (Pharma, Banken, Spitäler). Mit 0,60 CHF pro L4-Stunde, rund 12 % unter Schweizer GPU-Clouds, und 60 % fest gebuchten Stunden verdient DH beim Referenzhaus rund 34'500 CHF pro Jahr nach allen Kosten, Steuern und Zinsen, gibt dem Haushalt die Wärme gratis und hat die Investition nach 3 Jahren zurück. Die Grenze liegt bei 0,36 CHF (Spanne 0,26–0,55 CHF).

**Zwei Break-even-Zahlen:** Der Case definiert den Break-even als (Strom − Wert der genutzten Wärme) ÷ Server-Stunden = **0,23 CHF pro Server-Stunde** (ohne Hardware). Mit allen Kosten braucht DH **2,87 CHF pro Server-Stunde**, also 0,36 CHF pro L4-Karte und Stunde.

Ergebnis = Gewinn nach Steuern, Jahresmittel über 5 Jahre, nach Zinskosten (abgezinst), mit Preisverfall, Garantie, Restwert und Preissteigerung. Ohne Zinskosten ist der Gewinn nach Steuern im Mittel **43'000 CHF pro Jahr**; die Rendite auf die Investition beträgt rund **21 % pro Jahr** (vorsichtiger Fall 0,50 CHF: 14,5 %).

**Warum 0,60 CHF:** Die Zielkunden (Pharma, Banken, Spitäler, Versicherungen) brauchen ihre Daten in der Schweiz und unter Schweizer Recht. Für sie fallen US-Clouds weg, auch mit Rechenzentrum in der Schweiz (US-Behörden können über den CLOUD Act Daten verlangen). Sie vergleichen DH mit Schweizer GPU-Clouds: Hikube ≈ 0,68 CHF, Everyware 2,13 CHF pro L4-Stunde. DH liefert vor allem im Winter und unterbrechbar, darum liegt der Preis darunter. Für Aufträge ohne Standortpflicht gilt der vorsichtige Fall 0,50 CHF (US-Clouds mit festem Vertrag: 0,53–0,55 CHF).

---

## 1. Die Formel

```
Gewinn pro Haus und Jahr = Erlös Rechnen + Erlös Wärme − Strom − laufende Kosten − Steuern
                           − (Investition − Restwert) verteilt auf 5 Jahre inkl. Zins

Erlös Rechnen = Server-Stunden × 8 Karten × (1 − Plattform) × Verfügbarkeit
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
| Strompreis | 0,3325 CHF/kWh | – | Q | ElCom 2026, IWB H4 |
| Wärme an den Haushalt | **gratis** | 0–0,07 CHF/kWh | E | Joëls Pilot-Modell |
| Verfügbarkeit | 99,3 % | – | Q | arXiv 2503.11901 |

### Investition (einmalig)

| Variable | Final | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| **Server mit 8 L4 inkl. CPU, RAM, SSD** | **32'245 CHF** | ±15 % | Q | Konfigurierter Preis Gigabyte G293-Z43: 16× L4, 2× EPYC 9335, 12× 32 GB = 76'774 $ ≈ **64'490 CHF** (avadirect.com) → halbes System pro 8 L4 |
| Flüssigkühlung | 2'520 CHF pro kW | 1'260–3'780 CHF | D | 1'500–4'500 $/kW (introl.com, servnetuk.com, stlpartners.com) |
| **Einbau** (Wärmetauscher, Hydraulik, Elektro) | **9'000 CHF** | 6'400–12'800 | S | 30–60 h × 143,80 CHF/h (SAK) + Material 2'000–4'000 CHF |
| Pufferspeicher | 1'800 CHF | 1'200–2'500 | D | Gerät 830–1'020 CHF (klimaworld.com, 900–1'110 €) plus Einbau |
| Netzwerk (Firewall, Switch) | 1'200 CHF | 800–1'600 | Q/S | FortiGate 40F 441 CHF (boll.ch) |
| Abschreibung | 5 Jahre | – | E | Hyperscaler 5–6 Jahre |
| Restwert nach 5 Jahren | 20 % | 15–30 % | Q/S | Tesla T4 nach ≈ 7 Jahren 22–25 % des Neupreises (amcompute.com) |
| **Zins** | **4,5 %** | 3,5–5,5 % | S | SARON ≈ 0 % + Bankmarge; siehe Abschnitt 2b |

### Laufende Kosten (pro Jahr, Referenzhaus)

| Variable | Final | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| Strom | 12'066 CHF | – | Q | 36'290 kWh × 0,3325 CHF |
| GPU-Ersatz (ab Jahr 4, vorher Garantie) | 4,5 % der Karten pro Jahr, je 2'100 CHF | 3–6,1 % | Q | Meta Llama 3: 6,1 %/Jahr bei 24/7-Training; L4 3 Jahre Garantie (shi.com); L4 1'680–2'520 CHF (jarvislabs.ai) |
| Host-Reparaturen (ab Jahr 2) | 3,5 % des Hostanteils | 2–5 % | S | Supermicro: 1 Jahr Teile, 3 Jahre Arbeit |
| Störungseinsätze | 2'600 CHF | 1'100–4'200 | CH | SAK: 281 CHF Pauschale, 143,80 CHF/h, 1,60 CHF/km |
| Service Kühlung + Hydraulik | 520 CHF | 400–630 | CH/D | SAK-Serviceabo 275–500 CHF; Kühlservice 16,80 CHF pro kW |
| Monitoring | 1'210 CHF | 0–1'450 | Q | Datadog 12,60–15,10 CHF pro Server und Monat |
| Internet | 1'600 CHF | 800–2'460 | CH | Init7, Swisscom Business |
| **Versicherung** | **0,6 % des Hardwarewerts + 5 % Stempel = 1'625 CHF** | 0,3–1,0 % | S | siehe Abschnitt 2b |
| Netzwerk-Lizenz | 450 CHF | 300–600 | Q | boll.ch |
| Firmenanteil (Personal, Vertrieb, ISO 27001, Haftpflicht) | 1'200 CHF | 500–2'000 | S/D | ISO 27001: 23'000–55'000 CHF im 1. Jahr, danach 7'000–18'000 CHF (orbiqhq.com); Haftpflicht 200–1'500 CHF/Jahr (hellosafe.ch). Gilt bei rund 100 Häusern |
| Preissteigerung laufende Kosten | 4,5 % pro Jahr | 3–6 % | D | servnetuk.com |
| Gewinnsteuer | 13,04 % | – | Q | Basel-Stadt (KPMG 2026) |

### Erlös (aus `PHARMA_SICHT.md`)

| Variable | Final | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| **Vertragspreis** | **0,60 CHF pro L4-Stunde** | 0,50–0,66 CHF | Q/E | rund 12 % unter Schweizer GPU-Clouds (Hikube ≈ 0,68 CHF, Everyware 2,13 CHF; getdeploying.com, everyware.ch); vorsichtiger Fall 0,50 CHF |
| **Fest gebuchter Anteil** | **60 %** | 42–80 % | S | siehe Abschnitt 2b |
| Restliche Stunden als Füllauftrag | 0,29 CHF, sinkt 10 % pro Jahr | 0,29–0,38 CHF | Q | L4-Spot-Preis |
| Plattformkosten | 5 % | 0–5 % | E | Direktvertrag statt Marktplatz (15–30 %) |
| Preis im Vertrag | fest über die Laufzeit | – | E | Mehrjährige Verträge mit Abnahmepflicht sind im GPU-Markt Standard (2–5 Jahre) |

## 2b. Wie die vier unsicheren Werte geschätzt sind

Für diese Posten gibt es keine öffentliche Zahl, weil sie pro Firma oder pro Objekt festgelegt werden. Sie sind deshalb aus Vergleichswerten geschätzt. Eine Offerte ersetzt die Schätzung später.

| Posten | Vergleichswert | Schätzung | Begründung |
|---|---|---|---|
| **Versicherung** | Hausrat Schweiz: Mobiliar 91,80 CHF für 110'000 CHF Summe ≈ **0,8 ‰** (hellosafe.ch); Hausrat ab 150 CHF/Jahr (comparis.ch) | **0,3–1,0 %, final 0,6 %** des Hardwarewerts, plus 5 % Stempelabgabe | Server in fremden Kellern mit Flüssigkühlung sind riskanter als Hausrat (Wasser, Überspannung, Diebstahl), dazu kommt eine Elektronikdeckung |
| **Einbau** | Schweizer Servicetechniker 143,80 CHF/h, Fahrt 1,60 CHF/km (SAK); Installation einer Wärmepumpe ohne Gerät 4'600–11'000 CHF (Deutschland, 5'000–12'000 €) | **6'400–12'800 CHF, final 9'000 CHF** | 30–60 Arbeitsstunden plus 2'000–4'000 CHF Material |
| **Kreditzins** | SNB-Leitzins 0 %, SARON ≈ 0 %; gewerbliche SARON-Kredite = SARON + Marge (SGKB, BCF, Raiffeisen); Hypothekenmarge ab 1,0 % (PostFinance); Unternehmenskredite Euroraum 3,8 % (Bundesbank) | **3,5–5,5 %, final 4,5 %** | Ein ungesicherter Kredit für Server ist riskanter als eine Hypothek |
| **Fest gebuchter Anteil** | Cloud-Kunden binden im Median **42 %** ihrer Rechenzeit, die besten 25 % über **65 %**, Ziel vieler Firmen **70–80 %** (FinOps-Vergleiche); CoreWeave macht 96–98 % des Umsatzes mit Mehrjahresverträgen | **42–80 %, final 60 %** | Ein neuer, kleiner Anbieter mit Winterkontingent bekommt weniger feste Buchungen als ein grosser, aber mehr als der Median |

**Wirkung des fest gebuchten Anteils (Referenzhaus, 0,60 CHF):**

| Fest gebucht | 42 % (Median) | **60 % (final)** | 80 % (Zielwert) |
|---|---|---|---|
| Ergebnis pro Jahr | +19'200 CHF | **+34'500 CHF** | +51'500 CHF |
| Break-even | 0,41 CHF | **0,36 CHF** | 0,33 CHF |

## 3. Ergebnis pro Haus

| | Referenzhaus 8 kW | EFH 17'000 kWh, 4 kW | EFH 17'000 kWh, 5 kW |
|---|---|---|---|
| Wärmedeckung | 92,95 % | 93,6 % | 99,6 % |
| Hardware | 258'000 CHF | 129'000 CHF | 161'200 CHF |
| **Investition gesamt** | **290'100 CHF** | **151'100 CHF** | **185'800 CHF** |
| Rechenerlös im 1. Jahr | 130'800 CHF | 71'700 CHF | 76'300 CHF |
| Laufende Kosten im 1. Jahr (ohne Strom) | 9'200 CHF | 6'400 CHF | 7'100 CHF |
| **Ergebnis pro Jahr (0,60 CHF)** | **+34'500 CHF** | **+19'000 CHF** | **+15'300 CHF** |
| Ergebnis pro Jahr, vorsichtig (0,50 CHF) | +20'300 CHF | +11'200 CHF | +6'900 CHF |
| Investition zurück nach | 3,0 Jahren | 2,9 Jahren | 3,4 Jahren |
| Rendite (interner Zinsfuss) | 21 % | 22 % | 16 % |
| **Break-even pro L4-Stunde** | **0,36 CHF** | **0,36 CHF** | **0,42 CHF** |

**Rechnung Jahr für Jahr (Referenzhaus, 0,60 CHF):**

| CHF | Jahr 1 | Jahr 2 | Jahr 3 | Jahr 4 | Jahr 5 |
|---|---|---|---|---|---|
| Erlös | 130'802 | 127'581 | 124'682 | 122'074 | 119'726 |
| Strom | −12'066 | −12'066 | −12'066 | −12'066 | −12'066 |
| Laufende Kosten | −9'209 | −12'926 | −13'507 | −21'017 | −21'963 |
| Abschreibung | −47'706 | −47'706 | −47'706 | −47'706 | −47'706 |
| Gewinn vor Steuern | 61'821 | 54'883 | 51'403 | 41'285 | 37'991 |
| Steuern | −8'061 | −7'157 | −6'703 | −5'384 | −4'954 |
| **Gewinn nach Steuern** | **53'759** | **47'727** | **44'700** | **35'901** | **33'037** |
| Geld zurück (kumuliert, nach Investition 290'120) | −188'655 | −93'223 | −817 | +82'790 | +215'125 |

**Serverzahl:** Bei 0,60 CHF verdient DH beim Referenzhaus am meisten mit **7 Servern** (+35'600 CHF pro Jahr, 87,1 % Deckung). Die 8 Server für das Team-Ziel von 93 % kosten nur rund 1'000 CHF Gewinn pro Jahr, sind also praktisch optimal. Ab 13 Servern bleibt kaum noch Gewinn. Beim Durchschnitts-EFH sind 4 kW besser als 5 kW (+19'000 statt +15'300 CHF).

## 4. Bandbreite (Referenzhaus)

| | Günstig | **Final** | Teuer |
|---|---|---|---|
| Vertragspreis / fest gebucht | 0,66 CHF / 80 % | **0,60 CHF / 60 %** | 0,50 CHF / 42 % |
| Hardware | −15 % | **258'000 CHF** | +15 % |
| Kühlung pro kW | 1'260 CHF | **2'520 CHF** | 3'780 CHF |
| Einbau | 6'400 CHF | **9'000 CHF** | 12'800 CHF |
| Zins / Versicherung / GPU-Ausfälle | 3,5 % / 0,3 % / 3 % | **4,5 % / 0,6 % / 4,5 %** | 5,5 % / 1,0 % / 6,1 % |
| **Ergebnis pro Jahr** | **+75'700 CHF** | **+34'500 CHF** | **−5'300 CHF** |
| **Break-even pro L4-Stunde** | 0,26 CHF | **0,36 CHF** | 0,55 CHF |

**Was am meisten bewegt:**
1. **Vertragspreis.** 10 Rappen pro L4-Stunde machen rund 14'300 CHF pro Jahr aus (0,50 CHF: +20'300, 0,60 CHF: +34'500 CHF).
2. **Fest gebuchter Anteil.** Zwischen 42 % und 80 % liegen rund 32'000 CHF pro Jahr.
3. **Hardwarepreis.** ±15 % sind rund ±9'000 CHF pro Jahr.
4. **Zins und Versicherung.** Zusammen bis rund 4'000 CHF pro Jahr.
5. **Wärmepreis an den Haushalt.** Gratis oder 7 Rp./kWh macht nur rund 1'800 CHF pro Jahr aus. Gratiswärme ist für DH tragbar.

## 5. Wann es sich nicht lohnt

- **Vertragspreis unter 0,36 CHF pro L4-Stunde.** Bei 0,60 CHF bleibt also viel Spielraum.
- **Kunden ohne Standortpflicht:** Sie rechnen bei US-Clouds mit festem Vertrag für 0,53–0,55 CHF. Für sie muss DH auf rund 0,50 CHF (vorsichtiger Fall).
- **Teurer Fall** (0,50 CHF, nur 42 % fest gebucht, Kosten am oberen Rand): −5'300 CHF pro Jahr.
- **Nur Marktplatz statt Direktvertrag:** Mit 20 % Gebühr und Preisverfall von 10 % pro Jahr braucht es rund 0,50 CHF, also fast so viel wie die Cloud mit festem Vertrag.
- **Neue H100 statt L4:** Selbst im günstigen Fall Verlust, weil die Hardware für Dauerbetrieb gebaut ist, DH aber nur die halbe Zeit rechnet.
- **Server nur pausieren statt ausschalten:** +1'550 CHF Strom und 3'700 kWh Abwärme pro Jahr.
- **Pilot mit wenigen Häusern:** Die Firmenkosten (Zertifikat, Software, Personal) verteilen sich auf wenige Häuser; der Pilot ist eine Investition und macht voraussichtlich Verlust.

## 6. Abgleich mit Joëls Kundensicht

| Joëls Frage | Antwort Säule Firma |
|---|---|
| Wer zahlt Hardware, Einbau, Strom? | DH zahlt alles, eigener Stromzähler |
| Gratiswärme möglich? | **Ja.** Kostet DH rund 1'800 CHF pro Jahr gegenüber einem Abo zu 7 Rp. |
| Einheitengrösse? | Referenzhaus 8 kW, Durchschnitts-EFH **4 kW** (93,6 %) |
| Genug flexible Aufträge? | Ja im Winter, mit Pharma-Winterkontingent (`PHARMA_SICHT.md`) |
| Anteil am Rechenerlös? | Im Pilot nicht nötig |
| Vertrag, Konkurs? | Mindestens 5 Jahre (Abschreibung), Backup-Heizung bleibt |

**Hardwarekosten:** Joël nennt 142'000 CHF Hardware plus 20'000 CHF Einbau für 8 kW. Der belegte Komplettpreis ergibt **258'000 CHF für 8 kW** bzw. 161'000 CHF für 5 kW. Joëls 162'000 CHF passen eher zu einer 5-kW-Einheit. Für die Rechnung gilt der belegte Preis.

## 7. Was Offerten noch genauer machen würden

| Was | Bei wem | Wirkung |
|---|---|---|
| Preis und feste Buchung durch einen Kunden mit Standortpflicht | Gespräch mit Pharma, Bank oder Spital | grösster Hebel (±14'000 CHF pro 10 Rappen, ±32'000 CHF bei der Buchung) |
| Server-Konfiguration 8× L4 | Gigabyte-/Supermicro-Händler | ±9'000 CHF/Jahr |
| Kreditzins | Hausbank | ±2'000 CHF/Jahr |
| Versicherung (Inventar, Elektronik, Haftpflicht, Cyber) | Zurich, Mobiliar, AXA, Helvetia | ±1'500 CHF/Jahr |
| Einbau | Heizungsinstallateur Basel | ±1'000 CHF/Jahr |

## Quellen

- Schweizer GPU-Clouds: https://getdeploying.com/hikube, https://www.everyware.ch/fr/sovereign-cloud/open-cloud/prices, https://www.cloudscale.ch/en/gpu, https://www.infomaniak.com/en/hosting/gpu
- Wechselkurse: USD/CHF 0,84 (tradingeconomics.com, therighttrader.com), EUR/CHF ≈ 0,92 (currencylive.com: 0,924 am 18.11.2026)
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
