# Results and assumptions in plain English

## Basel reference house, 2025

The reference house needs **31'231 kWh** of heat in 2025. Space heating accounts for 26'851 kWh and hot water for 4'380 kWh. The model uses hourly Basel weather, a 20 °C indoor setpoint, a 12 °C daily-average threshold for heating days and 12 kWh of hot water per day. It assumes a 1'000-litre tank with 35 kWh of usable storage and zero storage losses. Each reference server draws 1 kW at full load and transfers 0.8 kW to water. [Reference case](../CASE.md)

| Metric | Case baseline, 8 servers | Demand-based shutdown, 8 servers |
|---|---:|---:|
| Share of heat demand covered | 93 % | 90.5 % |
| Heat rejected over the year | 5 kWh | Less than 1 kWh in the model |
| Server-hours running | 36'290 | 34'512 |
| Utilisation (running hours ÷ installed servers ÷ 8'760) | 51.8% | 49.2% |
| Missed deadlines | 0% | 0% |
| Electricity cost | About CHF 12'066 | About CHF 11'858 |

The 5 kWh figure assumes 0 W when a server is paused. With demand-based shutdown we assume 230 W at idle, 10 W in standby and a five-minute startup. Keeping the same servers powered while paused would reject about 4'200 kWh of heat and use roughly 5'200 kWh more electricity. Real L4 measurements are pending. A backup heat source covers the remaining demand. The household example assumes an existing wood stove. [Annual results data](../../daten/ergebnisse/bilanz_8_spot.json) · [Power-state sensitivity data](../../daten/ergebnisse/serverbetrieb.json)

## How the heat router works

The router checks heat demand and available storage each hour. It schedules flexible jobs while the heat is useful and pauses or moves them when it cannot be used. Short, non-interruptible jobs have a deadline. The policy decides whether to complete them locally, even if heat is rejected, or send them outside the site.

In the 20-house scenario, houses have priority. The heated St. Jakob sports pool can take jobs during its outdoor season. The model estimates its seasonal heat demand at roughly 650'000 kWh with an uncertainty band of ±30%. With limited demand, adding 50 pool servers reduces external transfers from about 195'000 to 30'000 server-hours, but the modelled fleet remains loss-making at that demand level. The day-ahead commitment uses only forecasts available by noon on the previous day. It covers about 93% of reference-house server-hours in the tested scenario. [Fleet data](../../daten/ergebnisse/flotte_abschalten.json) · [Day-ahead data](../../daten/ergebnisse/zusage_8_spot.json)

## What the business model assumes

The assumed tariff is CHF 0.3325/kWh. The case values useful heat at CHF 0.133/kWh, based on a heat pump with a factor of 2.5. The case break-even equals **(electricity cost − value of useful heat) ÷ server-hours sold**. In the baseline it is **CHF 0.226 per server-hour**, roughly CHF 0.23. This measure covers energy economics. Hardware and other expenses are included in the separate business model.

| Business scenario, demand-based shutdown | Equivalent annual result |
|---|---:|
| All hours sold at the target prices | About CHF 35'000 |
| Anchor customer plus a customer for the remaining winter hours | About CHF 27'500 |
| Anchor customer plus remaining hours at the modelled spot price | About CHF 15'800 |
| Anchor customer only | About −CHF 6'400 |

The hypothetical anchor customer buys 60% of hours at CHF 0.50 per L4-hour. Other customers pay CHF 0.55 in the fully sold scenario, which generates approximately CHF 135'400 of first-year compute revenue. The anchor price, additional demand and volumes are unconfirmed. The reference house costs about CHF 290'000 to equip. The depreciation period is five years, and the scenario breaks even at **66 %** of hours sold under the modelled sales mix. The switch-off scenario assumes free heat for the household. [Financial model data and assumptions](../../daten/ergebnisse/kosten_dh.json)

## What the demos establish

- A real local text-embedding or molecular docking process responds to heat decisions from the scheduler used for the annual balance.
- In the two-laptop docking demo, the checkpoint and route changes are live. The standard screens replay earlier Vina results while simulating the tank, heat demand and model clock.
- The laptop embedding measurements document throughput and chip power. Physical heating performance, L4 operating power, actual workloads and customer willingness to pay remain pilot questions. [Workload definitions and measurement methods](../../daten/JOBTYPEN.md)
