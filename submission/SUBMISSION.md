# Vorschläge für die Submission (vorübergehend)

Das Formular ist auf Englisch, darum sind die Texte zum Einfügen auf Englisch. Alle Zahlen stammen aus `docs/ergebnisse/ERGEBNISSE.md` und `docs/wirtschaft/KOSTEN_DH.md`. Nach der Abgabe kann dieser Ordner gelöscht werden.

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
We model 8 liquid-cooled servers (8× NVIDIA L4 each, 8 kW total) in the Basel reference house. The scheduler uses heat demand, a 35 kWh tank and job deadlines to decide when to run AI jobs. The idealised case with zero idle draw covers 93 % of heating and hot water, dumps 5 kWh of heat, meets all deadlines and reaches 52 % utilisation. Break-even (case definition): 0.23 CHF per server-hour. At an assumed 230 W idle draw per server, switching off unused servers saves about 5,200 kWh per year compared with leaving them powered on.
Our heat router shares a job pool across 20 houses and Sportbad St. Jakob, a heated 50 m outdoor pool. Homes get priority. The model starts servers where there is work and demand for heat. The pool's servers stay in standby outside its season. With 50 servers at the pool, annual work passed to other clouds falls from about 195,000 to 30,000 server-hours under the limited-demand scenario.
We sell L4 compute for public, synthetic or customer-anonymised tasks (no confidential data). Assumed prices: an anchor customer (Roche) books 60 % of the hours at 0.50 CHF per L4-hour (4.00 CHF per server-hour); the remaining hours go to customers without minimum volume at 0.55 CHF per L4-hour, falling 10 % per year. These are target prices, not confirmed by a customer. At noon the day before, the ECMWF forecast helps estimate available capacity. About 91 % of modelled capacity can be committed in the fleet with the pool. The reference house with power management yields an annualised result of about CHF 35,000 after all costs, taxes and interest, but only if every hour is sold; at 66 % sold hours it is zero. As a company rolling out 170 houses by 2031 (one hardware generation, no loan), the project IRR is 19.9 % with a capital need of CHF 23.4 million; below about 85 % sold hours it falls under the 12 % investors expect.
Where it does not pay off, we say so: with demand limited to deadline jobs (Alibaba trace), even the fleet with the pool loses money. The bottleneck is demand, not heat.

HOW IT WORKS – REAL VS. MOCKED
Real: an AI job (text embeddings, fastembed) runs on our laptop with measured power (28.9 W) and speed. The same scheduler code that computes the yearly balance pauses it (SIGSTOP/SIGCONT) and migrates it via checkpoint and restart. Live demo: on 25 May 2025 the job runs in house 01 until 10:00, the tank is full, the router moves it to the pool – results are bit-identical to an uninterrupted run. Weather (Open-Meteo), forecasts (ECMWF previous runs), electricity price (ElCom 2026) and hardware prices are real data.
Simulated: the 20 houses and the pool, server power states, job arrivals based on the 2020 Alibaba GPU trace, pool heat demand (estimate ±30 %), and the network between sites during migration.
Reproducible: simulation and costs can be rerun from code. Automated tests cover scheduling, forecasts, and server power states.

NEXT FOUR WEEKS
1. Replace the pool estimate with measured district-heating data from the Sportamt Basel-Stadt.
2. Talk to Roche and 2–3 other Basel companies: would they book a paid winter quota of day-ahead committed Swiss compute at 0.50 CHF per L4-hour (4.00 CHF per server-hour), and for how many hours?
3. Pilot one real server with liquid cooling in a former oil-heated house (oil boiler removed, the existing wood stove as backup): measure supply temperature, heat recovery, idle and standby power, and time from power-on to job readiness.
4. Different houses (heat load, tank size) and a second summer sink (hotel with spa), plus the network cost of migrating jobs.
```

## Repository URL *

```
https://github.com/jayjoee/DigitalHeat_Hackathon
```

Geprüft: Das Repo ist öffentlich und öffnet ohne Login. Das README hat die Setup-Schritte und einen Hinweis zu den KI-Werkzeugen (Claude Code, gstack). **Bitte im Team prüfen:** Mit welchem Werkzeug oder welcher Vorlage ist der Prototyp in `prototyp/` entstanden? Falls mit einem KI-Werkzeug, im README unter «Mit KI gebaut» ergänzen.

## Thumbnail image

Fertig: **`submission/thumbnail_600x600.png`**, 600 × 600 px, echter Screenshot aus dem Dashboard. Oben die Monatsverteilung Häuser/Sportbad, unten die Live-Demo, in der der Job ins Bad wandert.

---

## Checkliste vor dem Absenden
- [ ] Titel, Slogan und Beschreibung eingefügt
- [ ] Repo-URL eingefügt (öffentlich, geprüft)
- [ ] Herkunft von `prototyp/` im README ergänzt (falls KI oder Vorlage)
- [ ] Thumbnail hochgeladen
