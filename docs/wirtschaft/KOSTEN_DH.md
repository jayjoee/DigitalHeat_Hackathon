# Kosten und Wirtschaftlichkeit aus Sicht DigitalHeat (Stand 21.11.2026, Preismodell mit Ankerkunde)

Säule «Firma». Ergänzt Joëls Kundensicht (`CustomerView_Joel.md`), die Pharma-Sicht (`PHARMA_SICHT.md`) und die Rechnung für die ganze Firma (`FIRMA.md`). Das Angebot selbst ist in `L4_ANGEBOT.md` festgelegt. **Alle Beträge in CHF.** Dollar- und Euro-Quellen sind mit 0,84 CHF/$ und 0,92 CHF/€ umgerechnet (Mitte November 2026). Gerechnet wird mit `src/wirtschaft.py`, alle Zahlen dieses Dokuments erzeugt `src/kosten_dh.py` (Ergebnis in `daten/ergebnisse/kosten_dh.json`).

**Rechenbasis ist das Abschaltmodell**, wie in `PITCH.md`, `README.md` und `FIRMA.md`: Server ohne Arbeit werden abgeschaltet, im Leerlauf ziehen sie angenommene 230 W, im Standby 10 W, ein Start dauert 5 Minuten (`src/scheduler/serverbetrieb.py`, `ERGEBNISSE.md`, Abschnitt «Leerlauf und Abschalten im Referenzhaus»). Das Idealmodell des Case (0 W Leerlauf) steht jeweils zum Vergleich daneben.

