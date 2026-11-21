# Case: Useful Load ⇒ Useful Heat (DigitalHeat)

Can your computing power heat a home while doing useful work?

## Problem
Servers turn almost all electricity into heat, which is usually cooled away with more energy. Homes spend money and energy to produce heat. Open questions: which workloads fit, how to schedule them against a home's heat demand across the year, and when it pays off. Build alternatives to big data centres.

## Expected outcome
A working demonstrator that schedules interruptible computing jobs across distributed servers so their heat arrives where and when homes need it, over a full year. Transparent, reproducible numbers: useful heat, useful computing, cost.

## Who it serves
DigitalHeat; homeowners and building operators who want lower heating costs.

## Starting assumptions (DigitalHeat, simplified)
- 1 rack server: 1 kW electricity → ~1 kW heat
- 80 % of the heat recoverable into a water-based heating system
- Typical house: ~10 kW heating power on a cold winter day
- 1 server continuously: ~19.2 kWh recoverable heat per day
- Heating Oct–Mar, hot water all year
- Recovered heat usable for space heating and hot water without heat pump

Tension: coldest hour needs ~12.5 servers (10 ÷ 0.8), summer hot water ~0.6 (12 ÷ 19.2). Servers per house and what they do Apr–Sep: team decision.

## Reference house (same for every team)
- Weather: Open-Meteo historical archive, Basel (47.56 N, 7.59 E), 1.1.–31.12.2025, hourly, Europe/Zurich: temperature_2m, solar irradiance. https://open-meteo.com/en/docs/historical-weather-api
- Heating demand per hour: max(0, 10 kW × (20 − T) ÷ 25.6), only on heating days. Heating day = local calendar day (00–23 h) with mean of 24 hourly values < 12 °C. 25.6 fixed (20 − (−5.6 °C)). ≈ 27,000 kWh/year on 206 heating days.
- Ready hourly profile (weather, heating demand, hot water) provided as CSV with the case → `daten/`
- Hot water: 12 kWh/day, all year
- Storage: 1 water tank, ~35 kWh usable (1,000 l, 30 K), no losses
- Electricity price: ElCom 2026, IWB Basel, category H4, total price per kWh incl. fees, flat. https://www.strompreis.elcom.admin.ch
- Heat value: electricity price ÷ 2.5 (replaces heat pump, COP 2.5)

Report key figures for this reference house. Other houses/tanks/prices optional on top.

## Open data
- MLPerf Inference with power: https://mlcommons.org/benchmarks/inference-datacenter/
- Alibaba GPU cluster trace 2020: https://github.com/alibaba/clusterdata/tree/master/cluster-trace-gpu-v2020 (inspiration)
- Cloud on-demand and spot prices
- Own job types allowed (runtime, power, deadline) with source for each number

## Technology
No hardware or special access. Own laptop, any language/framework/model. At least one real workload runs locally (CPU is enough).

## Core use case
Cold January day in Basel, ~10 kW demand: system checks weather forecast, assigns AI jobs (embeddings, transcription, image recognition) to basement servers, pauses or moves lower-priority jobs once storage is full. July: only hot water → servers run less, jobs move to sites with summer heat demand (hotels, spas, agriculture, businesses), or heat is dumped. Dashboard shows balance per house and year.

## Must-haves (all on the reference house)
1. **Workloads:** ≥ 2 job types (e.g. embeddings, reranking, image recognition, transcription) with runtime and energy per job (own measurement or open benchmark), interruptible yes/no, deadline. ≥ 1 job type actually runs locally with measured runtime. Energy from software meter or runtime × device power; state scaling to 1 kW reference server. State jobs per day and source; a model with unlimited jobs must say so.
2. **Scheduling:** distribute, pause, reschedule jobs across servers by heat demand (winter heating, summer hot water), incl. simple heat storage and what happens to a job when its heat is not needed. The same scheduler code that produces the yearly balance must control ≥ 1 real running job: pause/resume (or checkpoint stop/restart) based on the heat signal.
3. **Balance per house and year:** servers per house; share of total heat demand (space heating + hot water) covered by server heat (rest from backup heater outside the model); heat dumped; utilisation (running hours ÷ (servers × 8,760)); missed deadlines in % of jobs; electricity cost and computing income; break-even computing price in CHF per server-hour = (electricity cost − value of heat actually used) ÷ server-hours sold. All assumptions visible, clear statement when the model does not pay off.

## Success for DigitalHeat
Prototype runs real jobs locally and shows in auditable numbers that distributed servers can meet a home's heat demand across the year without destroying hardware profitability.

## Stretch (only after must-haves)
Prepper Challenge: solar + computing + thermal storage for self-sufficiency. Not scored separately.
Out of scope: feeding heat into district heating (outlook in pitch only).

## Presentation
5 min pitch incl. live demo + 3 min Q&A.
- Open with key figures: servers per house, share covered, heat dumped, utilisation, missed deadlines, break-even price
- Live demo: one January day, one July day, one interrupted job (real process paused/resumed by scheduler on heat signal)

## Prototype requirements
Working demonstrator, list of all assumptions, reproducible measurements/calculations (code in repo, notebooks fine). ≥ 1 real job under scheduler control. Spreadsheet, slides or simulation alone are not valid.

## Jury
| Criterion | Weight | Rewarded |
|---|---|---|
| Transparency & reproducibility | 25 % | Traceable, repeatable, every assumption visible |
| Feasibility | 25 % | Basis for a pilot decision, knows where assumptions stop holding, says when it doesn't pay off |
| Scheduling quality & impact | 20 % | First share covered at least heat dumped, then utilisation and missed deadlines |
| Creativity & innovation | 20 % | Fresh, practical idea for matching computing to heat |
| Design & usability | 10 % | Homeowner or utility understands result in one minute |

## Contacts
- Dr. Vera Chiquet, co-initiator DigitalHeat (concept, business)
- Prof. Dr. Peter Fornaro, co-initiator DigitalHeat (technical)
