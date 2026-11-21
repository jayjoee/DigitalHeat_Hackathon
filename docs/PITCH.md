# Pitch DigitalHeat, Sonntag 8:30 Uhr (5 Minuten + Live-Demo)

Bewertung: Transparenz 25 %, Machbarkeit 25 %, Scheduling 20 %, Kreativität 20 %, Design 10 %.
Alle Zahlen stammen aus dem Code (`ERGEBNISSE.md`, `KOSTEN_DH.md`) und sind in CHF pro **Server-Stunde** angegeben. Ein Server hat 8 L4-Karten, darum gilt: Server-Stunde = 8 × L4-Stunde.

## Der Satz
**Server heizen Basler Häuser im Winter und das Sportbad im Sommer. Ein Wärme-Router verkauft die Rechenzeit einen Tag im Voraus verbindlich an Kunden, deren Daten in der Schweiz bleiben müssen.**

## Ablauf (5 Minuten)

**1. Einstieg mit den Kennzahlen (30 s)**, so verlangt es der Case
«Im Case-Modell decken 8 Server pro Haus 93 % der Wärme. Bei idealisierten 0 Watt Leerlauf fallen 5 kWh ungenutzte Wärme an. Die Server sind zu 52 % ausgelastet und verpassen keine Frist. Der Break-even nach Case-Formel liegt bei 0,23 CHF pro Server-Stunde.»
Danach in einem Satz das Problem: Server machen aus Strom fast nur Wärme, und die wird heute weggekühlt, während Basler Ölheizungen Öl für dieselbe Wärme verbrennen.

**2. Lösung im Haus (45 s)**
- Pro Referenzhaus 8 Server mit Flüssigkühlung. Im Case-Modell decken sie **93 %** der Wärme. Der Haushalt erhält die Wärme **gratis**.
- Beim blossen Pausieren der Jobs verbrauchen die Server weiter Strom. Bei angenommenen 230 W Leerlauf spart das Abschalten ungenutzter Server in der Simulation rund 5'200 kWh Strom pro Jahr. Die Wärmedeckung sinkt dabei von 91,3 % auf 90,5 %, alle Fristen werden eingehalten.
- Der Scheduler rechnet nur, wenn das Haus oder der Speicher die Wärme brauchen kann.
- **Kein Öl mehr:** Ölkessel und Tank kommen raus. Die restlichen 7 % liefert an den kältesten Tagen ein wasserführender Holzofen, der in den Speicher heizt (rund 1,9 Ster Holz pro Jahr).

**3. Was neu ist: der Wärme-Router (60 s)** (Kreativität und Scheduling)
- Das Problem ist der Sommer: Ohne zweiten Abnehmer laufen die Server in den Häusern nur zu 8 %.
- Ein gemeinsamer Auftragspool für 20 Häuser und das **Sportbad St. Jakob**. Das Bad hat ein beheiztes 50-m-Becken und ist genau dann offen, wenn die Häuser keine Wärme brauchen (Ende April bis Anfang Oktober).
- **Die Häuser haben immer Vorrang.** Das Bad nimmt nur Arbeit, deren Wärme kein Haus brauchen kann.
- Pro Standort simuliert der Router, wie viele Server starten oder im Standby bleiben. Im Bad bleiben sie ausserhalb der Saison im Standby.
- Bei knapper Nachfrage sinkt mit dem Bad die externe Abgabe von **195’000 auf 30’000 Serverstunden pro Jahr**. Das verbessert das Jahresergebnis der Flotte um rund **66’600 CHF**.
- Ein Auftrag wandert per Checkpoint zwischen Standorten. Getestet: Das Ergebnis ist exakt dasselbe wie ohne Unterbruch.

**4. Live-Demo (60 s)**, der Case verlangt einen Januartag, einen Julitag und einen unterbrochenen Job (siehe unten)

