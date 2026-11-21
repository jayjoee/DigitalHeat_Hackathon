# Pilotplan: ein Winter, ein Haus, klare Entscheidung

**Frage:** Lohnt es sich, nach einem Winter von einem Pilothaus auf 20 Häuser auszubauen?
**Antwort nach dem Pilot:** Ja, wenn alle Schwellen unten eingehalten sind. Sonst Stopp oder Anpassung.

Alle Schwellen mit «Modell» stammen aus `src/kosten_dh.py` (`daten/ergebnisse/kosten_dh.json`, Feld `pilot_schwellen`) und sind in [KOSTEN_DH.md, Abschnitt 9](KOSTEN_DH.md#9-nachfrage-zwischen-den-extremen-und-schwellen-für-den-pilotentscheid) hergeleitet. Schwellen mit «Teamvorgabe» sind technische Anforderungen ohne Modellrechnung.

## Umfang

| | |
|---|---|
| Haus | Ein ehemaliges Öl-Haus in Basel-Stadt mit Holzofen als Reserve, ähnlich dem Referenzhaus |
| Server | 2 Server mit je 8 L4 und Flüssigkühlung. Einbau, Pufferspeicher und Netzwerk sind schon für 8 kW ausgelegt |
| Investition | 81'500 CHF ([KOSTEN_DH.md, Abschnitt 9](KOSTEN_DH.md#9-nachfrage-zwischen-den-extremen-und-schwellen-für-den-pilotentscheid)) |
| Dauer | Eine Heizsaison, Oktober bis März, plus ein Sommermonat für das Warmwasser |
| Vertrag Haushalt | 1 Jahr, Wärme gratis, Rückbau kostenlos. Die Server sind nicht verloren: Sie ziehen danach ins nächste Haus um |
| Aufträge | Nur öffentliche, synthetische oder vom Kunden freigegebene anonymisierte Aufgaben ([L4_ANGEBOT.md](../kunden/L4_ANGEBOT.md)) |

## Was gemessen wird und wann es weitergeht

| Grösse | Annahme heute | Messung im Pilot | Weiter, wenn | Herkunft der Schwelle |
|---|---|---|---|---|
| Verkaufte Rechenstunden | 100 % | Abgerechnete ÷ gerechnete Server-Stunden | **mindestens 66 %** | Modell |
| Preis des Ankerkunden | 0,50 CHF pro L4-h | Vertrag oder Absichtserklärung für ein Winterkontingent | **mindestens 0,38 CHF**, falls die übrigen Stunden nur Spot bringen | Modell |
| Serverpreis in der Schweiz inkl. Lieferung | 32'245 CHF (US-Liste) | Offerte eines Schweizer Händlers | **höchstens 55'800 CHF** | Modell |
| Leerlauf, Standby, Startzeit | 230 W, 10 W, 5 min | Strommessung pro Server (PDU) | Leerlauf höchstens 350 W; Startzeit dokumentieren | Modell (bei 350 W noch +33'700 CHF) |
| Abschalten und Starten klappt automatisch | ja | Anteil geplanter Starts ohne Eingriff | praktisch immer; sonst wird pausiert (dann +26'100 statt +35'000 CHF) | Modell |
| Vorlauftemperatur | im Case ohne Wärmepumpe nutzbar | Temperaturfühler am Wärmetauscher | reicht für Heizkörper; für Warmwasser periodisch rund 60 °C (Legionellenschutz) oder eine kleine Nachheizung | Teamvorgabe, mit Installateur klären |
| Nutzbare Wärme | 80 % des Stroms | Wärmezähler | dokumentieren; beeinflusst die Deckung, nicht das Ergebnis (Wärme ist gratis) | Teamvorgabe |
| Zusage am Vortag | 92 % der Stunden zusagbar, Fehlmenge an rund 2 % der Tage | Zusage täglich um 12 Uhr, Vergleich mit Lieferung | Fehlmenge an höchstens 5 % der Tage | Kalibrierziel in `src/scheduler/zusage.py` |
| Lärm und Platz im Keller | – | Messung und Rückmeldung des Haushalts | Haushalt würde verlängern | Teamvorgabe |
| Kühlkreislauf dicht | – | Durchfluss- und Leckagesensor | keine Störung; bei Durchfluss 0 sperrt der Scheduler den Server schon heute | Teamvorgabe |

## Warum die Nachfrage realistisch ist

- **82 % der Rechenstunden fallen in die Heizsaison.** Roche plus ein Kunde für die übrigen Winterstunden reicht für +27'500 CHF pro Jahr pro Haus, auch wenn der Sommer unverkauft bleibt.
- **Die Menge ist klein:** Pro Haus müsste Roche 0,54 % seiner heutigen GPU-Kapazität auslagern.
- Beides ist hergeleitet in [KOSTEN_DH.md, Abschnitt 9](KOSTEN_DH.md#9-nachfrage-zwischen-den-extremen-und-schwellen-für-den-pilotentscheid). Eine Zusage von Roche gibt es noch nicht; sie ist die erste Aufgabe vor dem Pilot.

## Ablauf

1. **Vor dem Winter:** Absichtserklärung des Ankerkunden, Offerte für die Server, Installateur prüft Heizkreis und Warmwasser.
2. **Oktober–März:** Betrieb mit täglicher Zusage am Vortag, alle Messwerte laufend.
3. **April:** Vergleich mit den Schwellen und Neuberechnung mit den gemessenen Werten (`python3 start/alles_neu_rechnen.py` nach Anpassung von `src/scheduler/annahmen.py`).
4. **Entscheid:**
   - Alle Schwellen eingehalten → Ausbau auf 20 Häuser mit Sportbad als Sommerabnehmer.
   - Nachfrage zu klein → nicht ausbauen. Die Server ziehen in Häuser mit gesichertem Winterkontingent oder werden verkauft (Restwert).
   - Technik nicht ausreichend (Temperatur, Leerlauf) → Anlage anpassen und einen zweiten Winter messen, bevor investiert wird.
