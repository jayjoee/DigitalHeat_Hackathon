# Firmenrechnung DigitalHeat: Ausbau, Skaleneffekte, Förderung, Holz statt Öl

**Geltungsgrenze nach der Angebotsentscheidung:** Gewählt ist [L4 für freigegebene nicht vertrauliche Aufgaben](L4_ANGEBOT.md). Die folgenden Ergebnisse setzen die angenommenen Preise und Mengen voraus. Sie bestätigen weder genügend öffentliche Winteraufträge noch die Zahlungsbereitschaft dafür; vertrauliche Pharma-Nachfrage darf nicht als verfügbarer L4-Auftrag weitergezählt werden.

Stand 21.11.2026. Reproduzieren: `python3 src/firma.py` → `daten/ergebnisse/firma.json`. Alle Beträge in CHF.

## Was neu ist

| Thema | Vorher | Jetzt |
|---|---|---|
| Ebene | ein Haus, Firmenkosten als 1'200 CHF pro Haus | ganze Firma, Ausbauplan, jedes Haus 5 Jahre |
| Preise | 0,60 CHF pro L4-Stunde, Rest zum Spot-Preis | **Roche 60 % zu 0,50 CHF fest, übrige Stunden 0,55 CHF**, sinkt 10 % pro Kalenderjahr ([KOSTEN_DH.md](KOSTEN_DH.md)) |
| Reserveheizung | bestehender Ölkessel | **kein Öl mehr**: Kessel und Tank werden zurückgebaut (4'000 CHF). Den Rest liefert der Holzofen oder das Cheminée, das viele ältere Häuser schon haben (Team-Annahme, keine Kosten) |
| Förderung | keine | wie für eine Luft/Wasser-Wärmepumpe in Basel-Stadt, laut DigitalHeat wahrscheinlich |
| Skaleneffekte | keine | Mengenrabatt Server, Lernkurve beim Einbau, Fixkosten verteilen sich, dichtere Servicetouren |
| Steuern | pro Haus | auf Firmenebene mit Verlustvortrag (7 Jahre) |
| Finanzierung | 50 % Kredit, Eigenkapital-IRR | **ohne Kredit**: Ein junges Unternehmen ohne Sicherheiten bekommt kaum 50 % Kredit zu 4,5 %. Die Firma braucht das ganze Kapital als Eigenkapital |
| Endwert | Restbuchwert nach 10 Jahren | **kein Endwert**: Wir rechnen eine Hardware-Generation, jedes Haus läuft 5 Jahre (2027–2035). Am Ende zählt nur der Wiederverkaufswert der Server |

Grundlage pro Haus: Referenzhaus mit 8 Servern im Abschaltmodell (230 W Leerlauf), 34'512 verkaufte Server-Stunden pro Jahr, Roche 0,50 CHF (= 4,00 CHF pro Server-Stunde), übrige Stunden 0,55 CHF (= 4,40 CHF). Der Roche-Vertrag gilt 5 Jahre; die Rechnung nimmt an, dass er für die späteren Häuser zum selben Preis verlängert wird.

## Förderbeiträge Basel-Stadt (Stand Oktober 2026)

- Luft/Wasser-Wärmepumpe ausserhalb des Fernwärmegebiets: **Fr. 8'000 + Fr. 250 pro kW thermisch**; innerhalb halb so viel ([bs.ch/en/node/39393](https://www.bs.ch/en/node/39393)).
- Höchstens 40 % der Investition, Gesuch vor Baubeginn; ein beauftragtes Unternehmen darf das Gesuch stellen, ausbezahlt wird an den Eigentümer ([bs.ch/en/node/28384](https://www.bs.ch/en/node/28384)).
- Unser Haus liefert 6,4 kW thermisch (8 Server × 0,8 kW): 9'600 CHF ausserhalb, 4'800 CHF innerhalb. Annahme: die Hälfte der Häuser liegt im Fernwärmegebiet → **7'200 CHF pro Haus**, vertraglich an DigitalHeat abgetreten.
- **Wichtig:** Die Förderung ist klein gegenüber 290'000 CHF Hardware. Ohne sie sinkt die Projekt-IRR nur von 28,8 % auf 26,9 %.
- Holz: Wir rechnen mit einem Holzofen, der schon im Haus steht. Er braucht keine Förderung und kostet DigitalHeat nichts.

## Holz statt Öl: der vorhandene Holzofen

Annahme des Teams: Die Zielhäuser, ältere Öl- und Gas-Häuser, haben oft schon einen Holzofen oder ein Cheminée. Eine BFS-Zahl zu solchen Zusatzheizungen haben wir nicht gefunden (Hauptheizung Holz: rund 10–12 % der Gebäude, [BFS](https://www.bfs.admin.ch/asset/de/27905548)).

Wie oft reicht die Serverwärme nicht? (Wetter Basel 2025)

| | Referenzhaus 31'231 kWh, 8 Server | Durchschnitts-EFH 17'000 kWh, 5 Server |
|---|---|---|
| Rest-Wärme pro Jahr | 2'203 kWh (Case-Regel) bis 2'936 kWh (Abschalten) | 246 kWh |
| Tage mit Fehlmenge | 77–94, Dezember bis Februar und einzelne im März/November | 30 |
| Grösste Fehlmenge | 4,1–4,3 kW | 1,4 kW |
| Tage mit mehr als 10 kWh | 57–77 | 11 |
| Ohne jede Zusatzheizung | Raum fällt bis 13,5 °C, an 56 Tagen unter 18 °C | Raum bleibt über 18 °C |
| Brennholz | 1,4–1,9 Ster (≈ 350–470 CHF) | ≈ 0,15 Ster |

**Folge:** Beim durchschnittlichen Einfamilienhaus sind es wirklich nur wenige kalte Tage, und selbst ohne Ofen bleibt es über 18 °C. Beim grossen Referenzhaus muss der Holzofen im Hochwinter an vielen Abenden mitlaufen. Für solche Häuser ist entweder ein 9. Server (95,3 % Deckung, an 28 statt 56 Tagen unter 18 °C ohne Ofen) oder ein regelmässig genutzter Ofen nötig. Ein Cheminée oder Schwedenofen heizt vor allem den Raum, in dem er steht.

Offen: Bewilligung und Feinstaub-Vorgaben für Holzöfen in Basel-Stadt.

## Ergebnis Firma (Basisfall)

Ausbau: 5 / 15 / 30 / 50 / 70 neue Häuser von 2027 bis 2031, zusammen 170 Häuser (10'880 L4). Jedes Haus läuft 5 Jahre und wird in dieser Rechnung nicht ersetzt; die Häuser von 2031 laufen bis 2035. Beträge in Mio. CHF.

| Jahr | Häuser | Umsatz | EBITDA | Gewinn nach Steuern | Investitionen | Förderung | Cashflow | kumuliert |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2027 | 5 | 0,68 | 0,19 | −0,04 | 1,46 | 0,04 | −1,23 | −1,23 |
| 2028 | 20 | 2,59 | 1,74 | 0,74 | 4,16 | 0,11 | −2,42 | −3,65 |
| 2029 | 50 | 6,23 | 4,61 | 2,08 | 8,30 | 0,22 | −3,79 | −7,44 |
| 2030 | 100 | 11,99 | 9,03 | 4,09 | 13,19 | 0,36 | −4,42 | −11,85 |
| 2031 | 170 | 19,67 | 14,71 | 6,48 | 18,47 | 0,50 | −3,96 | **−15,82** |
| 2032 | 165 | 18,48 | 13,13 | 5,31 | 0 | 0 | 13,07 | −2,75 |
| 2033 | 150 | 16,29 | 11,00 | 4,03 | 0 | 0 | 11,87 | **9,12** |
| 2034 | 120 | 12,67 | 7,82 | 2,41 | 0 | 0 | 9,78 | 18,90 |
| 2035 | 70 | 7,20 | 4,15 | 1,05 | 0 | 0 | 7,25 | 26,14 |

Der Umsatz sinkt ab 2032, weil die ersten Häuser auslaufen und der Preis der übrigen Stunden jedes Jahr 10 % fällt.

| Kennzahl | Wert |
|---|---|
| Projekt-IRR (eine Hardware-Generation, ohne Kredit, ohne Endwert) | **28,8 %** |
| Kapitalbedarf (tiefster kumulierter Cashflow, ohne Kredit) | **15,8 Mio. CHF** |
| Payback | **2033** |
| Kapitalwert bei 12 % Eigenkapitalkosten | 8,7 Mio. CHF |
| Firma trägt ihre Fixkosten ab | **6 Häusern** (5,6) |
| Investition pro Haus nach Förderung | 285'000 CHF (Pilot) → 257'000 CHF (ab 2030) |
| Fixkosten pro Haus | 77'000 CHF (2027, 5 Häuser) → 5'400 CHF (2031, 170 Häuser) |

Zum Vergleich: Über 10 Jahre mit Ersatz der Hardware nach 5 Jahren und dem Restbuchwert als Endwert kommt fast dieselbe IRR heraus (28,8 %). Ohne Endwert wäre sie in dieser Variante stark negativ, weil 2035 und 2036 Ersatz-Hardware gekauft wird, die im Horizont kaum noch läuft. Deshalb ist die Rechnung über eine Generation die ehrlichere Zahl. Mit 50 % Kredit läge die Eigenkapital-IRR bei 50 % und der Eigenkapitalbedarf bei 4,2 Mio. CHF; diesen Kredit nehmen wir nicht an (`nur_information_mit_kredit` in `firma.json`).

## Szenarien

| Szenario | Projekt-IRR | Kapitalbedarf | Payback | Firma trägt sich ab |
|---|---:|---:|---:|---:|
| **Basis** (alle Stunden verkauft) | **28,8 %** | 15,8 Mio. | 2033 | 6 Häusern |
| Ohne Förderung | 26,9 % | 17,0 Mio. | 2033 | 6 Häusern |
| Halber Ausbau (88 Häuser) | 22,8 % | 9,0 Mio. | 2033 | 6 Häusern |
| 90 % der Stunden verkauft | 21,0 % | 18,9 Mio. | 2033 | 7 Häusern |
| 80 % verkauft | 13,8 % | 22,0 Mio. | 2034 | 10 Häusern |
| 72 % verkauft | 8,3 % | 24,5 Mio. | 2034 | 15 Häusern |
| Nur Roche (60 %), Rest unverkauft | 0,4 % | 28,2 Mio. | 2035 | 45 Häusern |
| Übrige Stunden nur zum Spot-Preis (0,294 CHF) | 14,7 % | 21,6 Mio. | 2034 | 10 Häusern |
| **Knappe Nachfrage** (nur Jobs mit Frist, Wärme zuerst) | **−7,7 %** | 30,0 Mio. | nie | 32 Häusern |

Bei weniger verkauften Stunden läuft der Strom trotzdem, weil das Haus die Wärme braucht. Roche nimmt seine 60 % immer ab; es fehlen Stunden aus dem Rest.

**Der Engpass ist die Nachfrage.** Mit allen Stunden verkauft ist das Geschäft stark. Schon bei 80 % verkauften Stunden liegt die IRR nur noch knapp über den 12 %, die Investoren von einem jungen Unternehmen erwarten. Unter rund 78 % lohnt es sich nicht mehr. Förderung und Skaleneffekte verschieben das Ergebnis wenig, Absatz und Preis der übrigen Stunden sehr. Nächster Schritt: ein bezahltes Winterkontingent mit einem ersten Kunden, um Absatz und Preis zu belegen.

## Annahmen (Auszug, alle in `src/firma.py` mit Quelle)

- Team: 2 Personen Grundteam + 1 Person pro 40 Häuser, 130'000 CHF pro Person (Schätzung); ISO 27001 40'000, Büro/IT 40'000, Vertrieb 30'000 CHF pro Jahr.
- Mengenrabatt Server 5 % ab 80, 10 % ab 300 Servern pro Jahr (Schätzung, übliche 5–15 %).
- Lernkurve Einbau −15 % je Verdopplung, höchstens −50 % (Schätzung, Lernraten PV/Wärmepumpen 10–20 %).
- Service: −10 % ab 50, −20 % ab 150 Häusern (kürzere Anfahrten).
- Gewinnsteuer Basel-Stadt 13,04 %, Verlustvortrag 7 Jahre (DBG Art. 67).
- Preis der übrigen Stunden: 0,55 CHF im Jahr 2027, danach −10 % pro Kalenderjahr, auch für spätere Häuser (vorher startete jedes neue Haus fälschlich wieder beim vollen Preis). Laufende Kosten +4,5 % pro Kalenderjahr.
- Nicht gerechnet: zweite Hardware-Generation, Wärmeverkauf, Bad als Sommer-Senke, Kosten der Kundengewinnung über 30'000 CHF/Jahr.
