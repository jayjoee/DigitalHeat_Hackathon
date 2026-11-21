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

Firmenrechnung mit Ausbau, Skaleneffekten, Förderbeitrag und Holzofen: `docs/wirtschaft/FIRMA.md`.

## Kennzahlen für 8 Server pro Haus

Szenario **Genug Aufträge**: Roche bucht 60 % der Stunden fest (Winterkontingent) zu 0,50 CHF pro L4-Stunde, die übrigen Stunden gehen zu 0,55 CHF an Kunden ohne Mindestmenge. Typ B kommt begrenzt nach Alibaba-Trace (40 Jobs pro Tag, Frist 2 h).

| Kennzahl | Wert |
|---|---|
| Server pro Haus | **8** |
| Deckung des Wärmebedarfs (Heizung + Warmwasser, 31'231 kWh) | **93,0 %** (29'027 kWh, Rest 2'203 kWh vom vorhandenen Holzofen, keine Ölheizung mehr) |
| Abgeführte Wärme | **5 kWh** (Case-Idealwert bei 0 W Leerlauf, 0,02 % der Serverwärme) |
| Auslastung | **51,8 %** (36'290 Server-h ÷ 8 × 8'760) |
| Verpasste Fristen | **0,0 %** von 14'390 Jobs mit Frist |
| Stromkosten | 12'066 CHF (36'290 kWh × 0,3325) |
| Wert der genutzten Wärme | 3'861 CHF (29'027 kWh × 0,133) |
| **Break-even-Rechenpreis (Case-Definition)** | **0,226 CHF pro Server-h** = (12'066 − 3'861) ÷ 36'290, ohne Hardware |
| Investition DigitalHeat | 290'100 CHF (8 Server mit 64 L4, Kühlung, Einbau, Speicher, Netzwerk) |
| Rechenerlös im 1. Jahr | 135'400 CHF (Roche 60 % zu 0,50 CHF pro L4-Stunde, Rest 0,55 CHF; Schweizer Clouds ab ≈ 0,68 CHF) |
| Wärme an den Haushalt | gratis (Pilot in ehemaligen Öl-Häusern, vorhandener Holzofen als Reserve) |
| **Ergebnis DigitalHeat** | **+35'000 CHF pro Jahr** im Abschaltmodell (230 W Leerlauf, 90,5 % Deckung, 34'512 verkaufte Server-h) nach allen Kosten, Steuern und Zins; interner Zinsfuss 21,6 %, Investition nach 2,9 Jahren zurück. Im Idealmodell dieser Tabelle (0 W Leerlauf): +40'400 CHF. Preise: Roche 60 % zu 0,50 CHF pro L4-h, Rest 0,55 CHF. Voraussetzung in beiden Fällen: jede Rechenstunde ist verkauft (`KOSTEN_DH.md`) |
| Rest nur zum Spot-Preis (0,294 CHF) | +15'800 CHF pro Jahr, Investition nach 3,9 Jahren zurück (Idealmodell: +20'300 CHF, 3,6 Jahre) |
| **Nötiger Roche-Preis mit allen Kosten** | **0,24 CHF pro L4-Stunde**, wenn der Rest 0,55 CHF bringt; **0,38 CHF** (= 3,07 CHF pro Server-h), wenn der Rest nur den Spot-Preis bringt (`KOSTEN_DH.md`) |

## Leerlauf und Abschalten im Referenzhaus

Beide Strategien nutzen dasselbe Wetter, dieselbe Auftragsfolge und den 35-kWh-Speicher. Beim **Pausieren** bleiben acht Server bereit. Beim **Abschalten** schaltet das Modell je nach Wärmebedarf und Fristen nur die benötigten Server ein. Bei höchstens 35 % Speicherfüllung beginnt die Ladephase, ab 85 % endet sie. Fristkritische Aufträge können auch bei vollem Tank einen Server starten. Ein Server bleibt nach der letzten Anforderung eine Stunde bereit.

Die Annahmen pro Server sind 1’000 W unter Last, 100/230/350 W im Leerlauf, 10 W im Standby und fünf Minuten Startzeit. Während des Starts zieht der Server im Modell 1’000 W und kann noch keine Jobs ausführen. Für Last, Leerlauf und Start gelten je 80 % Wärmerückgewinnung. Die Standby-Leistung zählt zum Stromverbrauch, dem Wassertank wird daraus keine Wärme gutgeschrieben. Die 230 W sind aus einer H100-Messung abgeleitet. Für die L4-Konfiguration liegen noch keine Messungen vor.

