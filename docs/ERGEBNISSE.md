# Ergebnisse Referenzhaus Basel 2025 (Stand 20.11.2026)

Reproduzieren:
```
python3 src/referenzprofil.py                     # Stundenprofil aus Open-Meteo
python3 src/jobtypen.py                           # Jobtypen A und B
python3 src/scheduler/jahr.py                     # 1–13 Server, alle Szenarien → daten/ergebnisse/serverzahl.json
python3 src/scheduler/jahr.py --server 8 --stunden daten/ergebnisse/stunden_8_spot.csv
.venv/bin/python src/scheduler/live.py --tag 2025-01-15 --server 8   # echter Job, Januar
.venv/bin/python src/scheduler/live.py --tag 2025-07-15 --server 8   # echter Job, Juli
.venv/bin/python src/scheduler/live.py --tag 2025-03-07 --server 8 --sekunden 3   # Demo: Pause bei vollem Speicher
python3 src/dashboard_daten.py                    # Zahlen fürs Dashboard → dashboard/daten.js
bash dashboard/starten.sh                         # Dashboard auf http://localhost:8765
```

Das Dashboard zeigt alle Kennzahlen für 1–13 Server und beide Nachfrageszenarien. Strompreis, Vertragspreis, fest gebuchter Anteil, Serverpreis und Wärmepreis lassen sich verschieben, das Urteil «rechnet sich / rechnet sich nicht» folgt sofort. Läuft `live.py`, zeigt es den echten Prozess (rechnet oder pausiert) jede Sekunde.

**Alle Beträge in CHF.** Die Wirtschaftlichkeit von DigitalHeat rechnet `src/wirtschaft.py`; Herleitung aller Annahmen in `KOSTEN_DH.md`, Kundensicht Pharma in `PHARMA_SICHT.md`.

## Kennzahlen für 8 Server pro Haus

Szenario **Genug Aufträge**: Ein Pharma-Vertrag bucht 60 % der Stunden fest (Winterkontingent), der Rest läuft als Füllauftrag zum Spot-Preis. Typ B kommt begrenzt nach Alibaba-Trace (40 Jobs pro Tag, Frist 2 h).

| Kennzahl | Wert |
|---|---|
| Server pro Haus | **8** |
| Deckung des Wärmebedarfs (Heizung + Warmwasser, 31'231 kWh) | **93,0 %** (29'027 kWh, Rest 2'203 kWh vom Backup) |
| Abgeführte Wärme | **5 kWh** (0,02 % der Serverwärme) |
| Auslastung | **51,8 %** (36'290 Server-h ÷ 8 × 8'760) |
| Verpasste Fristen | **0,0 %** von 14'390 Jobs mit Frist |
| Stromkosten | 12'066 CHF (36'290 kWh × 0,3325) |
| Wert der genutzten Wärme | 3'861 CHF (29'027 kWh × 0,133) |
| **Break-even-Rechenpreis (Case-Definition)** | **0,226 CHF pro Server-h** = (12'066 − 3'861) ÷ 36'290, ohne Hardware |
| Investition DigitalHeat | 290'100 CHF (8 Server mit 64 L4, Kühlung, Einbau, Speicher, Netzwerk) |
| Rechenerlös im 1. Jahr | 130'800 CHF (Vertragspreis 0,60 CHF pro L4-Stunde, 60 % fest gebucht; Schweizer Clouds ab ≈ 0,68 CHF) |
| Wärme an den Haushalt | gratis (Öl-Pilot) |
| **Ergebnis DigitalHeat** | **+34'500 CHF pro Jahr** nach allen Kosten, Steuern und Zins (ohne Zins: +43'000 CHF), Rendite ≈ 21 %, Investition nach 3,0 Jahren zurück |
| Vorsichtiger Fall (0,50 CHF) | +20'300 CHF pro Jahr, Investition nach 3,6 Jahren zurück |
| **Nötiger Vertragspreis mit allen Kosten** | **0,36 CHF pro L4-Stunde** = 2,87 CHF pro Server-h |

## Warum 8 Server
| Server | 4 | 6 | **8** | 10 | 12 |
|---|---|---|---|---|---|
| Deckung | 58,1 % | 79,6 % | **93,0 %** | 99,3 % | 100 % |
| Auslastung | 64,7 % | 59,1 % | **51,8 %** | 44,2 % | 37,2 % |
| Abgeführt | 0 | 0 | **5 kWh** | 12 kWh | 28 kWh |
| Ergebnis DigitalHeat pro Jahr | 26'600 | 34'900 | **34'500** | 26'800 | 13'200 CHF |

