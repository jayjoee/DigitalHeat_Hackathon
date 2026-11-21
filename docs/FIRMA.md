# Firmenrechnung DigitalHeat: Ausbau, Skaleneffekte, Förderung, Holz statt Öl

Stand 21.11.2026. Reproduzieren: `python3 src/firma.py` → `daten/ergebnisse/firma.json`. Alle Beträge in CHF.

## Was neu ist

| Thema | Vorher | Jetzt |
|---|---|---|
| Ebene | ein Haus, Firmenkosten als 1'200 CHF pro Haus | ganze Firma, 10 Jahre, Ausbauplan |
| Reserveheizung | bestehender Ölkessel | **kein Öl mehr**: Kessel und Tank werden zurückgebaut (4'000 CHF), ein wasserführender Holzofen heizt in den Speicher (7'000 CHF) |
| Förderung | keine | wie für eine Luft/Wasser-Wärmepumpe in Basel-Stadt, laut DigitalHeat wahrscheinlich |
| Skaleneffekte | keine | Mengenrabatt Server, Lernkurve beim Einbau, Fixkosten verteilen sich, dichtere Servicetouren |
| Steuern | pro Haus | auf Firmenebene mit Verlustvortrag (7 Jahre) |
| Finanzierung | Zins als Annuität | Projektsicht (ohne Kredit) und Eigenkapitalsicht (50 % der Hardware über Kredit, 4,5 %) |

Grundlage pro Haus: Referenzhaus mit 8 Servern im Abschaltmodell (230 W Leerlauf), genug Aufträge, 0,60 CHF pro L4-Stunde (= 4,80 CHF pro Server-Stunde), 60 % fest gebucht.

## Förderbeiträge Basel-Stadt (Stand Oktober 2026)