| Genug Aufträge | Leerlauf je Server | Strom pro Jahr | Abgeführte Wärme | Wärmedeckung | Fristen verpasst |
|---|---:|---:|---:|---:|---:|
| Case-Idealmodell | 0 W | 36’290 kWh | 5 kWh | 93,0 % | 0 |
| Jobs pausieren | 100 W | 36’891 kWh | 1’083 kWh | 91,0 % | 0 |
| Server abschalten | 100 W | 35’552 kWh | <1 kWh | 90,3 % | 0 |
| Jobs pausieren | 230 W | 40’890 kWh | 4’191 kWh | 91,3 % | 0 |
| Server abschalten | 230 W | 35’662 kWh | <1 kWh | 90,5 % | 0 |
| Jobs pausieren | 350 W | 44’623 kWh | 7’098 kWh | 91,6 % | 0 |
| Server abschalten | 350 W | 35’777 kWh | <1 kWh | 90,8 % | 0 |

Bei 230 W spart das Abschalten rund **5’200 kWh bzw. 1’740 CHF Strom pro Jahr**. Die Wärmedeckung sinkt gegenüber dem Pausieren um **0,8 Prozentpunkte**. Die Case-Kostenschwelle beträgt rund **0,23 CHF pro Rechenstunde** beim Abschalten und **0,30 CHF** beim Pausieren. Leerlauf und Standby verursachen Kosten, während nur die Rechenstunden als Erlösgrundlage zählen.

Bei **nur Jobs mit Frist** (Alibaba-Szenario) fallen bei 230 W auch mit Abschalten **8’760 kWh** abgeführte Wärme an, gegenüber **10’969 kWh** beim Pausieren. Fristkritische Jobs laufen in diesem Vergleich lokal, auch wenn der Tank voll ist. In beiden Strategien wurden alle fälligen Fristen des Referenzjahrs eingehalten.