- Bis 8 Server bringt jeder weitere Server 6–13 Prozentpunkte Deckung, der 9. nur noch 3,9.
- Die Kosten tragen die Winterstunden: Ab Server 9 laufen die zusätzlichen Server nur in wenigen kalten Stunden, die Auslastung fällt unter 50 %.
- 12,5 Server für die kälteste Stunde wären 100 % Deckung bei 37 % Auslastung.

Was jeder weitere Server zum Ergebnis von DigitalHeat beiträgt (alle Kosten, Steuern, Zins; 0,60 CHF, 60 % fest gebucht):

| Server Nr. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | **8** | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Beitrag CHF/Jahr | 7'573 | 6'734 | 6'284 | 5'991 | 5'262 | 3'045 | 708 | **−1'054** | −3'018 | −4'765 | −6'418 |

Server 1 trägt zusätzlich die Fixkosten des Hauses (Einbau, Internet, Firmenanteil). Regel: **Ein Server mehr lohnt sich, solange sein Beitrag positiv ist.** Am meisten verdient DigitalHeat mit 7 Servern (+35'600 CHF, 87,1 % Deckung). Die 8 Server für das Team-Ziel von 93 % Deckung kosten nur rund 1'000 CHF Gewinn pro Jahr und sind damit praktisch optimal. Das Dashboard zeigt diese Rechnung im Abschnitt «Lohnt sich ein Server mehr?» für jeden Preis.

## Jahresverlauf (8 Server, Spot)
| Monat | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Deckung | 86 % | 90 % | 98 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 92 % | 89 % |
| Auslastung | 97 % | 96 % | 84 % | 48 % | 22 % | 8 % | 8 % | 8 % | 20 % | 53 % | 84 % | 96 % |

Von Juni bis August laufen die Server nur noch für das Warmwasser (0,6 Server). **Das Sommerloch ist das Problem der Wirtschaftlichkeit, nicht die Deckung.**

## Wann es sich nicht lohnt
1. **Rechenpreis unter 0,226 CHF pro Server-h:** Dann deckt der Erlös nicht einmal den Strom abzüglich Wärmewert. Das gilt unabhängig von der Serverzahl, solange keine Wärme abgeführt wird.
2. **Mit allen Kosten** (Hardware, Kühlung, Einbau, Wartung, Versicherung, Steuern, Zins): Vertragspreis unter **0,36 CHF pro L4-Stunde** (= 2,87 CHF pro Server-h; Spanne 0,26–0,55 CHF) oder weniger als rund **40 % der Stunden fest gebucht**. Über einen Marktplatz statt Direktvertrag bräuchte es rund 0,50 CHF. Mit neuen H100 statt L4 verliert DigitalHeat selbst im günstigen Fall Geld.
3. **Ohne flexible Nachfrage (Szenario Alibaba):** Kommen alle Jobs mit Frist nach Alibaba-Trace, sinkt die Deckung bei 8 Servern auf 51,7 %. Im Sommer müssen 7'506 kWh Wärme abgeführt werden, weil die Jobs vor ihrer Frist laufen müssen. Der Break-even steigt auf 0,260 CHF.
   Mit der Regel «abgeben» gehen 9'608 Jobs (8'990 Server-h) an andere Standorte. Abgeführt werden nur noch 316 kWh. **Genau diese 9'000 Server-h im Sommer bräuchten einen Abnehmer mit Sommerwärmebedarf** (Hotel mit Spa, Maistrockner).

