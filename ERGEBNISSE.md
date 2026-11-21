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

Das Dashboard zeigt alle Kennzahlen für 1–13 Server und beide Nachfrageszenarien. Strompreis, Rechenpreis und Hardwarekosten lassen sich verschieben, das Urteil «rechnet sich / rechnet sich nicht» folgt sofort. Läuft `live.py`, zeigt es den echten Prozess (rechnet oder pausiert) jede Sekunde.

## Kennzahlen für 8 Server pro Haus (Vorschlag)

Szenario **Spot**: Typ A wird jederzeit vom Spot-Markt abgenommen (Annahme: unbegrenzte Nachfrage, ohne Frist). Typ B kommt begrenzt nach Alibaba-Trace (40 Jobs pro Tag, Frist 2 h).

| Kennzahl | Wert |
|---|---|
| Server pro Haus | **8** |
| Deckung des Wärmebedarfs (Heizung + Warmwasser, 31'231 kWh) | **93,0 %** (29'027 kWh, Rest 2'203 kWh vom Backup) |
| Abgeführte Wärme | **5 kWh** (0,02 % der Serverwärme) |
| Auslastung | **51,8 %** (36'290 Server-h ÷ 8 × 8'760) |
| Verpasste Fristen | **0,0 %** von 14'390 Jobs mit Frist |
| Stromkosten | 12'066 CHF (36'290 kWh × 0,3325) |
| Wert der genutzten Wärme | 3'861 CHF (29'027 kWh × 0,133) |
| Rechenerlös bei 1,06 CHF/Server-h | 38'409 CHF |
| **Break-even-Rechenpreis** | **0,226 CHF pro Server-h** = (12'066 − 3'861) ÷ 36'290 |
| Höchstens tragbare Hardwarekosten | 3'775 CHF pro Server und Jahr (beim Rechenpreis 1,06 CHF/Server-h) |
| Hardware laut Recherche | 6'720 CHF pro Server und Jahr (1,6 × 25'000 $ × 0,84 ÷ 5 Jahre, `daten/PREISE.md`) |
| **Nötiger Rechenpreis mit Hardware** | **1,71 CHF pro Server-h** = (12'066 − 3'861 + 8 × 6'720) ÷ 36'290 ≈ 1,27 $ pro H100-Stunde |
| Ergebnis mit Hardware bei 1,06 CHF/Server-h | −23'556 CHF pro Jahr für 8 Server |

## Warum 8 Server
| Server | 4 | 6 | **8** | 10 | 12 |
|---|---|---|---|---|---|
| Deckung | 58,1 % | 79,6 % | **93,0 %** | 99,3 % | 100 % |
| Auslastung | 64,7 % | 59,1 % | **51,8 %** | 44,2 % | 37,2 % |
| Abgeführt | 0 | 0 | **5 kWh** | 12 kWh | 28 kWh |
| Max. Hardware/Server/Jahr | 4'715 | 4'310 | **3'775** | 3'226 | 2'712 CHF |

- Bis 8 Server bringt jeder weitere Server 6–13 Prozentpunkte Deckung, der 9. nur noch 3,9.
- Die Kosten tragen die Winterstunden: Ab Server 9 laufen die zusätzlichen Server nur in wenigen kalten Stunden, die Auslastung fällt unter 50 %.
- 12,5 Server für die kälteste Stunde wären 100 % Deckung bei 37 % Auslastung.

Was jeder weitere Server pro Jahr zusätzlich bringt (Spot, 1,06 CHF/Server-h, ohne Hardware):

| Server Nr. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | **8** | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Zusatzergebnis CHF/Jahr | 6'351 | 4'292 | 4'154 | 4'064 | 3'840 | 3'160 | 2'442 | **1'901** | 1'297 | 762 | 252 |

Regel: **Ein Server mehr lohnt sich, solange er pro Jahr weniger kostet, als er zusätzlich bringt.** Damit folgt die Serverzahl aus dem Hardwarepreis. Bei 6'720 CHF pro Jahr lohnt sich am Spot-Tiefstpreis schon der erste Server nicht. Die 8 Server sind deshalb eine Wahl für die Deckung (93 % bei fast null Abwärme), nicht für den Gewinn. Das Dashboard zeigt diese Rechnung im Abschnitt «Lohnt sich ein Server mehr?» für jeden Preis.

## Jahresverlauf (8 Server, Spot)
| Monat | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Deckung | 86 % | 90 % | 98 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 92 % | 89 % |
| Auslastung | 97 % | 96 % | 84 % | 48 % | 22 % | 8 % | 8 % | 8 % | 20 % | 53 % | 84 % | 96 % |

Von Juni bis August laufen die Server nur noch für das Warmwasser (0,6 Server). **Das Sommerloch ist das Problem der Wirtschaftlichkeit, nicht die Deckung.**

## Wann es sich nicht lohnt
1. **Rechenpreis unter 0,226 CHF pro Server-h:** Dann deckt der Erlös nicht einmal den Strom abzüglich Wärmewert. Das gilt unabhängig von der Serverzahl, solange keine Wärme abgeführt wird.
2. **Hardware:** Mit Hardware gilt: nötiger Rechenpreis = Hardware pro Server und Jahr ÷ 4'538 Server-h + 0,226 CHF.
   Recherchiert (`daten/PREISE.md`): H100 NVL 24'500–32'383 $, untere Spanne 25'000 $, 1,6 GPU pro Server, 5 Jahre Abschreibung → **6'720 CHF pro Server und Jahr** (ohne Host, Kühlung, Wartung, Netz). Damit braucht es **1,71 CHF pro Server-h** (≈ 1,27 $ pro H100-Stunde). Das liegt in der Spot-Spanne (0,79–2,50 $), aber deutlich über dem Tiefstpreis.
   **Bei 1,06 CHF/Server-h (unterster Spot-Preis) lohnt es sich nur, wenn ein Server weniger als 3'775 CHF pro Jahr kostet. Mit H100-Hardware ist das nicht der Fall.**
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
- **Unbegrenzte Spot-Nachfrage für Typ A** (Szenario Spot). Das ist die stärkste Annahme. Das Szenario Alibaba zeigt, was ohne sie passiert.
- Rechenpreis 1,26 $/Server-h (unterster Spot-Preis × 1,6 GPU/kW), Wechselkurs 0,84 CHF/$ (Stand 20.11.2026).
- Hardware: 6'720 CHF pro Server und Jahr (H100-Preis, untere Spanne, 5 Jahre). Die Case-Kennzahl «Break-even» bleibt ohne Hardware, daneben steht der nötige Preis mit Hardware.
- Keine Wetterprognose: Bei verlustfreiem Speicher und unbegrenzten Aufträgen A ist «Speicher immer füllen» schon die beste Deckung. Eine Prognose bringt erst etwas, wenn Aufträge knapp sind oder der Speicher Verluste hat.
- Wärmeabgabe = Strom × 0,8, unabhängig von der Auslastung der GPU im Server. Läuft ein Server, läuft er voll (Alibaba zeigt im Median 4 % GPU-Nutzung: Jobs müssen dicht gepackt werden).
- Stündliche Auflösung, perfekte Kenntnis des Bedarfs der laufenden Stunde, keine Prognose über die Stunde hinaus.
- Speicher ohne Verluste, Warmwasser gleichmässig über den Tag (0,5 kWh pro Stunde).
- Ankünfte nach Alibaba-Tagesform in UTC+8, nicht auf Basel umgerechnet.
