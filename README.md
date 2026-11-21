# DigitalHeat — useful computing, useful heat

DigitalHeat schedules computing jobs where their waste heat can warm homes in Basel or the St. Jakob sports pool in summer. Holyhackers built this prototype for the [DigitalHeat case](docs/CASE.md).

## Run the demos

Run the commands from the repository root. The dashboards and the recorded two-laptop demo work with Python 3.10 or later on macOS or Linux. The two-laptop demo also uses OpenSSL.

### 3D dashboard and live tracker

Start the dashboard and open [the 3D view](http://127.0.0.1:8765/3d/).

```sh
bash dashboard/starten.sh
```

Use **January day** and **July day** to compare winter heating with summer hot water. The 3D view includes the houses, storage, server states, thermostat and sports pool. The [analysis dashboard](http://127.0.0.1:8765/) shows the yearly figures and assumptions. You can also open `dashboard/artifact/index.html` directly for an offline version with recorded playback.

Set up AutoDock Vina using the [Docking setup guide](daten/docking/README.md). Keep the dashboard server running and start the scheduler in a second terminal:

```sh
python3 src/scheduler/live.py --tag 2025-03-07 --server 8 --sekunden 3 --job docking
```

The **LIVE** tracker shows the running job and completed molecule count. The same scheduler used for the annual simulation pauses and resumes the real local process according to simulated heat demand. This run plays 24 model hours in about 75 seconds.

### Screening handoff between house and sports pool

Use the same code version on two laptops connected to the same network. Start the **sports pool** first and enter its six-digit code on the **house** laptop. Click **Start screening** in the house browser.

| Laptop | Command | Local view |
|---|---|---|
| Sports pool | `python3 prototyp/schwimmbad.py` | [Port 8092](http://127.0.0.1:8092/) |
| House | `python3 prototyp/haus.py` | [Port 8082](http://127.0.0.1:8082/) |

The screens exchange checkpoints over TLS and show the job moving **house → sports pool → house**. The heat timeline is simulated, and the standard demo plays recorded Vina results. To try both screens on one laptop:

```sh
python3 prototyp/docking_demo.py demo --open
```

For the separate image inspection demo, append `--job blister` to both two-laptop commands. See the [blister inspection guide](prototyp/blister/README.md) and the [application prototype guide](prototyp/README.md).

### Guided demo with local text embeddings

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements/live.txt
.venv/bin/python -c 'from fastembed import TextEmbedding; TextEmbedding("BAAI/bge-small-en-v1.5")'
.venv/bin/python start/demo_start.py --open
```

Open [the guided demo](http://127.0.0.1:18200/) and click **Start live demo**. It shows a winter day, a summer day and a pause when the tank fills. The embedding process runs locally.

## Reference-house results

| Metric | Result and assumptions |
|---|---|
| Annual heat demand | 31'231 kWh in Basel in 2025, including space heating and hot water |
| Servers per house | 8, rated at 1 kW each in the case, with 80% heat recovery into water |
| Ideal case baseline (0 W when paused) | 93 % of heat demand covered, 5 kWh of heat rejected, 51.8% utilisation, 0.0% missed deadlines |
| Case break-even | CHF 0.226 per server-hour, based on electricity less the value of useful heat |
| Model with demand-based shutdown | 90.5 % heat coverage and about 5'200 kWh less electricity per year than leaving paused servers on, using 230 W assumed idle power |
| House installation | About CHF 290'000, including eight servers with eight NVIDIA L4 cards each |
| Target prices | CHF 0.50 per L4-hour for the hypothetical anchor customer (60% of hours), CHF 0.55 for the remainder |
| Equivalent annual business result | About CHF 35'000 if all hours sell at the target prices. Break-even at 66 % of hours sold under the modelled sales mix |
| Winter customer scenario | About CHF 27'500 if an additional customer buys the remaining winter hours. 82 % of compute hours fall in the heating season |
| Proposed pilot | One house, two servers, one winter, CHF 81'500 |

The hardware, heat demand, operating states and commercial assumptions are modelled. The figures rely on enough suitable work and unconfirmed customer prices and volumes. See [plain-English results and assumptions](docs/ergebnisse/RESULTATE_EINFACH.md), [workloads and measurements](daten/JOBTYPEN.md) and [the case brief](docs/CASE.md).

The prototype runs actual text embeddings and molecular docking on a CPU. The two-laptop screens exchange checkpoint state. The optional ML forecast is trained on modelled heat demand. The project has yet to validate physical L4 electricity consumption, recovered water temperature or the protection of confidential customer workloads. The proposed service is for public, synthetic or appropriately anonymised and customer-approved tasks.

## Reproduce the results

```sh
python3 start/alles_neu_rechnen.py
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s prototyp/tests -v
```

Individual entry points include `python3 src/scheduler/jahr.py --server 8` for the reference house, `python3 src/kosten_dh.py` for the economics and `python3 src/dashboard3d_daten.py` for the 3D dashboard data. Install the corresponding dependencies from `requirements/` before running the optional ML, embedding or docking tests.

| Folder | Contents |
|---|---|
| `start/` | Launch scripts and result regeneration |
| `src/` | Scheduler, workloads, energy and business models |
| `dashboard/` | 3D view, annual analysis, guided demo and offline export |
| `prototyp/` | Two-laptop demos and product prototypes |
| `daten/` | Inputs, workload sources and reproducible results |
| `docs/`, `messungen/` | Case, technical and financial notes, and measurement reports |
| `tests/` | Regression tests |

Claude Code and OpenAI Codex were used for code, analysis and documentation.
