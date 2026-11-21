# Vorschläge für die Submission (vorübergehend)

Das Formular ist auf Englisch, darum sind die Texte zum Einfügen auf Englisch. Alle Zahlen stammen aus `docs/ERGEBNISSE.md` und `docs/KOSTEN_DH.md`. Nach der Abgabe kann dieser Ordner gelöscht werden.

---

## Project title *

```
Rechnen, das heizt – a heat router for Basel
```

Alternative: `DigitalHeat Router: Computing that heats Basel`

## Slogan

Eine Zeile: was es tut und für wen.

```
Servers in Basel basements heat homes in winter and the public pool in summer, sold as day-ahead Swiss compute to pharma, banks and hospitals.
```

Kürzer: `AI jobs that heat Basel homes in winter and the swimming pool in summer.`

## Description

Reihenfolge wie verlangt: Problem, Lösung, wie es funktioniert (echt oder simuliert), nächste vier Wochen.

```
THE PROBLEM (in DigitalHeat's words)
"Servers turn almost all electricity into heat, which is usually cooled away with more energy. Homes spend money and energy to produce heat." The open questions: which workloads fit, how to schedule them against a home's heat demand across the year, and when it pays off.

OUR SOLUTION
We put 8 liquid-cooled servers (8× NVIDIA L4 each, 8 kW total) into the reference house in Basel. A scheduler only runs AI jobs when the house or its 35 kWh water tank can use the heat. Result for 2025 weather: 93 % of heating and hot water covered, 5 kWh of heat dumped in the whole year, 0 % missed deadlines, 52 % utilisation. Break-even (case definition): 0.23 CHF per server-hour.
The summer gap is the real problem: houses only need hot water, servers drop to 8 % utilisation. Our answer is a heat router: one shared job pool for 20 houses plus the Sportbad St. Jakob, a heated 50 m outdoor pool that is open exactly when houses need no heat (late April to early October). Houses always have priority; the pool only takes work whose heat no house can use. Work given away to other clouds without revenue drops from 180,000 to 12,500 server-hours per year.
Customers are companies whose data must stay in Switzerland (pharma, banks, hospitals). We sell 4.80 CHF per server-hour (12 % below Swiss GPU clouds) – but only for hours we commit to at noon the day before, based on the ECMWF weather forecast. 93 % of hours can be committed, shortfalls happen on about 2 % of days. Net result after all costs, taxes and interest: +34,300 CHF per house and year, payback in 3 years.
Where it does not pay off, we say so: with demand limited to deadline jobs (Alibaba trace), even the fleet with the pool loses money. The bottleneck is demand, not heat.

HOW IT WORKS – REAL VS. MOCKED
Real: an AI job (text embeddings, fastembed) runs on our laptop with measured power (28.9 W) and speed. The same scheduler code that computes the yearly balance pauses it (SIGSTOP/SIGCONT) and migrates it via checkpoint and restart. Live demo: on 25 May 2025 the job runs in house 01 until 10:00, the tank is full, the router moves it to the pool – results are bit-identical to an uninterrupted run. Weather (Open-Meteo), forecasts (ECMWF previous runs), electricity price (ElCom 2026) and hardware prices are real data.
Simulated: the houses, the pool and the 20-site fleet (hourly models); the job stream (based on the Alibaba GPU trace 2020); the pool's heat demand (estimate ±30 % from the Swiss pool association guideline); the network between sites during migration.
Reproducible: every number comes from code, every assumption has a source in one file (src/scheduler/annahmen.py), 22 automated tests incl. regression tests and a check that no forecast published after the decision is used.

NEXT FOUR WEEKS
1. Replace the pool estimate with measured district-heating data from the Sportamt Basel-Stadt.
2. Talk to 2–3 Basel pharma/biotech companies: would they buy day-ahead committed Swiss compute at 4.80 CHF per server-hour, and for how many hours?
3. Pilot one real server with liquid cooling in an oil-heated house: measure supply temperature, idle power and real heat recovery.
4. Different houses (heat load, tank size) and a second summer sink (hotel with spa), plus the network cost of migrating jobs.
```

## Repository URL *

```
https://github.com/jayjoee/DigitalHeat_Hackathon
```

Geprüft: Das Repo ist öffentlich und öffnet ohne Login. Das README hat die Setup-Schritte und einen Hinweis zu den KI-Werkzeugen (Claude Code, gstack). **Bitte im Team prüfen:** Mit welchem Werkzeug oder welcher Vorlage ist der Prototyp in `prototyp/` entstanden? Falls mit einem KI-Werkzeug, im README unter «Mit KI gebaut» ergänzen.

## Video pitch URL *

Ein Video gibt es noch nicht. Vorschlag für eine Bildschirmaufnahme mit Stimme, rund 3 Minuten (macOS: `Cmd + Shift + 5`, danach als «Nicht gelistet» auf YouTube hochladen):

| Zeit | Bild | Was man sagt |
|---|---|---|
| 0:00–0:20 | Dashboard oben: Kacheln | «8 Server pro Haus, 93 % der Wärme gedeckt, fast nichts weggekühlt, keine Frist verpasst.» |
| 0:20–0:50 | Januartag und Julitag im Dashboard | «Im Januar laufen alle 8 Server. Im Juli braucht das Haus nur Warmwasser, die Server stehen fast still.» |
| 0:50–1:30 | Abschnitt «Flotte», Senke «Sportbad 50 Server» | «Der Wärme-Router schickt die Sommerarbeit ins Sportbad. Häuser haben Vorrang.» |
| 1:30–2:30 | Terminal + Dashboard: `live.py --flotte` | «Das ist ein echter Prozess. Um 10 Uhr ist der Tank voll, der Job speichert und läuft im Bad weiter.» |
| 2:30–3:00 | Zusage-Diagramm, dann Kachel «Ergebnis» | «Wir sagen am Vortag zu, 93 % sind planbar. +34'300 CHF pro Haus und Jahr. Zu wenig Aufträge: dann lohnt es sich nicht.» |

## Project ZIP (optional, max. 500 MB)

Nicht nötig, denn alles liegt im Repo. Falls die Jury es offline will, ZIP mit klaren Namen:
- `DigitalHeat_Dashboard_offline.html` (= `dashboard/artifact/index.html`, läuft ohne Installation)
- `DigitalHeat_Pitch.md` (= `docs/PITCH.md`)
- `DigitalHeat_Resultate_einfach.md` (= `docs/RESULTATE_EINFACH.md`)

## Thumbnail image

Fertig: **`submission/thumbnail_600x600.png`**, 600 × 600 px, echter Screenshot aus dem Dashboard. Oben die Monatsverteilung Häuser/Sportbad, unten die Live-Demo, in der der Job ins Bad wandert.

---

## Checkliste vor dem Absenden
- [ ] Titel, Slogan und Beschreibung eingefügt
- [ ] Repo-URL eingefügt (öffentlich, geprüft)
- [ ] Herkunft von `prototyp/` im README ergänzt (falls KI oder Vorlage)
- [ ] Video aufgenommen, als «Nicht gelistet» hochgeladen, Link ohne Login getestet
- [ ] Thumbnail hochgeladen