- Luft/Wasser-Wärmepumpe ausserhalb des Fernwärmegebiets: **Fr. 8'000 + Fr. 250 pro kW thermisch**; innerhalb halb so viel ([bs.ch/en/node/39393](https://www.bs.ch/en/node/39393)).
- Höchstens 40 % der Investition, Gesuch vor Baubeginn; ein beauftragtes Unternehmen darf das Gesuch stellen, ausbezahlt wird an den Eigentümer ([bs.ch/en/node/28384](https://www.bs.ch/en/node/28384)).
- Unser Haus liefert 6,4 kW thermisch (8 Server × 0,8 kW): 9'600 CHF ausserhalb, 4'800 CHF innerhalb. Annahme: die Hälfte der Häuser liegt im Fernwärmegebiet → **7'200 CHF pro Haus**, vertraglich an DigitalHeat abgetreten.
- **Wichtig:** Die Förderung ist klein gegenüber 290'000 CHF Hardware. Ohne sie sinkt die Projekt-IRR nur von 33,7 % auf 32,0 %.
- Holz: gefördert werden automatische Pellet- und Hackschnitzelheizungen ([bs.ch/en/node/39409](https://www.bs.ch/en/node/39409)); ein Stückholzofen ist dort nicht genannt. Wir rechnen ihn deshalb ohne Förderung.

## Holz statt Öl

- Rest-Wärme pro Referenzhaus: rund **2'960 kWh pro Jahr** (9,5 % im Abschaltmodell), nur an den kältesten Tagen, höchstens rund 4 kW.
- Das sind etwa **1,9 Ster Buche** pro Jahr (2'100 kWh pro Ster, Ofen 75 %) oder rund **470 CHF** für den Haushalt.
- Das Haus ist damit ganz ohne fossile Energie. Offen: Bewilligung und Feinstaub-Vorgaben für Holzöfen in Basel-Stadt.

## Ergebnis Firma (Basisfall)

Ausbau: 5 / 15 / 30 / 50 / 70 neue Häuser von 2027 bis 2031, danach 170 Häuser (10'880 L4). Hardware wird nach 5 Jahren ersetzt.

| Jahr | Häuser | Umsatz | EBITDA | Gewinn nach Steuern | Investitionen | Cashflow Eigenkapital |
|---|---:|---:|---:|---:|---:|---:|
| 2027 | 5 | 0,62 Mio. | 0,14 Mio. | −0,14 Mio. | 1,50 Mio. | −0,77 Mio. |
| 2028 | 20 | 2,47 Mio. | 1,62 Mio. | 0,52 Mio. | 4,26 Mio. | −1,19 Mio. |
| 2029 | 50 | 6,14 Mio. | 4,56 Mio. | 1,73 Mio. | 8,51 Mio. | −1,52 Mio. |
| 2030 | 100 | 12,22 Mio. | 9,35 Mio. | 3,80 Mio. | 13,54 Mio. | −1,04 Mio. |
| 2031 | 170 | 20,64 Mio. | 15,90 Mio. | 6,60 Mio. | 18,96 Mio. | 0,58 Mio. |
| 2032 | 170 | 20,23 Mio. | 15,07 Mio. | 6,04 Mio. | 1,40 Mio. | 9,01 Mio. |

| Kennzahl | Wert |
|---|---|
| Projekt-IRR (vor Finanzierung, 10 Jahre, Endwert = Restbuchwert) | **33,7 %** |
| Eigenkapital-IRR (50 % der Hardware über Kredit) | **58,6 %** |
| Eigenkapitalbedarf (tiefster kumulierter Cashflow) | **4,5 Mio. CHF** |
| Payback Eigenkapital | **2032** (Projekt: 2033) |
| Firma trägt ihre Fixkosten ab | **7 Häusern** |
| Investition pro Haus | 292'000 CHF (Pilot) → 264'000 CHF (ab 2030) |
| Fixkosten pro Haus | 77'000 CHF (2027, 5 Häuser) → 5'400 CHF (2031, 170 Häuser) |

## Szenarien

| Szenario | Projekt-IRR | EK-IRR | EK-Bedarf | Firma trägt sich ab |
|---|---:|---:|---:|---:|
| Basis | 33,7 % | 58,6 % | 4,5 Mio. | 7 Häusern |
| Ohne Förderung | 32,0 % | 55,4 % | 5,0 Mio. | 7 Häusern |
| Vertragspreis 0,50 CHF | 21,7 % | 38,0 % | 8,6 Mio. | 10 Häusern |
| Halber Ausbau (88 Häuser) | 27,8 % | 46,7 % | 3,0 Mio. | 7 Häusern |
| **Knappe Nachfrage** (nur Jobs mit Frist, Wärme zuerst) | **−1,5 %** | 5,0 % | 18,7 Mio. | **91 Häusern** |

**Der Engpass ist die Nachfrage.** Mit genug fest gebuchten Aufträgen ist das Geschäft stark; mit der Nachfrage aus dem Alibaba-Trace trägt es sich nicht. Förderung und Skaleneffekte verschieben das Ergebnis wenig, Preis und Auslastung sehr.

## Annahmen (Auszug, alle in `src/firma.py` mit Quelle)

- Team: 2 Personen Grundteam + 1 Person pro 40 Häuser, 130'000 CHF pro Person (Schätzung); ISO 27001 40'000, Büro/IT 40'000, Vertrieb 30'000 CHF pro Jahr.
- Mengenrabatt Server 5 % ab 80, 10 % ab 300 Servern pro Jahr (Schätzung, übliche 5–15 %).
- Lernkurve Einbau −15 % je Verdopplung, höchstens −50 % (Schätzung, Lernraten PV/Wärmepumpen 10–20 %).
- Service: −10 % ab 50, −20 % ab 150 Häusern (kürzere Anfahrten).
- Gewinnsteuer Basel-Stadt 13,04 %, Verlustvortrag 7 Jahre (DBG Art. 67).
- Nicht gerechnet: sinkende GPU-Preise beim Ersatz, Wärmeverkauf, Bad als Sommer-Senke, Kosten der Kundengewinnung über 30'000 CHF/Jahr.
