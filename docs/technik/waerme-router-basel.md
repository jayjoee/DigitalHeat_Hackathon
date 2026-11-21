# Wärme-Router für Basel: Bauplan und Entscheide

Stand 21.11.2026. Kurzfassung des Design-Dokuments; umgesetzt in `src/scheduler/`. Ergebnisse stehen in [ERGEBNISSE.md](../ergebnisse/ERGEBNISSE.md), Geld in [KOSTEN_DH.md](../wirtschaft/KOSTEN_DH.md).

## Ausgangslage

Der Case verlangt einen Scheduler, der unterbrechbare Aufträge «across distributed servers» nach Wärmebedarf verteilt. Ein einzelnes Referenzhaus hatte drei Schwächen:
1. **Nicht verteilt.** Die Regel `abgeben` schickte Aufträge an einen Standort, der nicht modelliert war.
2. **Sommerloch.** Von Juni bis August laufen in einem Haus nur 8 % der Server.
3. **Kennzahlen konstruktionsbedingt gut.** 0 % verpasste Fristen und 5 kWh abgeführt folgen aus «unbegrenzt pausierbare Aufträge». Ohne diese Annahme (Alibaba-Trace) sind es rund 52 % Deckung.

## Gewählter Ansatz

Eine Flotte aus Wohnhäusern und einem Sommerabnehmer in einem Jahresmodell, ein Router über dem unveränderten Kern `kern.entscheide()` und eine Zusage am Vortag. Verworfen wurden ein reines Einzelhaus (nicht verteilt) und eine echte Migration zwischen zwei Laptops (zu hohes Demo-Risiko).

**Prämissen:**
1. Preise: Ankerkunde 0,50 CHF pro L4-Stunde, übrige Stunden 0,55 CHF ([KOSTEN_DH.md](../wirtschaft/KOSTEN_DH.md)). Nur öffentliche oder freigegebene Aufträge, keine vertraulichen Daten ([L4_ANGEBOT.md](../kunden/L4_ANGEBOT.md)).
2. Wärme zuerst: Server laufen nur, wenn ein Standort die Wärme brauchen kann. Kein Dauerbetrieb mit Rückkühler.
3. Der Engpass ist die Nachfrage, nicht die Technik.
4. Datensicherheit im Privatkeller: verplombtes Gehäuse, getrennte Netze, ISO 27001.
5. Pilot mit Ölheizungen in Basel-Stadt, Gratiswärme für Haushalte.

## Bausteine

Die Nummern werden im Code zitiert.

1. **Standorte** (`flotte.py`): Ein Standort ist ein `Haus`-Objekt mit Typ (`haus`, `bad`), Serverzahl, Speicher und Wärmeprofil. Serverzahl Haus: kleinste Zahl mit Deckung ≥ 92,9 % (Referenzhaus: 8).
2. **Aufteilung von `Haus.schritt`** (`jahr.py`): `vorbereiten`, `lage`, `verbuchen`; Verhalten unverändert (Regressionstest).
3. **Router** (`router.py`): gemeinsamer Auftragspool. Pro Stunde zuerst Pflichtaufträge an den Standort mit dem grössten freien Wärmeziel, dann entscheidet jeder Standort mit `kern.entscheide()`. Angefangene Aufträge bleiben an ihrem Standort, solange dort Wärme gebraucht wird; sonst wandern sie per Checkpoint (Migration). Nicht unterbrechbare Aufträge wandern nie.
4. **Nachfrage:** «Genug Aufträge» (unbegrenzt pausierbare Aufträge) und «Nur Jobs mit Frist» (Alibaba-Trace, gleicher Auftragsstrom für alle Varianten).
5. **Zusage am Vortag** (`zusage.py`): Entscheid um 12 Uhr am Vortag mit dem ECMWF-Lauf, der zu diesem Zeitpunkt veröffentlicht war (Open-Meteo «Previous Runs»). Ein Trockenlauf des nächsten Tages ergibt die Prognose; zugesagt wird Sicherheitsfaktor × Prognose. Kalibriert auf Januar–Juni 2025, ausgewertet auf Juli–Dezember 2025 (für 2024 gibt es keine Previous Runs).
6. **Wirtschaft** (`wirtschaft.py`): Fehlmenge als Kostenposition (fehlende Stunde unbezahlt plus 50 % Gutschrift), Rechnung pro Standort.
7. **Ehrliche Kennzahlen:** Jede Hauptzahl steht neben dem Szenario «Nur Jobs mit Frist»; Auslastung getrennt für Haus- und Bad-Server.
8. **Dashboard:** Abschnitt «Flotte» mit vorgerechneten Ergebnissen.
9. **Demo** (`live.py --flotte`): Ein markierter Auftrag ist ein echter Prozess. Pause mit SIGSTOP/SIGCONT, Migration mit SIGTERM (Checkpoint) und Neustart. Ergebnis mit und ohne Migration identisch (`messungen/vektorvergleich.json`).

## Entscheide im Code

- **Vorrang (Team-Entscheid):** Wohnhäuser haben immer Vorrang. Das Bad nimmt nur Rechenlast, deren Wärme kein Haus brauchen kann; ein Haus darf einen angefangenen Auftrag vom Bad zurückholen.
- **Sommerabnehmer:** Sportbad St. Jakob, offen Ende April bis Anfang Oktober (`daten/HALLENBAD.md`, Wärmebedarf geschätzt ±30 %). Ein Hallenbad scheidet aus: Das Rialto hat Sommerpause, das Hallenbad Eglisee steht nur im Winter.
- **Grösse des Bads:** Die Regel «so viele Server, wie der Sommerbedarf aufnimmt» ergibt 170 Server, viel mehr als Aufträge da sind. Die Grösse nach Nachfrage (Suche 10–80 Server) ergibt 50.
- **Pflichtaufträge ohne freien Server** gehen trotzdem an den Standort mit dem grössten freien Wärmeziel; dort entscheidet der Kern wie im Einzelhaus. Jeder Auftrag wird pro Stunde genau einmal gezählt.
- **Einheiten:** Der Code rechnet in CHF pro L4-Stunde, Pitch und Dashboard zeigen × 8 pro Server-Stunde.
- **Gleiche Häuser gleichen sich nicht aus:** 20 Häuser mit demselben Wetter rechnen so viel wie 20 einzelne. Nutzen entsteht erst mit einem Standort, der zu anderen Zeiten Wärme braucht.

## Offen

- Wärmebedarf des Sportbads mit Messwert ersetzen.
- Vorlauftemperatur: Flüssigkühlung liefert je nach System rund 45–60 °C. Für Warmwasser mit 60 °C (Legionellen) braucht es an einzelnen Tagen eine Nachheizung; wird im Pilot gemessen ([PILOTPLAN.md](../wirtschaft/PILOTPLAN.md)).
- Übertragung von Checkpoint und Modell über das Netz bei der Migration messen.
- Verschiedene Häuser in der Flotte und eine zweite Senke (Hotel mit Spa): verschoben ([TODO.md](../TODO.md)).
