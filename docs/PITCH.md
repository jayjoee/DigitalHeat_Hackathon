# Pitch DigitalHeat, Sonntag 8:30 Uhr (5 Minuten + Live-Demo)

Bewertung: Transparenz 25 %, Machbarkeit 25 %, Scheduling 20 %, Kreativität 20 %, Design 10 %.
Alle Zahlen stammen aus dem Code (`ERGEBNISSE.md`, `KOSTEN_DH.md`) und sind in CHF pro **Server-Stunde** angegeben. Ein Server hat 8 L4-Karten, darum gilt: Server-Stunde = 8 × L4-Stunde.

## Der Satz
**Server heizen Basler Häuser im Winter und das Sportbad im Sommer. Ein Wärme-Router verkauft die Rechenzeit einen Tag im Voraus verbindlich an Kunden, deren Daten in der Schweiz bleiben müssen.**

## Ablauf (5 Minuten)

**1. Einstieg mit den Kennzahlen (30 s)**, so verlangt es der Case
«8 Server pro Haus. 93 % der Wärme gedeckt. 5 kWh im ganzen Jahr weggekühlt. 52 % Auslastung. 0 % verpasste Fristen. Break-even 0,23 CHF pro Server-Stunde.»
Danach in einem Satz das Problem: Server machen aus Strom fast nur Wärme, und die wird heute weggekühlt, während Basler Ölheizungen Öl für dieselbe Wärme verbrennen.

**2. Lösung im Haus (45 s)**
- Pro Referenzhaus 8 Server mit Flüssigkühlung. Sie decken **93 %** der Wärme, der Haushalt bekommt sie **gratis**.
- Im Jahr werden nur 5 kWh weggekühlt, und keine Frist wird verpasst.
- Der Scheduler rechnet nur, wenn das Haus oder der Speicher die Wärme brauchen kann.

**3. Was neu ist: der Wärme-Router (60 s)** (Kreativität und Scheduling)
- Das Problem ist der Sommer: Ohne zweiten Abnehmer laufen die Server in den Häusern nur zu 8 %.
- Ein gemeinsamer Auftragspool für 20 Häuser und das **Sportbad St. Jakob**. Das Bad hat ein beheiztes 50-m-Becken und ist genau dann offen, wenn die Häuser keine Wärme brauchen (Ende April bis Anfang Oktober).
- **Die Häuser haben immer Vorrang.** Das Bad nimmt nur Arbeit, deren Wärme kein Haus brauchen kann.
- Wird eine Frist knapp und braucht niemand die Wärme, geht die Arbeit an eine andere Schweizer Cloud: ohne Bad **180'000 Server-h** im Jahr, mit Bad nur **12'500 Server-h**.
- Ein Auftrag wandert per Checkpoint zwischen Standorten. Getestet: Das Ergebnis ist exakt dasselbe wie ohne Unterbruch.

**4. Live-Demo (60 s)**, der Case verlangt einen Januartag, einen Julitag und einen unterbrochenen Job (siehe unten)

**5. Geld (45 s)** (Machbarkeit)
- Kunden: Pharma, Banken, Spitäler, deren Daten in der Schweiz und unter Schweizer Recht bleiben müssen.
- Preis **4,80 CHF pro Server-h** (= 0,60 CHF pro L4-h), rund 12 % unter Hikube (5,44 CHF).
- **Zusage am Vortag um 12 Uhr** aus der ECMWF-Wetterprognose: 93 % der Stunden lassen sich zusagen, verkauft werden 60 %. An rund 2 % der Tage fehlt etwas, die Gutschrift kostet rund 270 CHF pro Jahr.
- Ergebnis nach allen Kosten, Steuern und Zinsen: **+34'300 CHF pro Haus und Jahr**. Investition 290'000 CHF, nach **3 Jahren** zurück.
- Ab **2,87 CHF pro Server-h** rechnet es sich (Break-even), Spielraum ist also da.

**6. Ehrlich: wo es nicht trägt (30 s)** (Transparenz)
- Gibt es nur Aufträge mit Frist (Nachfrage wie im Alibaba-Trace), macht auch die Flotte mit Bad Verlust: −101'000 CHF pro Jahr für 20 Häuser. Der Router verteilt Arbeit, er schafft keine neue. **Der Engpass ist die Nachfrage, nicht die Wärme.**
- Darum der feste Vertrag. Unter 0,36 CHF pro L4-h oder unter rund 40 % fest gebuchten Stunden lohnt es sich nicht.
- Der Wärmebedarf des Bads ist eine Schätzung (±30 %). Ein Messwert vom Sportamt würde sie ersetzen.

