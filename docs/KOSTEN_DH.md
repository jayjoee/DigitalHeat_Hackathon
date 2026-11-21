# Kosten und Wirtschaftlichkeit aus Sicht DigitalHeat (Stand 21.11.2026, überarbeitet)

Säule «Firma». Ergänzt Joëls Kundensicht (`CustomerView_Joel.md`), die Pharma-Sicht (`PHARMA_SICHT.md`) und die Rechnung für die ganze Firma (`FIRMA.md`). Das Angebot selbst ist in `L4_ANGEBOT.md` festgelegt. **Alle Beträge in CHF.** Dollar- und Euro-Quellen sind mit 0,84 CHF/$ und 0,92 CHF/€ umgerechnet (Mitte November 2026). Gerechnet wird mit `src/wirtschaft.py`.

**Rechenbasis ist das Abschaltmodell**, wie in `PITCH.md`, `README.md` und `FIRMA.md`: Server ohne Arbeit werden abgeschaltet, im Leerlauf ziehen sie angenommene 230 W, im Standby 10 W, ein Start dauert 5 Minuten (`src/scheduler/serverbetrieb.py`, `ERGEBNISSE.md`, Abschnitt «Leerlauf und Abschalten im Referenzhaus»). Das Idealmodell des Case (0 W Leerlauf) steht jeweils zum Vergleich daneben. Frühere Fassungen dieses Dokuments nannten nur die Zahlen des Idealmodells (+34'500 CHF, Break-even 0,36 CHF).

## Kurzfassung

| | Referenzhaus (31'231 kWh) | Durchschnitts-EFH (17'000 kWh), 4 kW | Durchschnitts-EFH, 5 kW |
|---|---|---|---|
| Server (je 1 kW) | **8** | 4 | 5 |
| Wärmedeckung | **90,5 %** | 91,5 % | 98,7 % |
| Verkaufte Server-Stunden pro Jahr | 34'512 | 18'873 | 20'324 |
| Investition DH | **290'100 CHF** | 151'100 CHF | 185'800 CHF |
| Wärme an den Haushalt | gratis | gratis | gratis |
| **Ergebnis DH pro Jahr** (0,60 CHF, 60 % fest gebucht, alle Stunden verkauft) | **+29'400 CHF** | +16'100 CHF | +12'700 CHF |
| Vorsichtiger Preis (0,50 CHF) | +15'800 CHF | +8'700 CHF | +4'700 CHF |
| Investition zurück nach | **3,2 Jahren** | 3,1 Jahren | 3,6 Jahren |
| Interner Zinsfuss | 18,8 % | 19,6 % | 14,4 % |
| **Nötiger Vertragspreis (Break-even)** | **0,38 CHF pro L4-Stunde** (= 3,07 CHF pro Server-Stunde) | 0,38 CHF | 0,44 CHF |
| Zum Vergleich: Idealmodell des Case (0 W Leerlauf) | 92,95 % Deckung, +34'500 CHF, Break-even 0,36 CHF | 93,6 %, +19'000 CHF | 99,6 %, +15'300 CHF |

**In einem Satz:** Wenn DigitalHeat jede Rechenstunde verkauft, 60 % davon fest zu 0,60 CHF pro L4-Stunde und den Rest zum Spot-Preis, bleiben beim Referenzhaus rund 29'400 CHF pro Jahr nach allen Kosten, Steuern und Zinsen. Der Haushalt bekommt die Wärme gratis, die Investition ist nach gut 3 Jahren zurück. Preis und Absatz sind Annahmen und noch mit keinem Kunden bestätigt.

### Was diese Zahl voraussetzt

Die +29'400 CHF gelten nur, wenn alle fünf Punkte zutreffen. Die ersten beiden entscheiden über das Geschäft.

1. **Jede gerechnete Stunde findet einen Käufer.** Die Server laufen, wenn das Haus Wärme braucht. Das Modell verkauft alle diese Stunden. Bleibt ein Teil unverkauft, läuft der Strom trotzdem:

   | Verkaufte Stunden | 100 % | 90 % | 80 % | 72 % | 60 % |
   |---|---|---|---|---|---|
   | Ergebnis pro Jahr | **+29'400 CHF** | +19'000 CHF | +8'700 CHF | 0 | −12'700 CHF |

   Mit der Nachfrage aus dem Alibaba-Trace ist die Flotte negativ (Abschnitt 8).
2. **0,60 CHF pro L4-Stunde ist ein Zielpreis, kein bestätigter Preis.** Nach `L4_ANGEBOT.md` rechnet DH nur öffentliche, synthetische oder vom Kunden freigegebene anonymisierte Aufgaben. Für solche Aufgaben ist die Zahlungsbereitschaft noch nicht belegt.
3. **Der Vertragspreis bleibt 5 Jahre fest**, während der Spot-Preis im Modell 10 % pro Jahr fällt. Fällt der Vertragspreis ebenso, bleiben +15'200 CHF.
4. **Firmenkosten von 1'200 CHF pro Haus.** Das gilt erst bei grosser Stückzahl. `FIRMA.md` rechnet mit 5'400 CHF pro Haus bei 170 Häusern und 77'000 CHF bei 5 Häusern.
5. **4,5 % Zins**, der zugleich der Diskontsatz ist. Für ein junges Unternehmen ist das tief: bei 8 % bleiben +22'500 CHF, bei 12 % +14'400 CHF.

**Preise pro Server-Stunde (für den Pitch):** Ein Server hat 8 L4-Karten. 0,60 CHF pro L4-Stunde = **4,80 CHF pro Server-Stunde**. Hikube 0,68 CHF = 5,44 CHF, Spot 0,294 CHF = 2,35 CHF, Break-even 0,384 CHF = 3,07 CHF pro Server-Stunde. Im Code und in `annahmen.py` bleibt alles pro L4-Stunde, nur die Anzeige rechnet × 8.

**Zwei Break-even-Zahlen:** Der Case definiert den Break-even als (Strom − Wert der genutzten Wärme) ÷ Server-Stunden = **0,23 CHF pro Server-Stunde** (ohne Hardware; im Abschaltmodell 0,235 CHF, im Idealmodell 0,226 CHF). Mit allen Kosten braucht DH **3,07 CHF pro Server-Stunde**, also 0,38 CHF pro L4-Karte und Stunde.

**Was «Ergebnis pro Jahr» heisst:** Kapitalwert über 5 Jahre, als gleichmässiger Jahresbetrag ausgedrückt. Enthalten sind Steuern, Zinskosten, Preisverfall beim Spot-Preis, Garantie, Restwert und Preissteigerung der laufenden Kosten. Ohne Zinskosten ist der Gewinn nach Steuern im Mittel **37'900 CHF pro Jahr**, das sind 13 % der Investition. Der interne Zinsfuss beträgt 18,8 % (bei 0,50 CHF: 12,4 %).

**Warum 0,60 CHF:** Der Preis ist eine Zielannahme des Teams (`L4_ANGEBOT.md`). Zur Einordnung: Schweizer GPU-Clouds verlangen ab ≈ 0,68 CHF (Hikube) bis 2,13 CHF (Everyware) pro L4-Stunde, US-Clouds mit festem Vertrag 0,53–0,55 CHF, Spot kostet 0,29–0,38 CHF. Die Vergleichsangebote enthalten teils andere CPU-, RAM- und Serviceleistungen und sind nicht Stück für Stück verglichen. DH liefert vor allem im Winter und unterbrechbar, darum liegt der Zielpreis unter den Schweizer Listenpreisen. Die frühere Begründung über Kunden mit Datenstandortpflicht (Pharma, Banken, Spitäler) gilt nicht mehr: Vertrauliche Daten sind vom L4-Angebot ausgeschlossen, weil L4 keinen Schutz während der Verarbeitung bietet (`CONFIDENTIAL_COMPUTING.md`).

---

## 1. Die Formel

```
Gewinn pro Haus und Jahr = Erlös Rechnen + Erlös Wärme − Strom − laufende Kosten − Steuern
                           − (Investition − Restwert) verteilt auf 5 Jahre inkl. Zins

Erlös Rechnen = verkaufte Server-Stunden × 8 Karten × (1 − Plattform) × Verfügbarkeit
                × [Anteil fest gebucht × Vertragspreis + Rest × Spot-Preis]

Strom         = gesamter Verbrauch (Rechnen + Leerlauf + Standby + Starts) × Strompreis

Break-even    = der Vertragspreis, bei dem der Gewinn genau 0 ist
```

**Nachrechnen** (Referenzhaus, Stunden und Strom aus `daten/ergebnisse/serverbetrieb.json`, Zeile «abschalten», 230 W):

```sh
python3 -c "from src.wirtschaft import rechne, break_even as b; a=(8, 34511.6, 28272.3); print(rechne(*a, strom_kwh=35662.1)['ergebnis_pro_jahr_chf'], b(*a, strom_kwh=35662.1))"
# 29388 0.384
```

Die Werte für das Durchschnitts-EFH stammen aus derselben Simulation (`HausMitServerbetrieb` mit dem Profil aus `src/dashboard3d_daten.py`, `profil_haus2`). Dafür gibt es noch kein eigenes Skript und keine Ergebnisdatei im Repo.

## 2. Annahmen

**Qualität:** **Q** = Quelle · **CH** = Schweizer Preisliste · **D** = ausländische oder Branchenwerte · **S** = Schätzung aus Vergleichswerten (Herleitung in Abschnitt 2b) · **E** = Entscheid im Team

### Haus und Betrieb

| Variable | Wert | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| Verkaufte Server-Stunden Referenzhaus | 34'512 h | 36'290 h im Idealmodell | Q | Jahressimulation Basel 2025, Abschaltmodell |
| Gesamtstrom | 35'662 kWh | – | Q | davon Rechnen 34'512, Leerlauf 769, Standby 322, Starts 60 kWh |
| Genutzte Wärme | 28'272 kWh (90,5 %) | 29'027 kWh im Idealmodell | Q | Jahressimulation |
| Leerlauf, Standby, Startzeit | 230 W, 10 W, 5 min | Leerlauf 100–350 W (Ergebnis +30'500 bis +28'200 CHF) | S | Leerlauf aus einer H100-Messung abgeleitet (Latif et al. 2024). **Keine Messung an L4-Hardware** |
| Server ausschalten statt pausieren | ja | – | E | Pausieren kostet rund 8'500 CHF Ergebnis pro Jahr (Abschnitt 5) |
| Strompreis | 0,3325 CHF/kWh | 0,327–0,333 | Q | ElCom 2026, IWB H4 (Haushaltsprofil). Bei 36 MWh pro Jahr passt eher das Gewerbeprofil C2 mit 0,32745 CHF (`ANNAHMEN_PRUEFUNG.md`); das wären +160 CHF pro Jahr |
| Wärme an den Haushalt | **gratis** | 0–0,07 CHF/kWh | E | Joëls Pilot-Modell |
| Verfügbarkeit | 99,3 % | – | Q | arXiv 2503.11901 |

### Investition (einmalig)

| Variable | Wert | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| **Server mit 8 L4 inkl. CPU, RAM, SSD** | **32'245 CHF** | ±15 % | Q | Konfigurierter Preis Gigabyte G293-Z43: 16× L4, 2× EPYC 9335, 12× 32 GB = 76'774 $ ≈ **64'490 CHF** (avadirect.com) → halbes System pro 8 L4. US-Listenpreis ohne Versand und Schweizer Händlermarge |
| Flüssigkühlung | 2'520 CHF pro kW | 1'260–3'780 CHF | D | 1'500–4'500 $/kW (introl.com, servnetuk.com, stlpartners.com) |
| **Einbau** (Wärmetauscher, Hydraulik, Elektro) | **9'000 CHF** | 6'400–12'800 | S | 30–60 h × 143,80 CHF/h (SAK) + Material 2'000–4'000 CHF |
| Pufferspeicher | 1'800 CHF | 1'200–2'500 | D | Gerät 830–1'020 CHF (klimaworld.com, 900–1'110 €) plus Einbau |
| Netzwerk (Firewall, Switch) | 1'200 CHF | 800–1'600 | Q/S | FortiGate 40F 441 CHF (boll.ch) |
| Abschreibung | 5 Jahre | – | E | Hyperscaler 5–6 Jahre |
| Restwert nach 5 Jahren | 20 % | 15–30 % | Q/S | Tesla T4 nach ≈ 7 Jahren 22–25 % des Neupreises (amcompute.com) |
| **Zins und Diskontsatz** | **4,5 %** | 3,5–5,5 % (Kredit), 8–12 % (Risikokapital) | S | SARON ≈ 0 % + Bankmarge; siehe Abschnitt 2b |

**Nicht in dieser Investition, aber in `FIRMA.md`:** Rückbau von Ölkessel und Tank (4'000 CHF, zahlt DH) und der Förderbeitrag Basel-Stadt (rund 7'200 CHF pro Haus, an DH abgetreten). Beide zusammen verbessern das Ergebnis um rund 650 CHF pro Jahr. Ebenfalls nicht enthalten: Wärmezähler, Rückbau der Anlage am Vertragsende, ein allfälliger Ausbau des Hausanschlusses.

### Laufende Kosten (pro Jahr, Referenzhaus)

| Variable | Wert | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| Strom | 11'858 CHF | – | Q | 35'662 kWh × 0,3325 CHF |
| GPU-Ersatz (ab Jahr 4, vorher Garantie) | 4,5 % der Karten pro Jahr, je 2'100 CHF | 3–6,1 % | Q | Meta Llama 3: 6,1 %/Jahr bei 24/7-Training; L4 3 Jahre Garantie (shi.com); L4 1'680–2'520 CHF (jarvislabs.ai) |
| Host-Reparaturen (ab Jahr 2) | 3,5 % des Hostanteils | 2–5 % | S | Supermicro: 1 Jahr Teile, 3 Jahre Arbeit |
| Störungseinsätze | 2'600 CHF | 1'100–4'200 | CH | SAK: 281 CHF Pauschale, 143,80 CHF/h, 1,60 CHF/km |
| Service Kühlung + Hydraulik | 520 CHF | 400–630 | CH/D | SAK-Serviceabo 275–500 CHF; Kühlservice 16,80 CHF pro kW |
| Monitoring | 1'210 CHF | 0–1'450 | Q | Datadog 12,60–15,10 CHF pro Server und Monat |
| Internet | 1'600 CHF | 800–2'460 | CH | Init7, Swisscom Business |
| **Versicherung** | **0,6 % des Hardwarewerts + 5 % Stempel = 1'625 CHF** | 0,3–1,0 % | S | siehe Abschnitt 2b |
| Netzwerk-Lizenz | 450 CHF | 300–600 | Q | boll.ch |
| Firmenanteil (Personal, Vertrieb, ISO 27001, Haftpflicht) | 1'200 CHF | 1'200–10'000 | S/D | Untergrenze bei sehr vielen Häusern. `FIRMA.md` rechnet die Firma einzeln: 5'400 CHF pro Haus bei 170 Häusern, 77'000 CHF bei 5 Häusern. ISO 27001: 23'000–55'000 CHF im 1. Jahr, danach 7'000–18'000 CHF (orbiqhq.com); Haftpflicht 200–1'500 CHF/Jahr (hellosafe.ch) |
| Preissteigerung laufende Kosten | 4,5 % pro Jahr | 3–6 % | D | servnetuk.com |
| Gewinnsteuer | 13,04 % | – | Q | Basel-Stadt (KPMG 2026) |

### Erlös

| Variable | Wert | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| **Vertragspreis** | **0,60 CHF pro L4-Stunde** | 0,50–0,66 CHF | E | Unbestätigter Zielpreis (`L4_ANGEBOT.md`). Einordnung: Hikube ≈ 0,68 CHF, Everyware 2,13 CHF (getdeploying.com, everyware.ch), US-Clouds mit Vertrag 0,53–0,55 CHF |
| **Fest gebuchter Anteil** | **60 %** | 42–80 % | S | siehe Abschnitt 2b |
| **Verkaufter Anteil der Rechenstunden** | **100 %** | offen | E | Annahme «genug Aufträge». Kein Nachfragebeleg; siehe Kurzfassung und Abschnitt 8 |
| Restliche Stunden als Füllauftrag | 0,29 CHF, sinkt 10 % pro Jahr | 0,29–0,38 CHF | Q | L4-Spot-Preis |
| Plattformkosten | 5 % | 0–5 % | E | Direktvertrag statt Marktplatz (15–30 %) |
| Preis im Vertrag | fest über 5 Jahre | – | E | Mehrjährige Verträge mit Abnahmepflicht sind im GPU-Markt üblich (2–5 Jahre). `PHARMA_SICHT.md` nennt 3 Jahre, der Pilot läuft 1 Jahr: Laufzeiten sind noch nicht abgeglichen (`TODO_KURZ.md`) |

## 2b. Wie die vier unsicheren Werte geschätzt sind

Für diese Posten gibt es keine öffentliche Zahl, weil sie pro Firma oder pro Objekt festgelegt werden. Sie sind deshalb aus Vergleichswerten geschätzt. Eine Offerte ersetzt die Schätzung später.

| Posten | Vergleichswert | Schätzung | Begründung |
|---|---|---|---|
| **Versicherung** | Hausrat Schweiz: Mobiliar 91,80 CHF für 110'000 CHF Summe ≈ **0,8 ‰** (hellosafe.ch); Hausrat ab 150 CHF/Jahr (comparis.ch) | **0,3–1,0 %, gerechnet 0,6 %** des Hardwarewerts, plus 5 % Stempelabgabe | Server in fremden Kellern mit Flüssigkühlung sind riskanter als Hausrat (Wasser, Überspannung, Diebstahl), dazu kommt eine Elektronikdeckung |
| **Einbau** | Schweizer Servicetechniker 143,80 CHF/h, Fahrt 1,60 CHF/km (SAK); Installation einer Wärmepumpe ohne Gerät 4'600–11'000 CHF (Deutschland, 5'000–12'000 €) | **6'400–12'800 CHF, gerechnet 9'000 CHF** | 30–60 Arbeitsstunden plus 2'000–4'000 CHF Material |
| **Kreditzins** | SNB-Leitzins 0 %, SARON ≈ 0 %; gewerbliche SARON-Kredite = SARON + Marge (SGKB, BCF, Raiffeisen); Hypothekenmarge ab 1,0 % (PostFinance); Unternehmenskredite Euroraum 3,8 % (Bundesbank) | **3,5–5,5 %, gerechnet 4,5 %** | Ein ungesicherter Kredit für Server ist riskanter als eine Hypothek. Das Modell finanziert die ganze Investition zu diesem Satz. Eigenkapital verlangt mehr, siehe Abschnitt 4 |
| **Fest gebuchter Anteil** | Cloud-Kunden binden im Median **42 %** ihrer Rechenzeit, die besten 25 % über **65 %**, Ziel vieler Firmen **70–80 %** (FinOps-Vergleiche); CoreWeave macht 96–98 % des Umsatzes mit Mehrjahresverträgen | **42–80 %, gerechnet 60 %** | Die Vergleichswerte beschreiben Käufer, nicht einen neuen Anbieter mit Winterkontingent. 60 % ist ein Ziel für die Kundengespräche, kein Messwert |

**Wirkung des fest gebuchten Anteils (Referenzhaus, 0,60 CHF, alle Stunden verkauft):**

| Fest gebucht | 0 % | 24 % | 42 % (Median) | **60 % (gerechnet)** | 80 % (Zielwert) |
|---|---|---|---|---|---|
| Ergebnis pro Jahr | −20'900 CHF | 0 | +14'800 CHF | **+29'400 CHF** | +45'600 CHF |
| Break-even | – | – | 0,45 CHF | **0,38 CHF** | 0,35 CHF |

## 3. Ergebnis pro Haus

| | Referenzhaus 8 kW | EFH 17'000 kWh, 4 kW | EFH 17'000 kWh, 5 kW |
|---|---|---|---|
| Wärmedeckung | 90,5 % | 91,5 % | 98,7 % |
| Hardware | 258'000 CHF | 129'000 CHF | 161'200 CHF |
| **Investition gesamt** | **290'100 CHF** | **151'100 CHF** | **185'800 CHF** |
| Rechenerlös im 1. Jahr | 124'400 CHF | 68'000 CHF | 73'300 CHF |
| Laufende Kosten im 1. Jahr (ohne Strom) | 9'200 CHF | 6'400 CHF | 7'100 CHF |
| **Ergebnis pro Jahr (0,60 CHF)** | **+29'400 CHF** | **+16'100 CHF** | **+12'700 CHF** |
| Ergebnis pro Jahr, vorsichtig (0,50 CHF) | +15'800 CHF | +8'700 CHF | +4'700 CHF |
| Investition zurück nach | 3,2 Jahren | 3,1 Jahren | 3,6 Jahren |
| Interner Zinsfuss | 18,8 % | 19,6 % | 14,4 % |
| **Break-even pro L4-Stunde** | **0,38 CHF** | **0,38 CHF** | **0,44 CHF** |

**Rechnung Jahr für Jahr (Referenzhaus, 0,60 CHF):**

| CHF | Jahr 1 | Jahr 2 | Jahr 3 | Jahr 4 | Jahr 5 |
|---|---|---|---|---|---|
| Erlös | 124'392 | 121'329 | 118'573 | 116'092 | 113'859 |
| Strom | −11'858 | −11'858 | −11'858 | −11'858 | −11'858 |
| Laufende Kosten | −9'209 | −12'926 | −13'507 | −21'017 | −21'963 |
| Abschreibung | −47'706 | −47'706 | −47'706 | −47'706 | −47'706 |
| Gewinn vor Steuern | 55'620 | 48'840 | 45'502 | 35'511 | 32'333 |
| Steuern | −7'253 | −6'369 | −5'933 | −4'631 | −4'216 |
| **Gewinn nach Steuern** | **48'367** | **42'471** | **39'568** | **30'881** | **28'116** |
| Geld zurück (kumuliert, nach Investition 290'120; Jahr 5 mit Restwert 51'592) | −194'048 | −103'871 | −16'597 | +61'989 | +189'403 |

**Serverzahl (Referenzhaus, 0,60 CHF):**

| Server | 6 | 7 | **8** | 9 | 10 | 13 |
|---|---|---|---|---|---|---|
| Wärmedeckung | 76,6 % | 84,5 % | **90,5 %** | 95,2 % | 98,1 % | 100 % |
| Ergebnis pro Jahr | +29'600 CHF | +30'500 CHF | **+29'400 CHF** | +27'100 CHF | +22'700 CHF | +3'000 CHF |

DH verdient am meisten mit 7 Servern. Der 8. Server kostet rund 1'100 CHF Ergebnis pro Jahr und bringt 6 Prozentpunkte Deckung, der 9. kostet weitere 2'300 CHF für knapp 5 Punkte. Das frühere Team-Ziel von 93 % Deckung erreicht das Abschaltmodell erst mit 9 Servern; im Idealmodell reichen 8 (92,95 %). Beim Durchschnitts-EFH sind 4 kW für DH besser als 5 kW (+16'100 statt +12'700 CHF), decken aber nur 91,5 % statt 98,7 %.

## 4. Bandbreite (Referenzhaus)

| | Günstig | **Gerechnet** | Teuer |
|---|---|---|---|
| Vertragspreis / fest gebucht | 0,66 CHF / 80 % | **0,60 CHF / 60 %** | 0,50 CHF / 42 % |
| Hardware | −15 % | **258'000 CHF** | +15 % |
| Kühlung pro kW | 1'260 CHF | **2'520 CHF** | 3'780 CHF |
| Einbau | 6'400 CHF | **9'000 CHF** | 12'800 CHF |
| Zins / Versicherung / GPU-Ausfälle | 3,5 % / 0,3 % / 3 % | **4,5 % / 0,6 % / 4,5 %** | 5,5 % / 1,0 % / 6,1 % |
| **Ergebnis pro Jahr** | **+69'200 CHF** | **+29'400 CHF** | **−9'400 CHF** |
| **Break-even pro L4-Stunde** | 0,28 CHF | **0,38 CHF** | 0,59 CHF |

In allen drei Spalten sind alle Rechenstunden verkauft. Diese Bandbreite deckt das Absatzrisiko also nicht ab.

**Was am meisten bewegt:**
1. **Verkaufte Stunden.** Je 10 % unverkaufte Stunden fehlen rund 10'400 CHF pro Jahr. Unter 72 % ist das Ergebnis negativ.
2. **Vertragspreis.** 10 Rappen pro L4-Stunde machen rund 13'600 CHF pro Jahr aus (0,50 CHF: +15'800, 0,60 CHF: +29'400 CHF).
3. **Fest gebuchter Anteil.** Zwischen 42 % und 80 % liegen rund 30'700 CHF pro Jahr.
4. **Preisbindung.** Fällt auch der Vertragspreis 10 % pro Jahr, fehlen rund 14'100 CHF pro Jahr.
5. **Zins.** 8 % statt 4,5 % kosten rund 6'900 CHF pro Jahr, 12 % rund 15'000 CHF.
6. **Hardwarepreis.** ±15 % sind rund ±7'200 CHF pro Jahr.
7. **Firmenkosten.** 5'400 statt 1'200 CHF pro Haus kosten rund 4'000 CHF pro Jahr, 10'000 CHF rund 8'300 CHF.
8. **Zinsspanne für Kredit und Versicherung** (3,5–5,5 % und 0,3–1,0 %). Zusammen rund ±3'000 CHF pro Jahr.
9. **Wärmepreis an den Haushalt.** Gratis oder 7 Rp./kWh macht nur rund 1'700 CHF pro Jahr aus. Gratiswärme ist für DH tragbar.

## 5. Wann es sich nicht lohnt

- **Zu wenig Aufträge.** Unter 72 % verkauften Rechenstunden ist das Ergebnis negativ. Mit der Nachfrage aus dem Alibaba-Trace verliert die Flotte Geld (Abschnitt 8).
- **Vertragspreis unter 0,38 CHF pro L4-Stunde.**
- **Weniger als rund ein Viertel der Stunden fest gebucht** (bei 0,60 CHF). Nur zum Spot-Preis verkauft: −20'900 CHF pro Jahr.
- **Kunden, die den Preis mit US-Clouds vergleichen:** Dort kostet ein fester Vertrag 0,53–0,55 CHF. Für sie muss DH auf rund 0,50 CHF (+15'800 CHF pro Jahr).
- **Teurer Fall** (0,50 CHF, nur 42 % fest gebucht, Kosten am oberen Rand): −9'400 CHF pro Jahr.
- **Nur Marktplatz statt Direktvertrag:** Mit 20 % Gebühr und Preisverfall von 10 % pro Jahr auf allen Stunden braucht es rund 0,47 CHF im ersten Jahr.
- **Vertrauliche Aufträge:** L4 schützt Daten während der Verarbeitung nicht. Solche Aufträge sind ausgeschlossen (`L4_ANGEBOT.md`). Neue H100 mit diesem Schutz rechneten sich in der früheren Rechnung selbst im günstigen Fall nicht, weil die Hardware für Dauerbetrieb gebaut ist, DH aber nur die halbe Zeit rechnet. Im Abschaltmodell ist das nicht neu gerechnet.
- **Server nur pausieren:** Bei 230 W Leerlauf rund 5'200 kWh mehr Strom (1'740 CHF) und 2'340 Rechenstunden weniger, weil die Leerlaufwärme den Speicher füllt. Das Ergebnis fällt von +29'400 auf +20'900 CHF pro Jahr. Details im [Betriebsvergleich](ERGEBNISSE.md#leerlauf-und-abschalten-im-referenzhaus).
- **Pilot mit wenigen Häusern:** Die Firmenkosten (Zertifikat, Software, Personal) verteilen sich auf wenige Häuser. Nach `FIRMA.md` trägt die Firma ihre Fixkosten ab 7 Häusern bei genug Aufträgen und erst ab 68 Häusern bei knapper Nachfrage.

## 6. Abgleich mit Joëls Kundensicht

| Joëls Frage | Antwort Säule Firma |
|---|---|
| Wer zahlt Hardware, Einbau, Strom? | DH zahlt alles, eigener Stromzähler |
| Gratiswärme möglich? | **Ja.** Kostet DH rund 1'700 CHF pro Jahr gegenüber einem Abo zu 7 Rp. |
| Einheitengrösse? | Referenzhaus 8 kW. Durchschnitts-EFH: 4 kW ist für DH besser (91,5 % Deckung), 5 kW für den Haushalt (98,7 %). Die Kundensicht, `FIRMA.md` und der Pitch rechnen mit 5 kW. **Offen, vom Team zu entscheiden** |
| Genug flexible Aufträge? | Nicht belegt. Das Modell nimmt es an (Abschnitt 8) |
| Anteil am Rechenerlös? | Im Pilot nicht nötig |
| Vertrag, Konkurs? | Die Rechnung braucht 5 Jahre Laufzeit (Abschreibung). Der Pilotvertrag der Kundensicht läuft 1 Jahr mit kostenlosem Rückbau: Für diesen Fall ist die Investition nicht gedeckt. Holzofen bleibt im Haus |

**Hardwarekosten:** Abgeglichen. `CustomerView_Joel.md` rechnet ebenfalls mit **258'000 CHF Hardware** und **290'000 CHF** gesamt für 8 kW (vorher 142'000 + 20'000 CHF ohne Quelle).

**Noch nicht abgeglichen:** Die Wärmedeckungen der Kundensicht (92,9 % und 99,6 %) stammen aus dem Idealmodell. Im Abschaltmodell sind es 90,5 % und 98,7 %, der Holzofen muss also etwas mehr liefern (`FIRMA.md`: bis 2'936 kWh pro Jahr im Referenzhaus).

## 7. Was die Rechnung genauer machen würde

| Was | Bei wem | Wirkung |
|---|---|---|
| Bezahltes Winterkontingent für einen zulässigen Workflow: Menge, Preis, Laufzeit | Gespräch mit einem ersten Kunden | grösster Hebel (±10'400 CHF pro 10 % Absatz, ±13'600 CHF pro 10 Rappen, bis 30'700 CHF bei der Festbuchung) |
| Leerlauf, Standby und Startzeit am L4-Server messen | eigener Testaufbau | mit Abschalten +28'200 CHF (350 W) bis +30'500 CHF (100 W); wichtiger ist, ob das Abschalten in der Praxis klappt, sonst +20'900 CHF |
| Server-Konfiguration 8× L4, Schweizer Preis inkl. Lieferung | Gigabyte-/Supermicro-Händler | ±7'200 CHF/Jahr |
| Finanzierung: Anteil Kredit und Eigenkapital, Zinssatz | Hausbank, Investoren | rund 2'000 CHF/Jahr pro Prozentpunkt |
| Versicherung (Inventar, Elektronik, Haftpflicht, Cyber) | Zurich, Mobiliar, AXA, Helvetia | ±1'500 CHF/Jahr |
| Einbau | Heizungsinstallateur Basel | ±1'000 CHF/Jahr |

## 8. Zusage am Vortag und Flotte mit Sportbad (Stand 21.11.2026)

**Kostenposition Fehlmenge** (`src/wirtschaft.py`):
Fehlmenge CHF = nicht gelieferte, zugesagte Server-h × 8 Karten × Vertragspreis × 50 % Gutschrift × (1 + Kostensteigerung)^(t−1).
Die fehlende Stunde wird nicht bezahlt. Zusätzlich gibt es 50 % Gutschrift. Das ist eine Schätzung: AWS EC2 schreibt je nach Ausfall 10, 30 oder 100 % der Monatsrechnung gut. Die Position ist vor Steuer abzugsfähig.

**Referenzhaus mit Zusage** (`src/scheduler/zusage.py`, `daten/ergebnisse/zusage_8_spot.json`). Diese Auswertung gibt es für das Einzelhaus nur im Idealmodell; entscheidend ist die Differenz.

| | ohne Zusage (Annahme 60 % fest) | mit Zusage am Vortag |
|---|---|---|
| Zusagbar | – | 93 % der Server-h im ganzen Jahr, **92 % im Auswertungshalbjahr** Juli–Dezember (Sicherheitsfaktor 0,95, kalibriert auf Januar–Juni) |
| Tatsächlich fest gebucht | 60 % | 59,8 % |
| Fehlmenge | 0 | 57 Server-h pro Jahr an einem Tag, Gutschrift 138 CHF im 1. Jahr |
| **Ergebnis pro Jahr (Idealmodell)** | **+34'543 CHF** | **+34'276 CHF** |

Die Zusage kostet rund 270 CHF pro Jahr. Der Betrag ist so klein, weil der Kunde im Modell nur 64 % der zugesagten Menge abnimmt. Bucht er mehr, wächst die Fehlmenge. Kalibrierung und Auswertung stützen sich auf je ein Halbjahr eines einzigen Wetterjahrs.

**Flotte: 20 Häuser + Sportbad St. Jakob im Abschaltmodell** (`src/scheduler/flotte.py --abschalten`, `daten/ergebnisse/flotte_abschalten.json`). Die Kosten des Bads sind eine Schätzung: kein neuer Speicher (das Becken speichert), Einbau 9'000 CHF pro 8 Server wie im Haus, sonst gleiche Kostensätze. Die Rechnung enthält den gesamten Strom einschliesslich Leerlauf, Standby, Starts und Migration.

| | Investition | Ergebnis pro Jahr «Nur Jobs mit Frist» (Alibaba-Nachfrage) | Ergebnis pro Jahr «Genug Aufträge» |
|---|---|---|---|
| 20 Häuser ohne Bad | 5,80 Mio. CHF | **−238'600 CHF** | +614'600 CHF |
| 20 Häuser + Bad mit 50 Servern | 7,60 Mio. CHF | **−172'000 CHF** | +737'000 CHF |

- Das Bad mit 50 Servern kostet rund 1,8 Mio. CHF und bringt der Flotte **+66'600 CHF pro Jahr** bei knapper Nachfrage und +122'500 CHF bei genug Aufträgen. 50 Server sind die Vergleichsgrösse aus dem Idealmodell; das Optimum im Abschaltmodell ist nicht gesucht.
- Mit Zusage am Vortag (genug Aufträge): 610'000 statt 614'600 CHF ohne Bad, 732'200 statt 737'000 CHF mit Bad. Zusagbar sind 91 % der Stunden (Auswertungshalbjahr: 89 % ohne, 90 % mit Bad).
- Bei knapper Nachfrage fehlen die Aufträge, nicht die Wärme. Der Router verschiebt Arbeit, er erzeugt keine neue. Darum hängt das Geschäft am Absatz (Kurzfassung, Abschnitt 5).

**Zum Vergleich: dieselbe Flotte im Idealmodell des Case** (`daten/ergebnisse/flotte.json`):

| | Investition | «Nur Jobs mit Frist» | «Genug Aufträge» |
|---|---|---|---|
| 20 Häuser ohne Bad | 5,80 Mio. CHF | −176'600 CHF | +690'500 CHF |
| 20 Häuser + Bad mit 50 Servern | 7,60 Mio. CHF | −101'400 CHF | +851'600 CHF |
| 20 Häuser + Bad mit 170 Servern (Senkenregel) | 11,90 Mio. CHF | −1'066'700 CHF | +1'203'700 CHF |

Die Firmenrechnung über 10 Jahre mit Ausbauplan, Fixkosten, Förderung und Finanzierung steht in `FIRMA.md`.

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
