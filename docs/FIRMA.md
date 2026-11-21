# Firmenrechnung DigitalHeat: Ausbau, Skaleneffekte, Förderung, Holz statt Öl

**Geltungsgrenze nach der Angebotsentscheidung:** Gewählt ist [L4 für freigegebene nicht vertrauliche Aufgaben](L4_ANGEBOT.md). Die folgenden Ergebnisse setzen die angenommenen Preise und Mengen voraus. Sie bestätigen weder genügend öffentliche Winteraufträge noch die Zahlungsbereitschaft dafür; vertrauliche Pharma-Nachfrage darf nicht als verfügbarer L4-Auftrag weitergezählt werden.

Stand 21.11.2026. Reproduzieren: `python3 src/firma.py` → `daten/ergebnisse/firma.json`. Alle Beträge in CHF.

## Was neu ist

| Thema | Vorher | Jetzt |
|---|---|---|
| Ebene | ein Haus, Firmenkosten als 1'200 CHF pro Haus | ganze Firma, 10 Jahre, Ausbauplan |
| Reserveheizung | bestehender Ölkessel | **kein Öl mehr**: Kessel und Tank werden zurückgebaut (4'000 CHF). Den Rest liefert der Holzofen oder das Cheminée, das viele ältere Häuser schon haben (Team-Annahme, keine Kosten) |
| Förderung | keine | wie für eine Luft/Wasser-Wärmepumpe in Basel-Stadt, laut DigitalHeat wahrscheinlich |
| Skaleneffekte | keine | Mengenrabatt Server, Lernkurve beim Einbau, Fixkosten verteilen sich, dichtere Servicetouren |
| Steuern | pro Haus | auf Firmenebene mit Verlustvortrag (7 Jahre) |
| Finanzierung | Zins als Annuität | Projektsicht (ohne Kredit) und Eigenkapitalsicht (50 % der Hardware über Kredit, 4,5 %) |

Grundlage pro Haus: Referenzhaus mit 8 Servern im Abschaltmodell (230 W Leerlauf), genug Aufträge, 0,60 CHF pro L4-Stunde (= 4,80 CHF pro Server-Stunde), 60 % fest gebucht.

## Förderbeiträge Basel-Stadt (Stand Oktober 2026)

- Luft/Wasser-Wärmepumpe ausserhalb des Fernwärmegebiets: **Fr. 8'000 + Fr. 250 pro kW thermisch**; innerhalb halb so viel ([bs.ch/en/node/39393](https://www.bs.ch/en/node/39393)).
- Höchstens 40 % der Investition, Gesuch vor Baubeginn; ein beauftragtes Unternehmen darf das Gesuch stellen, ausbezahlt wird an den Eigentümer ([bs.ch/en/node/28384](https://www.bs.ch/en/node/28384)).
- Unser Haus liefert 6,4 kW thermisch (8 Server × 0,8 kW): 9'600 CHF ausserhalb, 4'800 CHF innerhalb. Annahme: die Hälfte der Häuser liegt im Fernwärmegebiet → **7'200 CHF pro Haus**, vertraglich an DigitalHeat abgetreten.
- **Wichtig:** Die Förderung ist klein gegenüber 290'000 CHF Hardware. Ohne sie sinkt die Projekt-IRR nur von 35,4 % auf 33,6 %.
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

Ausbau: 5 / 15 / 30 / 50 / 70 neue Häuser von 2027 bis 2031, danach 170 Häuser (10'880 L4). Hardware wird nach 5 Jahren ersetzt.

| Jahr | Häuser | Umsatz | EBITDA | Gewinn nach Steuern | Investitionen | Cashflow Eigenkapital |
|---|---:|---:|---:|---:|---:|---:|
| 2027 | 5 | 0,62 Mio. | 0,14 Mio. | −0,13 Mio. | 1,46 Mio. | −0,75 Mio. |
| 2028 | 20 | 2,47 Mio. | 1,62 Mio. | 0,55 Mio. | 4,16 Mio. | −1,13 Mio. |
| 2029 | 50 | 6,14 Mio. | 4,56 Mio. | 1,79 Mio. | 8,30 Mio. | −1,39 Mio. |
| 2030 | 100 | 12,22 Mio. | 9,35 Mio. | 3,93 Mio. | 13,19 Mio. | −0,80 Mio. |
| 2031 | 170 | 20,64 Mio. | 15,90 Mio. | 6,83 Mio. | 18,47 Mio. | 0,93 Mio. |
| 2032 | 170 | 20,23 Mio. | 15,07 Mio. | 6,25 Mio. | 1,40 Mio. | 9,11 Mio. |

| Kennzahl | Wert |
|---|---|
| Projekt-IRR (vor Finanzierung, 10 Jahre, Endwert = Restbuchwert) | **35,4 %** |
| Eigenkapital-IRR (50 % der Hardware über Kredit) | **61,9 %** |
| Eigenkapitalbedarf (tiefster kumulierter Cashflow) | **4,1 Mio. CHF** |
| Payback Eigenkapital | **2032** (Projekt: 2033) |
| Firma trägt ihre Fixkosten ab | **7 Häusern** |
| Investition pro Haus | 285'000 CHF (Pilot) → 257'000 CHF (ab 2030) |
| Fixkosten pro Haus | 77'000 CHF (2027, 5 Häuser) → 5'400 CHF (2031, 170 Häuser) |

## Szenarien

| Szenario | Projekt-IRR | EK-IRR | EK-Bedarf | Firma trägt sich ab |
|---|---:|---:|---:|---:|
| Basis | 35,4 % | 61,9 % | 4,1 Mio. | 7 Häusern |
| Ohne Förderung | 33,6 % | 58,5 % | 4,5 Mio. | 7 Häusern |
| Vertragspreis 0,50 CHF | 23,0 % | 40,3 % | 7,8 Mio. | 10 Häusern |
| Halber Ausbau (88 Häuser) | 29,3 % | 49,1 % | 2,8 Mio. | 7 Häusern |
| **Knappe Nachfrage** (nur Jobs mit Frist, Wärme zuerst) | **−0,7 %** | 6,2 % | 17,8 Mio. | **68 Häusern** |

**Der Engpass ist die Nachfrage.** Mit genug fest gebuchten Aufträgen ist das Geschäft stark; mit der Nachfrage aus dem Alibaba-Trace trägt es sich nicht. Förderung und Skaleneffekte verschieben das Ergebnis wenig, Preis und Auslastung sehr.

## Annahmen (Auszug, alle in `src/firma.py` mit Quelle)

- Team: 2 Personen Grundteam + 1 Person pro 40 Häuser, 130'000 CHF pro Person (Schätzung); ISO 27001 40'000, Büro/IT 40'000, Vertrieb 30'000 CHF pro Jahr.
- Mengenrabatt Server 5 % ab 80, 10 % ab 300 Servern pro Jahr (Schätzung, übliche 5–15 %).
- Lernkurve Einbau −15 % je Verdopplung, höchstens −50 % (Schätzung, Lernraten PV/Wärmepumpen 10–20 %).
- Service: −10 % ab 50, −20 % ab 150 Häusern (kürzere Anfahrten).
- Gewinnsteuer Basel-Stadt 13,04 %, Verlustvortrag 7 Jahre (DBG Art. 67).
- Nicht gerechnet: sinkende GPU-Preise beim Ersatz, Wärmeverkauf, Bad als Sommer-Senke, Kosten der Kundengewinnung über 30'000 CHF/Jahr.