Der Einzelhausvergleich bildet die lokale Ausführung ab. Der Wärme-Router nutzt dieselbe Abschaltlogik auch für die [Flotte mit Sportbad](#flotte-mit-bedarfsgerechtem-abschalten). Vor einem Pilotbetrieb müssen Startzeit bis zur Jobbereitschaft und Leistung in allen Betriebszuständen am L4-System gemessen werden, ebenso der Strombedarf der Kühlung.

**Reproduzieren:** `python3 -m src.scheduler.serverbetrieb --ausgabe daten/ergebnisse/serverbetrieb.json`. Die Optionen `--leerlauf-watt`, `--standby-watt` und `--start-minuten` erlauben eigene Szenarien.

## Warum 8 Server
| Server | 4 | 6 | **8** | 10 | 12 |
|---|---|---|---|---|---|
| Deckung | 58,1 % | 79,6 % | **93,0 %** | 99,3 % | 100 % |
| Auslastung | 64,7 % | 59,1 % | **51,8 %** | 44,2 % | 37,2 % |
| Abgeführt | 0 | 0 | **5 kWh** | 12 kWh | 28 kWh |
| Ergebnis DigitalHeat pro Jahr | 30'200 | 39'900 | **40'400** | 33'000 | 19'500 CHF |

- Bis 8 Server bringt jeder weitere Server 6–13 Prozentpunkte Deckung, der 9. nur noch 3,9.
- Die Kosten tragen die Winterstunden: Ab Server 9 laufen die zusätzlichen Server nur in wenigen kalten Stunden, die Auslastung fällt unter 50 %.
- 12,5 Server für die kälteste Stunde wären 100 % Deckung bei 37 % Auslastung.

Was jeder weitere Server zum Ergebnis von DigitalHeat beiträgt (alle Kosten, Steuern, Zins; Roche 60 % zu 0,50 CHF, Rest 0,55 CHF):

| Server Nr. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | **8** | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Beitrag CHF/Jahr | 8'807 | 7'568 | 7'091 | 6'781 | 6'008 | 3'659 | 1'182 | **−685** | −2'765 | −4'616 | −6'369 |

Server 1 trägt zusätzlich die Fixkosten des Hauses (Einbau, Internet, Firmenanteil). Regel: **Ein Server mehr lohnt sich, solange sein Beitrag positiv ist.** Am meisten verdient DigitalHeat mit 7 Servern (+41'100 CHF, 87,1 % Deckung). Die 8 Server für das Team-Ziel von 93 % Deckung kosten nur rund 700 CHF Gewinn pro Jahr und sind damit praktisch optimal. Beide Tabellen stammen aus dem Idealmodell. Im Abschaltmodell bleibt die Reihenfolge gleich: 7 Server +35'700 CHF (84,5 % Deckung), 8 Server +35'000 CHF (90,5 %), 9 Server +32'900 CHF (95,2 %); siehe `KOSTEN_DH.md`, Abschnitt 3. Das Dashboard zeigt diese Rechnung im Abschnitt «Lohnt sich ein Server mehr?» für jeden Preis.

## Jahresverlauf (8 Server, Spot)
| Monat | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Deckung | 86 % | 90 % | 98 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 92 % | 89 % |
| Auslastung | 97 % | 96 % | 84 % | 48 % | 22 % | 8 % | 8 % | 8 % | 20 % | 53 % | 84 % | 96 % |

Von Juni bis August laufen die Server nur noch für das Warmwasser (0,6 Server). **Das Sommerloch ist das Problem der Wirtschaftlichkeit, nicht die Deckung.**

## Wann es sich nicht lohnt
1. **Rechenpreis unter 0,226 CHF pro Server-h:** Dann deckt der Erlös nicht einmal den Strom abzüglich Wärmewert. Das gilt unabhängig von der Serverzahl, solange keine Wärme abgeführt wird.
2. **Mit allen Kosten** (Hardware, Kühlung, Einbau, Wartung, Versicherung, Steuern, Zins): Roche-Preis unter **0,24 CHF pro L4-Stunde** bei 0,55 CHF für den Rest, unter **0,38 CHF**, wenn der Rest nur den Spot-Preis bringt, oder weniger als **68 % der Rechenstunden verkauft** (`KOSTEN_DH.md`). Über einen Marktplatz statt Direktvertrag bräuchte es rund 0,47 CHF. Mit neuen H100 statt L4 verliert DigitalHeat selbst im günstigen Fall Geld.
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
- **Genug Aufträge** (Szenario Standard): Roche bucht 60 % der Stunden fest, die übrigen Stunden finden Abnehmer zu 0,55 CHF pro L4-Stunde. Das ist die stärkste Annahme. Das Szenario Alibaba zeigt, was ohne sie passiert.
- Ankerkunde Roche 60 % zu 0,50 CHF pro L4-Stunde fest, übrige Stunden 0,55 CHF mit −10 % pro Jahr, als unbestätigte Zielpreise für öffentliche und freigegebene, nicht vertrauliche Aufgaben (`L4_ANGEBOT.md`; Schweizer GPU-Clouds ab ≈ 0,68 CHF, vorsichtig: Rest zum Spot-Preis 0,294 CHF), Server mit 8 L4 für 32'245 CHF (belegter Komplettpreis), 5 Jahre, Zins 4,5 %, Restwert 20 %. Alle Werte mit Quelle in `src/scheduler/annahmen.py` und `KOSTEN_DH.md`.
- Die Case-Kennzahl «Break-even» bleibt ohne Hardware (0,226 CHF pro Server-h); daneben steht der nötige Roche-Preis mit allen Kosten: 1,95 CHF pro Server-h im Abschaltmodell (1,75 CHF im Idealmodell), wenn die übrigen Stunden 0,55 CHF bringen. Bringen sie nur den Spot-Preis von 0,294 CHF, sind es 3,07 CHF (2,87 CHF).
- Keine Wetterprognose: Bei verlustfreiem Speicher und unbegrenzten Aufträgen A ist «Speicher immer füllen» schon die beste Deckung. Eine Prognose bringt erst etwas, wenn Aufträge knapp sind oder der Speicher Verluste hat.
- Wärmeabgabe = Strom × 0,8, unabhängig von der Auslastung der GPU im Server. Läuft ein Server, läuft er voll (Alibaba zeigt im Median 4 % GPU-Nutzung: Jobs müssen dicht gepackt werden).
- Stündliche Auflösung, perfekte Kenntnis des Bedarfs der laufenden Stunde, keine Prognose über die Stunde hinaus.
- Speicher ohne Verluste, Warmwasser gleichmässig über den Tag (0,5 kWh pro Stunde).
- Ankünfte nach Alibaba-Tagesform in UTC+8, nicht auf Basel umgerechnet.

## Day-ahead-Zusage (Stand 21.11.2026, `src/scheduler/zusage.py`)
Frage: Wie viele Server-Stunden kann DigitalHeat einen Tag im Voraus verbindlich zum Roche-Preis von 0,50 CHF pro L4-h (= 4,00 CHF pro Server-h) verkaufen?
- Entscheid um 12 Uhr Ortszeit am Vortag. Prognose: Open-Meteo «Previous Runs», ECMWF IFS 0,25°. Genutzt werden nur Läufe, die zum Entscheid schon veröffentlicht waren (konservativ 8 h Verzug, Test für jede Stunde). Der Vortagslauf ist genauer als der Lauf zwei Tage vorher: mittlerer Fehler 0,84 °C gegenüber 0,95 °C.
- Für 2024 gibt es keine Previous Runs. Darum: kalibriert auf Januar–Juni 2025, ausgewertet auf Juli–Dezember 2025.
- **Referenzhaus, 8 Server:** Sicherheitsfaktor 0,95. **93 % der Server-h sind zusagbar** (im Auswertungshalbjahr Juli–Dezember 92 %), die angenommenen 60 % fest gebucht sind also gedeckt. Fehlmenge an 2,2 % der Tage ausserhalb der Kalibrierung, 57 Server-h im Jahr. Gutschrift: 50 % des Vertragspreises (Schätzung). **Ergebnis im Idealmodell 40'286 CHF pro Jahr statt 40'412 CHF.** Die Fehlmenge ist so klein, weil im Modell nur 64 % der zugesagten Menge abgenommen werden.
- Damit ist gezeigt, dass die Liefermenge für eine Zusage am Vortag reicht. Preis und Nachfrage bleiben Annahmen: Zusagbar heisst noch nicht verkauft.
- Daten: `daten/ergebnisse/zusage_8_spot.json`.

## Wärme-Router im Case-Idealmodell
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
| Ergebnis DigitalHeat | −108'690 CHF/J | **−6'207 CHF/J** | −965'465 CHF/J |

| Szenario «Genug Aufträge» (Spot) | 0 Senken | Sportbad 50 | Sportbad 170 |
|---|---|---|---|
| Ergebnis DigitalHeat | 807'900 CHF/J | 1'001'068 CHF/J | 1'427'634 CHF/J |
| mit Day-ahead-Zusage (60 % fest, Fehlmenge) | 805'380 CHF/J | 998'572 CHF/J | – |

**Befunde**
1. **Der Router schliesst das Sommerloch nur, wenn es genug Aufträge gibt.** Ohne Senke gibt die Flotte 179'870 Server-h an andere Clouds ab, weil die Häuser im Sommer keine Wärme brauchen. Ein Sportbad mit 50 Servern nimmt 93 % davon auf. Das verbessert das Ergebnis um rund **102'000 CHF pro Jahr**. Bei Nachfrage nach Alibaba bleibt die Flotte trotzdem im Minus: Der Engpass ist die Nachfrage, nicht die Wärme.
2. **Die Senkenregel aus dem Design-Doc ist falsch dimensioniert.** Sie richtet die Serverzahl nach dem Wärmebedarf (170 Server) statt nach den Aufträgen. Die richtige Grösse ergibt sich aus der Nachfrage: bestes Ergebnis bei 50 Servern (gesucht von 10 bis 80, `suche_senkengroesse_alibaba`). Nur wenn es unbegrenzt Aufträge gibt (Spot), lohnt jeder zusätzliche Server.
3. **Die Häuser behalten ihre Wärme.** Weil sie Vorrang haben, sinkt ihre Deckung mit Bad nur von 51,5 % auf 50,9 %. Die Häuser haben in jeder Stunde Vorrang. Was das Bad zu einer Zeit rechnet, in der kein Haus Wärme braucht, fehlt einem Haus manchmal ein paar Stunden später. Ohne die Vorrang-Regel lag die Deckung bei 47,5 %, und das Bad holte sich im Mai und September die Arbeit der Häuser.
4. **Gleiche Häuser gleichen sich nicht aus.** 20 gleiche Häuser mit gleichem Wetter rechnen so viel wie 20 einzelne Häuser (Test, Abweichung < 0,1 %). Der Nutzen der Verteilung entsteht erst mit einem Standort, der zu anderen Zeiten Wärme braucht.
5. **Migration ist echt und verlustfrei.** Der echte Job wurde nach 2'688 von 5'000 Texten mit SIGTERM angehalten und als neuer Prozess fortgesetzt. Die Vektoren sind identisch, Abweichung 0,0 (`tests/vektorvergleich.py`, `messungen/vektorvergleich.json`). Neustart bis rechenbereit: 0,28 s. Bis der laufende Block fertig ist: 1,4 s mit 6 Threads, 6,4 s mit 1 Thread. Die 3'457 Migrationen pro Jahr kosten damit zusammen rund 2 kWh.

**Grenzen:** Der Wärmebedarf des Bads ist eine Schätzung, ohne Lehrschwimmbecken und Duschen. Ins Becken als Speicher passen 1'200 kWh (Schätzung). Das Bad hat in der Zusage keinen Prognosefehler (Monatsprofil). Die Migration rechnet ohne Übertragung über das Netz. Die Typ-B-Ankünfte im Pool sind anders gezogen als in 20 einzelnen Häusern.

**Reproduzieren:** `python3 src/scheduler/zusage.py`, `python3 src/scheduler/flotte.py` (≈ 5 min), Tests `python3 -m unittest discover -s tests`, Vektorvergleich `.venv/bin/python tests/vektorvergleich.py` (≈ 8 min).

## Flotte mit bedarfsgerechtem Abschalten

Der Wärme-Router teilt zuerst den Häusern Aufträge zu. Zusammen mit Wärmebedarf und Speicherfüllstand bestimmt die verfügbare Arbeit, wie viele Server pro Standort starten. Starts dauern im Modell fünf Minuten und reduzieren das Rechenbudget der Stunde. Leerlauf und Starts liefern Wärme mit dem Case-Wirkungsgrad, nur Standby liefert keine nutzbare Wärme. Für beide Standorttypen gelten angenommene **230 W Leerlauf und 10 W Standby** pro Server. Ohne saisonalen Wärmebedarf hält das Bad alle Server im Standby. Für die Erlösrechnung zählen Rechenstunden abzüglich Migrationszeit. Die Stromrechnung verwendet den Gesamtverbrauch.

| Nachfrage | Sportbad | Strom Flotte | Wärmedeckung Häuser / Bad | Extern abgegeben | Fristen verpasst (intern) | Jahresergebnis |
|---|---|---:|---:|---:|---:|---:|
| Nur Jobs mit Frist | Ohne | 451’579 kWh | 56,8 % / – | 194’940 h | 0 | −172’139 CHF |
| Nur Jobs mit Frist | 50 Server | 620’914 kWh | 56,2 % / 21,0 % | 30’227 h | 0 | −78’626 CHF |
| Genug Aufträge | Ohne | 714’113 kWh | 90,6 % / – | 183 h | 0 | +727’666 CHF |
| Genug Aufträge | 50 Server | 903’903 kWh | 90,6 % / 23,1 % | 187 h | 0 | +880’032 CHF |

Mit und ohne Bad kommen dieselben Aufträge mit Frist an. Bei knapper Nachfrage hält das Sportbad rund **165’000 zusätzliche Serverstunden** im eigenen System und verbessert das Jahresergebnis um **93’513 CHF**. Dabei steigt der Gesamtstrom, weil mehr Aufträge lokal laufen. Die 50 Bad-Server sind übers Jahr zu rund **60 % im Standby**. Mit genügend Aufträgen erhöht das Bad das Jahresergebnis um **152’366 CHF**. In diesem Szenario füllt der Spot-Nachschub auch die zusätzliche Kapazität am Bad. **50 Server** sind die Vergleichsgrösse aus dem Case-Idealmodell. Das Optimum im Abschaltmodell wurde noch nicht gesucht.

Mit Vortagszusage und Gutschrift liegt das Jahresergebnis bei genügend Aufträgen bei **725’503 CHF ohne Bad** und **877’740 CHF mit Bad**. Rund **91 %** der simulierten Kapazität sind am Vortag zusagbar. Für das Sportbad verwendet die Prognose dasselbe geschätzte Monatsprofil wie die tatsächliche Simulation. Die Ausführung abgegebener Jobs in der externen Cloud wird nicht simuliert.

**Reproduzieren:** `python3 src/scheduler/flotte.py --abschalten` schreibt `daten/ergebnisse/flotte_abschalten.json`. Die Optionen `--leerlauf-watt`, `--standby-watt` und `--start-minuten` ändern das Leistungsprofil. Die Live-Option `--flotte --abschalten` zeigt simulierte Serverzustände neben dem echten lokalen Job.