**5. Geld (45 s)** (Machbarkeit)
- Kunden: Pharma, Banken, Spitäler, deren Daten in der Schweiz und unter Schweizer Recht bleiben müssen.
- Angenommener Vertragspreis **4,80 CHF pro Server-h** (= 0,60 CHF pro L4-h), bei 60 % Festbuchung und Spot-Verkäufen für die übrigen Stunden.
- **Zusage am Vortag um 12 Uhr** aus der ECMWF-Wetterprognose. Im Abschaltmodell mit Bad sind rund 91 % der Stunden zusagbar. Knapp 60 % gehen in der Rechnung als Festbuchung ein.
- Das Einzelhaus mit Abschalten erreicht rund **+29'400 CHF pro Jahr** vor möglichen Gutschriften, bei rund 290'000 CHF Investition.
- Der Vollkosten-Break-even des Einzelhauses mit Abschalten liegt bei **3,07 CHF pro Server-h**, sofern 60 % fest gebucht und die übrigen Stunden zum angenommenen Spot-Preis verkauft werden.
- **Firma** (`docs/FIRMA.md`): Ab **7 Häusern** trägt DigitalHeat ihre Fixkosten. Ausbau auf 170 Häuser bis 2031: Projekt-IRR **33,7 %**, Eigenkapitalbedarf **4,5 Mio. CHF**, Payback 2032. Der Förderbeitrag wie für eine Wärmepumpe (rund 7'200 CHF pro Haus) hilft wenig, Skaleneffekte vor allem bei den Fixkosten.

**6. Ehrlich: wo es nicht trägt (30 s)** (Transparenz)
- Bei der knappen Nachfrage aus dem Alibaba-Trace bleibt die Flotte mit Bad bei rund **−172’000 CHF pro Jahr**. Der feste Absatz von Rechenzeit entscheidet, ob sich die Investition trägt.
- Die 60 % Festbuchung und der Spot-Absatz sind Annahmen, die wir mit Kunden prüfen müssen. Mit knapper Nachfrage fällt die Projekt-IRR der Firma auf −1,5 %.
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
.venv/bin/python src/scheduler/live.py --flotte --sekunden 3 --arbeitsordner "messungen/live_job_flotte/$(date +%s)"
```
- Der Trockenlauf wählt den 25.5.2025. Das dauert rund 20 s vor dem Start; währenddessen erklären.
- **00–09 Uhr:** Der Job rechnet in Haus 01, der Speicher füllt sich von 16 auf 35 kWh (blaue Säulen).
- **10 Uhr:** Der Speicher ist voll. Migration ins Sportbad: Checkpoint bei 2'560 Texten, neuer Prozess (orange Säulen).
- Danach rechnet er im Bad: voll, wenn genug Wärmebedarf frei ist, gedrosselt, wenn Aufträge mit Frist Vorrang haben.
- Für eine Demo mit simulierten Ein/Aus-Zuständen `--abschalten` ergänzen. Mit `--nur-tag` lässt sich vorab der Ablauf ohne Embedding-Prozess prüfen. Das Dashboard zeigt dann Haus und Bad mit Anzahl eingeschalteter Server und Server im Standby.

**Demo B (Reserve): Pause und Weiterlauf im Haus**, 7. März:
```sh
.venv/bin/python src/scheduler/live.py --tag 2025-03-07 --server 8 --sekunden 3
```

**Wenn etwas hängt:** Das Dashboard und `dashboard/artifact/index.html` zeigen die Aufzeichnung des Laufs vom 25.5. (`daten/ergebnisse/live_flotte_2025-05-25.json`).

**Im Dashboard zeigen:** Abschnitt «Flotte», «Bedarfsgerecht abschalten», «Nur Jobs mit Frist». Zwischen «Ohne Bad» und «Sportbad 50 Server» wechseln. Die Kacheln zeigen Gesamtstrom und den Standby-Anteil am Bad.

## Fragen der Jury, kurze Antworten

| Frage | Antwort |
|---|---|
| Ist das wirklich verteilt? | Der echte Job speichert seinen Checkpoint und läuft in einem neuen Prozess auf dem Laptop weiter. Die 21 Standorte, der Netztransfer und der Stromzustand der Server sind simuliert. |
| Warum nicht einfach Rückkühler im Sommer? | Wärme zuerst: Ein Rückkühler macht aus DigitalHeat ein normales Rechenzentrum mit Strom zum Haushaltstarif. |
| Woher kommen die 60 % Festbuchung? | Das ist die Verkaufsannahme. Im Abschaltmodell mit Bad sind rund 91 % der simulierten Rechenkapazität am Vortag zusagbar. Die Abnahme müssen wir mit Kunden prüfen. |
| Wieso 50 Server im Bad und nicht 170? | 170 ergeben sich aus dem geschätzten sommerlichen Wärmebedarf. Im Case-Idealmodell schnitten bei knapper Nachfrage 50 Server am besten ab. Für den Abschaltvergleich haben wir diese Grösse übernommen. |
| Was kostet eine Migration? | Neustart bis rechenbereit rund 0,3 s, Checkpoint bis rund 6 s auf dem Laptop. Der Transfer übers Netz muss im Pilot gemessen werden. |
| Woher kommen die 230 W? | Sensitivität aus einem H100-Vergleich. Beim Pilot messen wir Leerlauf, Standby und Startzeit am geplanten L4-Server. |
| Datensicherheit im Privatkeller? | Verplombtes Gehäuse, Verschlüsselung, ISO 27001 (Premise im Design-Doc). Der Prototyp trennt die Oberflächen für Serverhalter und Pharma (`prototyp/`). |
| Warum kein Hallenbad? | Das Rialto macht im Sommer Pause, das Hallenbad Eglisee steht nur im Winter. Das Sportbad St. Jakob ist offen, wenn die Häuser keine Wärme brauchen. |
| Ist 2025 repräsentativ? | 2025 war ein milder Winter. In den Jahren 2010–2025 schwankt die Deckung zwischen 84,5 % und 95,9 % (`ANNAHMEN_PRUEFUNG.md`). |

## Nachweise (für Rückfragen)
- Tests: `python3 -m unittest discover -s tests` (Regression, Router, Prognose und Serverbetrieb)
- Vektorvergleich mit Migration: `messungen/vektorvergleich.json` (Abweichung 0,0)
- Annahmen mit Quelle: `src/scheduler/annahmen.py`, im Dashboard unter «Alle Annahmen mit Quelle»