**7. Schluss (15 s)**
«Wir verkaufen nicht billige Restkapazität, sondern planbare Schweizer Rechenzeit. Und im Keller wird es warm.»

## Live-Demo

**Vorbereitung (vor dem Pitch, Terminal im Repo):**
```sh
bash dashboard/starten.sh                    # Dashboard auf http://localhost:8765
```
Browser öffnen und zum Abschnitt «Echter Job, live gesteuert» scrollen.

**Zuerst im Dashboard (20 s):** Januartag und Julitag zeigen, die Diagramme «Ein Januartag» und «Ein Julitag». Im Januar laufen alle 8 Server, im Juli im Mittel 0,6.

**Demo A: Der Job wird unterbrochen und wandert vom Haus ins Bad** (ca. 90 s, zweites Terminal):
```sh
rm -rf messungen/live_job_flotte             # frischer Arbeitsordner, damit die Textzahlen wie unten stimmen
.venv/bin/python src/scheduler/live.py --flotte --sekunden 3
```
- Der Trockenlauf wählt den 25.5.2025. Das dauert rund 20 s vor dem Start; währenddessen erklären.
- **00–09 Uhr:** Der Job rechnet in Haus 01, der Speicher füllt sich von 16 auf 35 kWh (blaue Säulen).
- **10 Uhr:** Der Speicher ist voll. Migration ins Sportbad: Checkpoint bei 2'560 Texten, neuer Prozess (orange Säulen).
- Danach rechnet er im Bad: voll, wenn genug Wärmebedarf frei ist, gedrosselt, wenn Aufträge mit Frist Vorrang haben.

**Demo B (Reserve): Pause und Weiterlauf im Haus**, 7. März:
```sh
.venv/bin/python src/scheduler/live.py --tag 2025-03-07 --server 8 --sekunden 3
```

**Wenn etwas hängt:** Das Dashboard und `dashboard/artifact/index.html` zeigen die Aufzeichnung des Laufs vom 25.5. (`daten/ergebnisse/live_flotte_2025-05-25.json`).

**Im Dashboard zeigen:** Abschnitt «Flotte», Umschalter «Nur Jobs mit Frist», Senke «Sportbad 50 Server». Die orangen Säulen füllen Mai bis September, grün ist die abgegebene Arbeit.

## Fragen der Jury, kurze Antworten

| Frage | Antwort |
|---|---|
| Ist das wirklich verteilt? | Ja: ein Pool, 21 Standorte, Router pro Stunde, Migration per Checkpoint. Derselbe Kern rechnet die Jahresbilanz und steuert den echten Prozess. |
| Warum nicht einfach Rückkühler im Sommer? | Wärme zuerst: Ein Rückkühler macht aus DigitalHeat ein normales Rechenzentrum mit Strom zum Haushaltstarif. |
| Woher wisst ihr, dass 60 % fest verkauft werden? | Wissen wir nicht. Zusagbar sind 93 %, belegt mit der Prognose. Ob Kunden 60 % kaufen, ist die Hauptannahme. Der Schieberegler im Dashboard zeigt die Folgen. |
| Wieso 50 Server im Bad und nicht 170? | 170 Server würden die Wärme decken, aber so viele Aufträge gibt es nicht. 50 Server bringen das beste Ergebnis (Suche von 10 bis 80). |
| Was kostet eine Migration? | Neustart bis rechenbereit 0,3 s, Checkpoint bis 6 s. Die 3'457 Migrationen im Jahr kosten zusammen rund 2 kWh. Nicht gerechnet: Übertragung über das Netz. |
| Datensicherheit im Privatkeller? | Verplombtes Gehäuse, Verschlüsselung, ISO 27001 (Premise im Design-Doc). Der Prototyp trennt die Oberflächen für Serverhalter und Pharma (`prototyp/`). |
| Warum kein Hallenbad? | Das Rialto macht im Sommer Pause, das Hallenbad Eglisee steht nur im Winter. Das Sportbad St. Jakob ist offen, wenn die Häuser keine Wärme brauchen. |
| Ist 2025 repräsentativ? | 2025 war ein milder Winter. In den Jahren 2010–2025 schwankt die Deckung zwischen 84,5 % und 95,9 % (`ANNAHMEN_PRUEFUNG.md`). |

## Nachweise (für Rückfragen)
- Tests: `python3 -m unittest discover -s tests` (22 Tests, darunter Regressionstests, Router-Regeln und die Prüfung, dass keine Prognose nach dem Entscheid verwendet wird)
- Vektorvergleich mit Migration: `messungen/vektorvergleich.json` (Abweichung 0,0)
- Annahmen mit Quelle: `src/scheduler/annahmen.py`, im Dashboard unter «Alle Annahmen mit Quelle»