**Neues Preismodell (21.11.2026):** Ein Ankerkunde (Roche) kauft 60 % der Server-Stunden zu **0,50 CHF pro L4-Stunde** mit Mengenrabatt und festem Preis über 5 Jahre. Die übrigen 40 % gehen an Kunden ohne Mindestmenge zu **0,55 CHF**, dieser Preis sinkt 10 % pro Jahr. Die frühere Fassung rechnete mit 0,60 CHF fest gebucht und dem Rest zum Spot-Preis von 0,294 CHF (+29'400 CHF, Break-even 0,38 CHF). `FIRMA.md`, `PITCH.md`, `README.md`, `ERGEBNISSE.md`, `PHARMA_SICHT.md`, `RESULTATE_EINFACH.md` und das 3D-Dashboard sind auf das neue Preismodell nachgeführt.

## Kurzfassung

| | Referenzhaus (31'231 kWh) | Durchschnitts-EFH (17'000 kWh), 4 kW | Durchschnitts-EFH, 5 kW |
|---|---|---|---|
| Server (je 1 kW) | **8** | 4 | 5 |
| Wärmedeckung | **90,5 %** | 91,5 % | 98,7 % |
| Verkaufte Server-Stunden pro Jahr | 34'512 | 18'873 | 20'324 |
| Investition DH | **290'100 CHF** | 151'100 CHF | 185'800 CHF |
| Wärme an den Haushalt | gratis | gratis | gratis |
| **Ergebnis DH pro Jahr** (Roche 60 % zu 0,50 CHF, Rest 0,55 CHF, alle Stunden verkauft) | **+35'000 CHF** | +19'200 CHF | +16'000 CHF |
| Vorsichtig: Rest nur zum Spot-Preis (0,294 CHF) | +15'800 CHF | +8'700 CHF | +4'700 CHF |
| Nur Roche, Rest unverkauft | −6'400 CHF | −3'400 CHF | −8'600 CHF |
| Investition zurück nach | **2,9 Jahren** | 2,9 Jahren | 3,3 Jahren |
| Interner Zinsfuss | 21,6 % | 22,5 % | 17,0 % |
| **Break-even Roche-Preis** (Rest zu 0,55 CHF) | **0,24 CHF pro L4-Stunde** (= 1,95 CHF pro Server-Stunde) | 0,24 CHF | 0,30 CHF |
| Break-even Roche-Preis, wenn der Rest nur Spot bringt | 0,38 CHF | 0,38 CHF | 0,44 CHF |
| Zum Vergleich: Idealmodell des Case (0 W Leerlauf) | 92,95 % Deckung, +40'400 CHF, Break-even 0,22 CHF | 93,6 %, +22'300 CHF | 99,6 %, +18'700 CHF |

**In einem Satz:** Wenn DigitalHeat jede Rechenstunde verkauft, 60 % an Roche zu 0,50 CHF pro L4-Stunde und den Rest zu 0,55 CHF, bleiben beim Referenzhaus rund 35'000 CHF pro Jahr nach allen Kosten, Steuern und Zinsen. Der Haushalt bekommt die Wärme gratis, die Investition ist nach knapp 3 Jahren zurück. Preise und Absatz sind Annahmen und noch mit keinem Kunden bestätigt.

### Was diese Zahl voraussetzt

Die +35'000 CHF gelten nur, wenn alle fünf Punkte zutreffen. Die ersten beiden entscheiden über das Geschäft.

1. **Jede gerechnete Stunde findet einen Käufer.** Die Server laufen, wenn das Haus Wärme braucht. Das Modell verkauft alle diese Stunden. Bleibt ein Teil unverkauft, läuft der Strom trotzdem:

   | Verkaufte Stunden | 100 % | 90 % | 80 % | 70 % | 66 % | 60 % |
   |---|---|---|---|---|---|---|
   | Ergebnis pro Jahr | **+35'000 CHF** | +24'700 CHF | +14'400 CHF | +4'100 CHF | 0 | −6'400 CHF |

   Roche nimmt seine 60 % immer ab, es fehlen Stunden aus dem Rest (gleiche Regel wie `FIRMA.md`).

   Roche allein (60 %) trägt das Haus nicht: −6'400 CHF pro Jahr. Mit der Nachfrage aus dem Alibaba-Trace ist die Flotte negativ (Abschnitt 8).
2. **Die übrigen 40 % bringen 0,55 CHF pro L4-Stunde.** Das ist der am wenigsten belegte Wert, und er trägt das Ergebnis: Bringt der Rest nur den Spot-Preis, bleiben +15'800 CHF. Die Kunden dafür (ohne Mindestmenge, unterbrechbar, Lieferung nur in Heizstunden) sind noch nicht gefunden. Nach `L4_ANGEBOT.md` rechnet DH nur öffentliche, synthetische oder vom Kunden freigegebene anonymisierte Aufgaben.
3. **Der Roche-Preis bleibt 5 Jahre fest**, während der Preis der übrigen Stunden 10 % pro Jahr fällt. Fällt auch der Roche-Preis 10 % pro Jahr, bleiben +23'200 CHF.
4. **Firmenkosten von 1'200 CHF pro Haus.** Das gilt erst bei grosser Stückzahl. `FIRMA.md` rechnet mit 5'400 CHF pro Haus bei 170 Häusern und 77'000 CHF bei 5 Häusern.
5. **4,5 % Zins**, der zugleich der Diskontsatz ist. Für ein junges Unternehmen ist das tief: bei 8 % bleiben +28'200 CHF, bei 12 % +20'300 CHF.

**Preise pro Server-Stunde (für den Pitch):** Ein Server hat 8 L4-Karten. Roche 0,50 CHF pro L4-Stunde = **4,00 CHF pro Server-Stunde**, übrige Kunden 0,55 CHF = **4,40 CHF**. Hikube 0,68 CHF = 5,44 CHF, Spot 0,294 CHF = 2,35 CHF. Im Code und in `annahmen.py` bleibt alles pro L4-Stunde, nur die Anzeige rechnet × 8.

**Drei Break-even-Zahlen:**
- Der Case definiert den Break-even als (Strom − Wert der genutzten Wärme) ÷ Server-Stunden = **0,23 CHF pro Server-Stunde** (ohne Hardware; im Abschaltmodell 0,235 CHF, im Idealmodell 0,226 CHF). Er hängt nicht vom Preismodell ab.
- Mit allen Kosten braucht DH von Roche **0,24 CHF pro L4-Stunde**, solange die übrigen Stunden 0,55 CHF bringen.
- Bringen die übrigen Stunden nur den Spot-Preis, braucht DH von Roche **0,38 CHF pro L4-Stunde** (3,07 CHF pro Server-Stunde). Das ist die vorsichtigere Zahl.

**Was «Ergebnis pro Jahr» heisst:** Kapitalwert über 5 Jahre, als gleichmässiger Jahresbetrag ausgedrückt. Enthalten sind Steuern, Zinskosten, Preisverfall der übrigen Stunden, Garantie, Restwert und Preissteigerung der laufenden Kosten. Ohne Zinskosten ist der Gewinn nach Steuern im Mittel **43'300 CHF pro Jahr**, das sind 15 % der Investition. Der interne Zinsfuss beträgt 21,6 % (Rest nur Spot: 12,4 %).

**Warum diese Preise:**
- **Roche 0,50 CHF:** Mengenrabatt für den Ankerkunden. Roche nimmt 60 % der Stunden ab, fest über 5 Jahre. Das entspricht dem Cloud-Prinzip, nach dem Kunden mit Abnahmeverpflichtung weniger zahlen. Zur Einordnung: US-Clouds mit festem Vertrag 0,53–0,55 CHF.
- **Übrige Kunden 0,55 CHF:** ohne Mindestmenge, kurze Laufzeit, Rechenzentrum in der Schweiz. Diese Kunden bekommen die schlechtere Leistung: Ihre Aufträge laufen nur, wenn das Haus Wärme braucht, und können unterbrochen werden; Roche hat Vorrang. Der Preis muss deshalb unter den Alternativen bleiben: Schweizer GPU-Clouds verlangen ab ≈ 0,68 CHF (Hikube) bis 2,13 CHF (Everyware) pro L4-Stunde, Spot kostet 0,29–0,38 CHF. Weil diese Kunden jedes Jahr neu verhandeln und L4-Preise sinken, fällt der Preis im Modell 10 % pro Jahr.
- Die Vergleichsangebote enthalten teils andere CPU-, RAM- und Serviceleistungen und sind nicht Stück für Stück verglichen. Vertrauliche Daten sind vom L4-Angebot ausgeschlossen, weil L4 keinen Schutz während der Verarbeitung bietet (`CONFIDENTIAL_COMPUTING.md`).

---

## 1. Die Formel

```
Gewinn pro Haus und Jahr = Erlös Rechnen + Erlös Wärme − Strom − laufende Kosten − Steuern
                           − (Investition − Restwert) verteilt auf 5 Jahre inkl. Zins

Erlös Rechnen = verkaufte Server-Stunden × 8 Karten × (1 − Plattform) × Verfügbarkeit
                × [Anteil Roche × Roche-Preis + Rest × Preis übrige Stunden × 0,9^(Jahr−1)]

Strom         = gesamter Verbrauch (Rechnen + Leerlauf + Standby + Starts) × Strompreis

Break-even    = der Roche-Preis, bei dem der Gewinn genau 0 ist
```

Im Code heissen die Parameter `vertragspreis_chf_karte_h` (Roche), `anteil_fest_gebucht` (Anteil Roche), `spotpreis_chf_karte_h` (übrige Stunden; der Name ist historisch) und `spot_preisverfall`.

**Nachrechnen:**

```sh
python3 src/kosten_dh.py
# Referenzhaus: 34,970 CHF/J, Rest nur Spot 15,799, Break-even Ankerkunde 0.2438 CHF/L4-h
```

Das Skript simuliert auch das Durchschnitts-EFH (`profil_haus2` aus `src/dashboard3d_daten.py`) und alle Sensitivitäten dieses Dokuments.

## 2. Annahmen

**Qualität:** **Q** = Quelle · **CH** = Schweizer Preisliste · **D** = ausländische oder Branchenwerte · **S** = Schätzung aus Vergleichswerten (Herleitung in Abschnitt 2b) · **E** = Entscheid im Team

### Haus und Betrieb

| Variable | Wert | Spanne | Qualität | Quelle |
|---|---|---|---|---|
| Verkaufte Server-Stunden Referenzhaus | 34'512 h | 36'290 h im Idealmodell | Q | Jahressimulation Basel 2025, Abschaltmodell |
| Gesamtstrom | 35'662 kWh | – | Q | davon Rechnen 34'512, Leerlauf 769, Standby 322, Starts 60 kWh |
| Genutzte Wärme | 28'272 kWh (90,5 %) | 29'027 kWh im Idealmodell | Q | Jahressimulation |
| Leerlauf, Standby, Startzeit | 230 W, 10 W, 5 min | Leerlauf 100–350 W (Ergebnis +36'100 bis +33'700 CHF) | S | Leerlauf aus einer H100-Messung abgeleitet (Latif et al. 2024). **Keine Messung an L4-Hardware** |
| Server ausschalten statt pausieren | ja | – | E | Pausieren kostet rund 8'900 CHF Ergebnis pro Jahr (Abschnitt 5) |
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
| **Roche-Preis (Ankerkunde)** | **0,50 CHF pro L4-Stunde**, fest über 5 Jahre | 0,45–0,55 CHF | E | Mengenrabatt für 60 % Abnahme. Unbestätigt. Einordnung: US-Clouds mit Vertrag 0,53–0,55 CHF |
| **Anteil Roche** | **60 %** der Server-Stunden | 42–80 % | E/S | Teamannahme «Roche kann 60 % kaufen»; siehe Abschnitt 2b |
| **Preis übrige Stunden** | **0,55 CHF pro L4-Stunde**, sinkt 10 % pro Jahr | 0,29–0,68 CHF | E | Kunden ohne Mindestmenge, unterbrechbar, wärmegeführt. Unter Hikube ≈ 0,68 CHF (getdeploying.com), über Spot 0,29–0,38 CHF. Preisverfall: H100-Index −23 % in einem Jahr (Silicon Data) |
| **Verkaufter Anteil der Rechenstunden** | **100 %** | offen | E | Annahme «genug Aufträge». Kein Nachfragebeleg; siehe Kurzfassung und Abschnitt 8 |
| Untergrenze übrige Stunden | Spot 0,29 CHF | 0,29–0,38 CHF | Q | L4-Spot-Preis (AWS g6 Spot 0,35–0,45 $); Rückfall, wenn kein Kunde ohne Mindestmenge gefunden wird |
| Plattformkosten | 5 % | 0–5 % | E | Direktvertrag statt Marktplatz (15–30 %) |
| Laufzeit Roche-Vertrag | 5 Jahre | – | E | Mehrjährige Verträge mit Abnahmepflicht sind im GPU-Markt üblich (2–5 Jahre). `PHARMA_SICHT.md` nennt 3 Jahre, der Pilot läuft 1 Jahr: Laufzeiten sind noch nicht abgeglichen (`docs/TODO.md`) |

## 2b. Wie die unsicheren Werte geschätzt sind

Für diese Posten gibt es keine öffentliche Zahl, weil sie pro Firma oder pro Objekt festgelegt werden. Sie sind deshalb aus Vergleichswerten geschätzt. Eine Offerte oder ein Vertrag ersetzt die Schätzung später.

| Posten | Vergleichswert | Schätzung | Begründung |
|---|---|---|---|
| **Versicherung** | Hausrat Schweiz: Mobiliar 91,80 CHF für 110'000 CHF Summe ≈ **0,8 ‰** (hellosafe.ch); Hausrat ab 150 CHF/Jahr (comparis.ch) | **0,3–1,0 %, gerechnet 0,6 %** des Hardwarewerts, plus 5 % Stempelabgabe | Server in fremden Kellern mit Flüssigkühlung sind riskanter als Hausrat (Wasser, Überspannung, Diebstahl), dazu kommt eine Elektronikdeckung |
| **Einbau** | Schweizer Servicetechniker 143,80 CHF/h, Fahrt 1,60 CHF/km (SAK); Installation einer Wärmepumpe ohne Gerät 4'600–11'000 CHF (Deutschland, 5'000–12'000 €) | **6'400–12'800 CHF, gerechnet 9'000 CHF** | 30–60 Arbeitsstunden plus 2'000–4'000 CHF Material |
| **Kreditzins** | SNB-Leitzins 0 %, SARON ≈ 0 %; gewerbliche SARON-Kredite = SARON + Marge (SGKB, BCF, Raiffeisen); Hypothekenmarge ab 1,0 % (PostFinance); Unternehmenskredite Euroraum 3,8 % (Bundesbank) | **3,5–5,5 %, gerechnet 4,5 %** | Ein ungesicherter Kredit für Server ist riskanter als eine Hypothek. Das Modell finanziert die ganze Investition zu diesem Satz. Eigenkapital verlangt mehr, siehe Abschnitt 4 |
| **Anteil Roche** | Cloud-Kunden binden im Median **42 %** ihrer Rechenzeit, die besten 25 % über **65 %**, Ziel vieler Firmen **70–80 %** (FinOps-Vergleiche); CoreWeave macht 96–98 % des Umsatzes mit Mehrjahresverträgen | **60 %** (Teamannahme) | Die Vergleichswerte beschreiben Käufer, nicht einen neuen Anbieter mit Winterkontingent. 60 % ist ein Ziel für das Gespräch mit Roche, kein Messwert |
| **Preis übrige Stunden** | Hikube ≈ 0,68 CHF, Everyware 2,13 CHF, US-Clouds mit Vertrag 0,53–0,55 CHF, Spot 0,29–0,38 CHF pro L4-Stunde | **0,55 CHF, sinkt 10 % pro Jahr** | Etwas über Roche, weil ohne Mindestmenge und Laufzeit; unter allen Schweizer GPU-Clouds, weil unterbrechbar und nur in Heizstunden geliefert |

**Wirkung des Roche-Anteils (Referenzhaus, alle Stunden verkauft):**

| Anteil Roche | 0 % | 42 % | **60 % (gerechnet)** | 80 % | 100 % |
|---|---|---|---|---|---|
| Rest zu 0,55 CHF | +28'800 CHF | +33'100 CHF | **+35'000 CHF** | +37'000 CHF | +39'100 CHF |
| Rest nur Spot | −20'900 CHF | +5'300 CHF | +15'800 CHF | +27'400 CHF | +39'100 CHF |

Obwohl Roche weniger pro Stunde zahlt, steigt das Ergebnis mit dem Roche-Anteil leicht: Der Roche-Preis bleibt 5 Jahre fest, der Preis der übrigen Stunden fällt und liegt im Mittel der 5 Jahre bei 0,45 CHF. Vor allem senkt ein hoher Roche-Anteil das Absatzrisiko: Findet DH für den Rest nur Spot-Käufer, hängt alles am Roche-Anteil (zweite Zeile).

## 3. Ergebnis pro Haus

| | Referenzhaus 8 kW | EFH 17'000 kWh, 4 kW | EFH 17'000 kWh, 5 kW |
|---|---|---|---|
| Wärmedeckung | 90,5 % | 91,5 % | 98,7 % |
| Hardware | 258'000 CHF | 129'000 CHF | 161'200 CHF |
| **Investition gesamt** | **290'100 CHF** | **151'100 CHF** | **185'800 CHF** |
| Rechenerlös im 1. Jahr | 135'400 CHF | 74'100 CHF | 79'800 CHF |
| Laufende Kosten im 1. Jahr (ohne Strom) | 9'200 CHF | 6'400 CHF | 7'100 CHF |
| **Ergebnis pro Jahr** | **+35'000 CHF** | **+19'200 CHF** | **+16'000 CHF** |
| Ergebnis pro Jahr, Rest nur Spot | +15'800 CHF | +8'700 CHF | +4'700 CHF |
| Investition zurück nach | 2,9 Jahren | 2,9 Jahren | 3,3 Jahren |
| Interner Zinsfuss | 21,6 % | 22,5 % | 17,0 % |
| **Break-even Roche-Preis** (Rest 0,55 / Rest Spot) | **0,24 / 0,38 CHF** | **0,24 / 0,38 CHF** | **0,30 / 0,44 CHF** |

**Rechnung Jahr für Jahr (Referenzhaus):**

| CHF | Jahr 1 | Jahr 2 | Jahr 3 | Jahr 4 | Jahr 5 |
|---|---|---|---|---|---|
| Erlös | 135'435 | 129'705 | 124'548 | 119'907 | 115'730 |
| Strom | −11'858 | −11'858 | −11'858 | −11'858 | −11'858 |
| Laufende Kosten | −9'209 | −12'926 | −13'507 | −21'017 | −21'963 |
| Abschreibung | −47'706 | −47'706 | −47'706 | −47'706 | −47'706 |
| Gewinn vor Steuern | 66'663 | 57'216 | 51'478 | 39'327 | 34'204 |
| Steuern | −8'693 | −7'461 | −6'713 | −5'128 | −4'460 |
| **Gewinn nach Steuern** | **57'970** | **49'755** | **44'765** | **34'199** | **29'744** |
| Geld zurück (kumuliert, nach Investition 290'120; Jahr 5 mit Restwert 51'592) | −184'444 | −86'983 | +5'488 | +87'392 | +216'433 |

**Serverzahl (Referenzhaus):**

| Server | 6 | 7 | **8** | 9 | 10 | 13 |
|---|---|---|---|---|---|---|
| Wärmedeckung | 76,6 % | 84,5 % | **90,5 %** | 95,2 % | 98,1 % | 100 % |
| Ergebnis pro Jahr | +34'400 CHF | +35'700 CHF | **+35'000 CHF** | +32'900 CHF | +28'700 CHF | +9'100 CHF |

DH verdient am meisten mit 7 Servern. Der 8. Server kostet rund 800 CHF Ergebnis pro Jahr und bringt 6 Prozentpunkte Deckung, der 9. kostet weitere 2'000 CHF für knapp 5 Punkte. Das Team bleibt bei 8 Servern, weil die Wärmedeckung im Case zuerst bewertet wird. Das frühere Team-Ziel von 93 % Deckung erreicht das Abschaltmodell erst mit 9 Servern; im Idealmodell reichen 8 (92,95 %). Beim Durchschnitts-EFH sind 4 kW für DH besser als 5 kW (+19'200 statt +16'000 CHF), decken aber nur 91,5 % statt 98,7 %.

## 4. Bandbreite (Referenzhaus)

| | Günstig | **Gerechnet** | Teuer |
|---|---|---|---|
| Roche-Preis / Preis übrige Stunden | 0,55 / 0,65 CHF | **0,50 / 0,55 CHF** | 0,45 / 0,45 CHF |
| Hardware | −15 % | **258'000 CHF** | +15 % |
| Kühlung pro kW | 1'260 CHF | **2'520 CHF** | 3'780 CHF |
| Einbau | 6'400 CHF | **9'000 CHF** | 12'800 CHF |
| Zins / Versicherung / GPU-Ausfälle | 3,5 % / 0,3 % / 3 % | **4,5 % / 0,6 % / 4,5 %** | 5,5 % / 1,0 % / 6,1 % |
| **Ergebnis pro Jahr** | **+61'900 CHF** | **+35'000 CHF** | **+6'400 CHF** |
| **Break-even Roche-Preis** | 0,10 CHF | **0,24 CHF** | 0,40 CHF |

In allen drei Spalten sind alle Rechenstunden verkauft und Roche nimmt 60 %. Diese Bandbreite deckt das Absatzrisiko also nicht ab.

**Was am meisten bewegt:**
1. **Verkaufte Stunden.** Je 10 % unverkaufte Stunden fehlen rund 10'300 CHF pro Jahr. Unter 66 % ist das Ergebnis negativ.
2. **Preis der übrigen Stunden.** Nur Spot statt 0,55 CHF kostet rund 19'200 CHF pro Jahr; 10 Rappen machen rund 7'500 CHF aus.
3. **Roche-Preis.** 5 Rappen pro L4-Stunde machen rund 6'800 CHF pro Jahr aus (0,45 CHF: +28'200, 0,55 CHF: +41'800 CHF).
4. **Preisbindung.** Fällt auch der Roche-Preis 10 % pro Jahr, fehlen rund 11'800 CHF pro Jahr. Bleibt umgekehrt auch der Preis der übrigen Stunden fest, kommen rund 8'600 CHF dazu.
5. **Zins.** 8 % statt 4,5 % kosten rund 6'700 CHF pro Jahr, 12 % rund 14'700 CHF.
6. **Hardwarepreis.** ±15 % sind rund ±7'200 CHF pro Jahr.
7. **Firmenkosten.** 5'400 statt 1'200 CHF pro Haus kosten rund 4'000 CHF pro Jahr, 10'000 CHF rund 8'300 CHF.
8. **Zinsspanne für Kredit und Versicherung** (3,5–5,5 % und 0,3–1,0 %). Zusammen rund +2'700 bis −2'900 CHF pro Jahr.
9. **Wärmepreis an den Haushalt.** Gratis oder 7 Rp./kWh macht nur rund 1'700 CHF pro Jahr aus. Gratiswärme ist für DH tragbar.

## 5. Wann es sich nicht lohnt

- **Zu wenig Aufträge.** Unter 66 % verkauften Rechenstunden ist das Ergebnis negativ. Roche allein reicht nicht (−6'400 CHF pro Jahr). Mit der Nachfrage aus dem Alibaba-Trace verliert die Flotte Geld (Abschnitt 8).
- **Übrige Stunden nur zum Spot-Preis und Roche-Preis unter 0,38 CHF pro L4-Stunde.**
- **Kein Ankerkunde, alles nur zum Spot-Preis:** −20'900 CHF pro Jahr.
- **Teurer Fall** (Roche 0,45 CHF, übrige Stunden 0,45 CHF, Kosten am oberen Rand): nur noch +6'400 CHF pro Jahr.
- **Nur Marktplatz statt Direktvertrag:** Mit 20 % Gebühr und Preisverfall von 10 % pro Jahr auf allen Stunden braucht es rund 0,47 CHF im ersten Jahr.
- **Vertrauliche Aufträge:** L4 schützt Daten während der Verarbeitung nicht. Solche Aufträge sind ausgeschlossen (`L4_ANGEBOT.md`). Neue H100 mit diesem Schutz rechneten sich in der früheren Rechnung selbst im günstigen Fall nicht, weil die Hardware für Dauerbetrieb gebaut ist, DH aber nur die halbe Zeit rechnet. Im Abschaltmodell ist das nicht neu gerechnet.
- **Server nur pausieren:** Bei 230 W Leerlauf rund 5'200 kWh mehr Strom (1'740 CHF) und 2'340 Rechenstunden weniger, weil die Leerlaufwärme den Speicher füllt. Das Ergebnis fällt von +35'000 auf +26'100 CHF pro Jahr. Details im [Betriebsvergleich](../ergebnisse/ERGEBNISSE.md#leerlauf-und-abschalten-im-referenzhaus).
- **Pilot mit wenigen Häusern:** Die Firmenkosten (Zertifikat, Software, Personal) verteilen sich auf wenige Häuser. Laut `FIRMA.md` trägt die Firma ihre Fixkosten ab 6 Häusern, wenn alle Stunden verkauft sind, und erst ab 45 Häusern, wenn nur Roche abnimmt (knappe Nachfrage).

## 6. Abgleich mit Joëls Kundensicht

| Joëls Frage | Antwort Säule Firma |
|---|---|
| Wer zahlt Hardware, Einbau, Strom? | DH zahlt alles, eigener Stromzähler |
| Gratiswärme möglich? | **Ja.** Kostet DH rund 1'700 CHF pro Jahr gegenüber einem Abo zu 7 Rp. |
| Einheitengrösse? | Referenzhaus 8 kW. Durchschnitts-EFH: 4 kW ist für DH besser (91,5 % Deckung), 5 kW für den Haushalt (98,7 %). Die Kundensicht, `FIRMA.md` und der Pitch rechnen mit 5 kW. **Offen, vom Team zu entscheiden** |
| Genug flexible Aufträge? | Nicht belegt. Das Modell nimmt es an (Abschnitt 8) |
| Anteil am Rechenerlös? | Im Pilot nicht nötig |
| Vertrag, Konkurs? | Die Rechnung braucht 5 Jahre Laufzeit (Abschreibung, Roche-Vertrag). Der Pilotvertrag der Kundensicht läuft 1 Jahr mit kostenlosem Rückbau: Für diesen Fall ist die Investition nicht gedeckt. Holzofen bleibt im Haus |

**Hardwarekosten:** Abgeglichen. `CustomerView_Joel.md` rechnet ebenfalls mit **258'000 CHF Hardware** und **290'000 CHF** gesamt für 8 kW (vorher 142'000 + 20'000 CHF ohne Quelle).

**Noch nicht abgeglichen:** Die Wärmedeckungen der Kundensicht (92,9 % und 99,6 %) stammen aus dem Idealmodell. Im Abschaltmodell sind es 90,5 % und 98,7 %, der Holzofen muss also etwas mehr liefern (`FIRMA.md`: bis 2'936 kWh pro Jahr im Referenzhaus).

## 7. Was die Rechnung genauer machen würde

| Was | Bei wem | Wirkung |
|---|---|---|
| Kunden für die übrigen 40 %: Menge, Preis, Bereitschaft zu Unterbruch und Winterlieferung | Hochschulen, Forschungsgruppen, Rendering, KI-Startups | grösster Hebel (bis 19'200 CHF zwischen 0,55 CHF und Spot, ±10'900 CHF pro 10 % Absatz) |
| Roche: Menge, Preis, Laufzeit, Lieferung nach Wärmeprofil | Gespräch mit Roche | ±6'800 CHF pro 5 Rappen; ohne festen Preis −11'800 CHF |
| Leerlauf, Standby und Startzeit am L4-Server messen | eigener Testaufbau | mit Abschalten +36'100 CHF (100 W) bis +33'700 CHF (350 W); wichtiger ist, ob das Abschalten in der Praxis klappt, sonst +26'100 CHF |
| Server-Konfiguration 8× L4, Schweizer Preis inkl. Lieferung | Gigabyte-/Supermicro-Händler | ±7'200 CHF/Jahr |
| Finanzierung: Anteil Kredit und Eigenkapital, Zinssatz | Hausbank, Investoren | rund 1'900 CHF/Jahr pro Prozentpunkt |
| Versicherung (Inventar, Elektronik, Haftpflicht, Cyber) | Zurich, Mobiliar, AXA, Helvetia | ±1'000 CHF/Jahr |
| Einbau | Heizungsinstallateur Basel | ±700 CHF/Jahr |

## 8. Zusage am Vortag und Flotte mit Sportbad (Stand 21.11.2026)

**Kostenposition Fehlmenge** (`src/wirtschaft.py`):
Fehlmenge CHF = nicht gelieferte, zugesagte Server-h × 8 Karten × Roche-Preis × 50 % Gutschrift × (1 + Kostensteigerung)^(t−1).
Die fehlende Stunde wird nicht bezahlt. Zusätzlich gibt es 50 % Gutschrift. Das ist eine Schätzung: AWS EC2 schreibt je nach Ausfall 10, 30 oder 100 % der Monatsrechnung gut. Die Position ist vor Steuer abzugsfähig.

**Referenzhaus mit Zusage an Roche** (`src/scheduler/zusage.py`, `daten/ergebnisse/zusage_8_spot.json`). Diese Auswertung gibt es für das Einzelhaus nur im Idealmodell; entscheidend ist die Differenz.

| | ohne Zusage (Annahme 60 % Roche) | mit Zusage am Vortag |
|---|---|---|
| Zusagbar | – | 93 % der Server-h im ganzen Jahr, **92 % im Auswertungshalbjahr** Juli–Dezember (Sicherheitsfaktor 0,95, kalibriert auf Januar–Juni) |
| Tatsächlich an Roche verkauft | 60 % | 59,8 % |
| Fehlmenge | 0 | 57 Server-h pro Jahr an einem Tag, Gutschrift 115 CHF im 1. Jahr |
| **Ergebnis pro Jahr (Idealmodell)** | **+40'400 CHF** | **+40'300 CHF** |

Die Zusage kostet rund 130 CHF pro Jahr. Der Betrag ist so klein, weil Roche im Modell nur 64 % der zugesagten Menge abnimmt. Bucht Roche mehr, wächst die Fehlmenge. Kalibrierung und Auswertung stützen sich auf je ein Halbjahr eines einzigen Wetterjahrs.

**Flotte: 20 Häuser + Sportbad St. Jakob im Abschaltmodell** (`src/scheduler/flotte.py --abschalten`, `daten/ergebnisse/flotte_abschalten.json`). Die Kosten des Bads sind eine Schätzung: kein neuer Speicher (das Becken speichert), Einbau 9'000 CHF pro 8 Server wie im Haus, sonst gleiche Kostensätze. Die Rechnung enthält den gesamten Strom einschliesslich Leerlauf, Standby, Starts und Migration.

| | Investition | Ergebnis pro Jahr «Nur Jobs mit Frist» (Alibaba-Nachfrage) | Ergebnis pro Jahr «Genug Aufträge» |
|---|---|---|---|
| 20 Häuser ohne Bad | 5,80 Mio. CHF | **−172'100 CHF** | +727'700 CHF |
| 20 Häuser + Bad mit 50 Servern | 7,60 Mio. CHF | **−78'600 CHF** | +880'000 CHF |

- Das Bad mit 50 Servern kostet rund 1,8 Mio. CHF und bringt der Flotte **+93'500 CHF pro Jahr** bei knapper Nachfrage und +152'400 CHF bei genug Aufträgen. Im Sommer übernimmt es die Aufträge, für die die Häuser keine Wärme brauchen: Statt 194'900 werden nur noch 30'200 Server-Stunden abgegeben. 50 Server sind die Vergleichsgrösse aus dem Idealmodell; das Optimum im Abschaltmodell ist nicht gesucht.
- Mit Zusage am Vortag (genug Aufträge): 725'500 statt 727'700 CHF ohne Bad, 877'700 statt 880'000 CHF mit Bad. Zusagbar sind 91 % der Stunden (Auswertungshalbjahr: 89 % ohne, 90 % mit Bad).
- Bei knapper Nachfrage fehlen die Aufträge im Winter, nicht die Wärme. Der Router verschiebt Arbeit zwischen Standorten, aber nicht vom Sommer in den Winter, und er erzeugt keine neue. Die Häuser sind dann nur zu 28 % ausgelastet. Darum hängt das Geschäft am Absatz der Winterstunden (Kurzfassung, Abschnitt 5).

**Zum Vergleich: dieselbe Flotte im Idealmodell des Case** (`daten/ergebnisse/flotte.json`):

| | Investition | «Nur Jobs mit Frist» | «Genug Aufträge» |
|---|---|---|---|
| 20 Häuser ohne Bad | 5,80 Mio. CHF | −108'700 CHF | +807'900 CHF |
| 20 Häuser + Bad mit 50 Servern | 7,60 Mio. CHF | −6'200 CHF | +1'001'100 CHF |
| 20 Häuser + Bad mit 170 Servern (Senkenregel) | 11,90 Mio. CHF | −965'500 CHF | +1'427'600 CHF |

Auch mit den neuen Preisen bleibt 50 Server die beste Badgrösse bei knapper Nachfrage (Suche über 10–80 Server).

Die Firmenrechnung über 10 Jahre mit Ausbauplan, Fixkosten, Förderung und Finanzierung steht in `FIRMA.md` (noch mit den alten Preisen).

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