## Scheduler (Muss-Kriterium 2)
- Kern: `src/scheduler/kern.py`, Funktion `entscheide`. Pro Stunde: Pflichtjobs (Frist in Gefahr, 2 h Puffer) zuerst, dann nach frühester Frist so viel Arbeit, bis Wärmebedarf plus freier Speicher gedeckt sind. Pausierbare Jobs halten mitten in der Arbeit an.
- Speicher: 35 kWh, verlustfrei. Überschuss füllt den Speicher, erst dann wird abgeführt.
- Wärme nicht gebraucht und Frist drängt: Regel `rechnen` (Wärme abführen) oder `abgeben` (Job geht an einen anderen Standort, kein Erlös hier).
- Derselbe Kern steuert den echten Prozess (`src/scheduler/live.py`) über `Haus.schritt`:
  - Januar: alle 8 Server laufen durchgehend, der echte Job rechnet die ganze Stunde.
  - Juli: Speicher voll, nur Warmwasser. Der Scheduler fährt 0,62 Server, der echte Job läuft 62 % jeder Stunde und ist sonst mit SIGSTOP pausiert.
  - **Für die Demo besser: 7. März 2025.** `live.py` wählt automatisch den 8. Server (stärkste Schwankung). Er rechnet bis 14 Uhr voll, pausiert von 14 bis 21 Uhr ganz, weil der Speicher voll ist, und läuft abends wieder an. So sieht man Pause und Weiterlauf auf dem Wärmesignal, nicht nur einen gleichmässigen Takt.
  - Am Ende SIGTERM → Checkpoint. Der nächste Lauf macht dort weiter (getestet: 2'688 → 4'864 → 6'528 Texte).

## Annahmen und Grenzen
Alle Annahmen mit Quelle stehen in `src/scheduler/annahmen.py` und in jeder Ergebnisdatei (`daten/ergebnisse/serverzahl.json`, Feld `annahmen`). Die wichtigsten:
- **Genug Aufträge** (Szenario Standard): Ein Pharma-Vertrag bucht 60 % der Stunden fest, der Rest findet als Füllauftrag zum Spot-Preis Abnehmer. Das ist die stärkste Annahme. Das Szenario Alibaba zeigt, was ohne sie passiert.
- Vertragspreis 0,60 CHF pro L4-Stunde für Kunden mit Datenstandort Schweiz (rund 12 % unter Schweizer GPU-Clouds; vorsichtig 0,50 CHF), Server mit 8 L4 für 32'245 CHF (belegter Komplettpreis), 5 Jahre, Zins 4,5 %, Restwert 20 %. Alle Werte mit Quelle in `src/scheduler/annahmen.py` und `KOSTEN_DH.md`.
- Die Case-Kennzahl «Break-even» bleibt ohne Hardware (0,226 CHF pro Server-h); daneben steht der nötige Preis mit allen Kosten (2,87 CHF pro Server-h).
- Keine Wetterprognose: Bei verlustfreiem Speicher und unbegrenzten Aufträgen A ist «Speicher immer füllen» schon die beste Deckung. Eine Prognose bringt erst etwas, wenn Aufträge knapp sind oder der Speicher Verluste hat.
- Wärmeabgabe = Strom × 0,8, unabhängig von der Auslastung der GPU im Server. Läuft ein Server, läuft er voll (Alibaba zeigt im Median 4 % GPU-Nutzung: Jobs müssen dicht gepackt werden).
- Stündliche Auflösung, perfekte Kenntnis des Bedarfs der laufenden Stunde, keine Prognose über die Stunde hinaus.
- Speicher ohne Verluste, Warmwasser gleichmässig über den Tag (0,5 kWh pro Stunde).
- Ankünfte nach Alibaba-Tagesform in UTC+8, nicht auf Basel umgerechnet.

## Day-ahead-Zusage (Stand 21.11.2026, `src/scheduler/zusage.py`)
Frage: Wie viele Server-Stunden kann DigitalHeat einen Tag im Voraus verbindlich zu 0,60 CHF pro L4-h (= 4,80 CHF pro Server-h) verkaufen?
- Entscheid um 12 Uhr Ortszeit am Vortag. Prognose: Open-Meteo «Previous Runs», ECMWF IFS 0,25°. Genutzt werden nur Läufe, die zum Entscheid schon veröffentlicht waren (konservativ 8 h Verzug, Test für jede Stunde). Der Vortagslauf ist genauer als der Lauf zwei Tage vorher: mittlerer Fehler 0,84 °C gegenüber 0,95 °C.
- Für 2024 gibt es keine Previous Runs. Darum: kalibriert auf Januar–Juni 2025, ausgewertet auf Juli–Dezember 2025.
- **Referenzhaus, 8 Server:** Sicherheitsfaktor 0,95. **93 % der Server-h sind zusagbar**, die angenommenen 60 % fest gebucht sind also gedeckt. Fehlmenge an 2,2 % der Tage ausserhalb der Kalibrierung, 57 Server-h im Jahr. Gutschrift: 50 % des Vertragspreises (Schätzung). **Ergebnis 34'276 CHF pro Jahr statt 34'543 CHF.**
- Damit ist die Preisprämisse belegt und nicht nur angenommen. Offen bleibt die Nachfrage: Zusagbar heisst noch nicht verkauft.
- Daten: `daten/ergebnisse/zusage_8_spot.json`.

## Wärme-Router: Flotte mit Sommer-Senke (Stand 21.11.2026, `src/scheduler/router.py`, `flotte.py`)
Flotte: 20 × Referenzhaus mit je 8 Servern (Serverregel, Test). Ein gemeinsamer Auftragspool, der Router verteilt die Aufträge auf die Standorte. Der Kern `entscheide()` ist unverändert. Regel bei Überschuss: abgeben (Wärme zuerst).
**Vorrang (Team-Entscheid 21.11.2026): Wohnhäuser haben bei der Zuteilung immer Vorrang. Das Bad nimmt nur Rechenlast auf, die kein Haus als Wärme brauchen kann.** Ein Haus darf dafür auch einen angefangenen Job vom Bad zurückholen.
Senke: **Sportbad St. Jakob**, offen 26.4.–5.10.2025, ca. 650 MWh pro Jahr (Schätzung ±30 %, `daten/HALLENBAD.md`). Ein Hallenbad scheidet aus, weil das Rialto Sommerpause hat und das Hallenbad Eglisee nur im Winter steht.

| Szenario «Nur Jobs mit Frist» | 0 Senken | Sportbad 50 Server (nach Nachfrage) | Sportbad 170 Server (Senkenregel) |
|---|---|---|---|
| Wärme der Häuser gedeckt | 51,5 % | 50,9 % | 50,7 % |
| Auslastung Haus-Server | 29,2 % | 28,7 % | 28,3 % |
| Auslastung Bad-Server (übers Jahr) | – | 39,6 % | 12,6 % |
| An andere Cloud abgegebene Arbeit | 179'870 Server-h | **12'507 Server-h** | 5'249 Server-h |
| Migrationen | 0 | 3'457 | 2 |
| Verpasste Fristen | 0 % | 0 % | 0 % |
| Ergebnis DigitalHeat | −176'618 CHF/J | **−101'372 CHF/J** | −1'066'667 CHF/J |

| Szenario «Genug Aufträge» (Spot) | 0 Senken | Sportbad 50 | Sportbad 170 |
|---|---|---|---|
| Ergebnis DigitalHeat | 690'540 CHF/J | 851'590 CHF/J | 1'203'657 CHF/J |
| mit Day-ahead-Zusage (60 % fest, Fehlmenge) | 685'220 CHF/J | 846'393 CHF/J | – |

**Befunde**
1. **Der Router schliesst das Sommerloch nur, wenn es genug Aufträge gibt.** Ohne Senke gibt die Flotte 179'870 Server-h an andere Clouds ab, weil die Häuser im Sommer keine Wärme brauchen. Ein Sportbad mit 50 Servern nimmt 93 % davon auf. Das verbessert das Ergebnis um rund **75'000 CHF pro Jahr**. Bei Nachfrage nach Alibaba bleibt die Flotte trotzdem im Minus: Der Engpass ist die Nachfrage, nicht die Wärme.
2. **Die Senkenregel aus dem Design-Doc ist falsch dimensioniert.** Sie richtet die Serverzahl nach dem Wärmebedarf (170 Server) statt nach den Aufträgen. Die richtige Grösse ergibt sich aus der Nachfrage: bestes Ergebnis bei 50 Servern (gesucht von 10 bis 80, `suche_senkengroesse_alibaba`). Nur wenn es unbegrenzt Aufträge gibt (Spot), lohnt jeder zusätzliche Server.
3. **Die Häuser behalten ihre Wärme.** Weil sie Vorrang haben, sinkt ihre Deckung mit Bad nur von 51,5 % auf 50,9 %. Die Häuser haben in jeder Stunde Vorrang. Was das Bad zu einer Zeit rechnet, in der kein Haus Wärme braucht, fehlt einem Haus manchmal ein paar Stunden später. Ohne die Vorrang-Regel lag die Deckung bei 47,5 %, und das Bad holte sich im Mai und September die Arbeit der Häuser.
4. **Gleiche Häuser gleichen sich nicht aus.** 20 gleiche Häuser mit gleichem Wetter rechnen so viel wie 20 einzelne Häuser (Test, Abweichung < 0,1 %). Der Nutzen der Verteilung entsteht erst mit einem Standort, der zu anderen Zeiten Wärme braucht.
5. **Migration ist echt und verlustfrei.** Der echte Job wurde nach 2'688 von 5'000 Texten mit SIGTERM angehalten und als neuer Prozess fortgesetzt. Die Vektoren sind identisch, Abweichung 0,0 (`tests/vektorvergleich.py`, `messungen/vektorvergleich.json`). Neustart bis rechenbereit: 0,28 s. Bis der laufende Block fertig ist: 1,4 s mit 6 Threads, 6,4 s mit 1 Thread. Die 3'457 Migrationen pro Jahr kosten damit zusammen rund 2 kWh.

**Grenzen:** Der Wärmebedarf des Bads ist eine Schätzung, ohne Lehrschwimmbecken und Duschen. Ins Becken als Speicher passen 1'200 kWh (Schätzung). Das Bad hat in der Zusage keinen Prognosefehler (Monatsprofil). Die Migration rechnet ohne Übertragung über das Netz. Die Typ-B-Ankünfte im Pool sind anders gezogen als in 20 einzelnen Häusern.

**Reproduzieren:** `python3 src/scheduler/zusage.py`, `python3 src/scheduler/flotte.py` (≈ 5 min), Tests `python3 -m unittest discover -s tests` (22 Tests), Vektorvergleich `.venv/bin/python tests/vektorvergleich.py` (≈ 8 min).
