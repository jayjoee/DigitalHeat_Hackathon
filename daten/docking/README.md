# Molecular docking

AutoDock Vina estimates how well molecules fit into the binding pocket of Abl kinase (PDB 1IEP). The score is estimated in kcal/mol. More negative scores suggest stronger binding in the model. These predictions guide further evaluation and require experimental validation.

## Reproduce the reference run

The repository contains the prepared data and 28 distinct candidates. The CPU job saves a checkpoint after each completed candidate. The reference run on a four-core Linux machine took 384 seconds, with a median of 5.5 seconds per candidate. Nilotinib, imatinib and ponatinib received the most negative scores in that run. [Recorded scores](ergebnis.json)

Use Python 3.10–3.12 with a platform supported by the Vina Python package, or install the official Vina executable. On Linux, install the Python dependency inside your virtual environment:

```sh
python3 -m pip install -r requirements/docking.txt
```

On macOS, [download the executable matching your Mac from the official Vina release](https://github.com/ccsb-scripps/AutoDock-Vina/releases/tag/v1.2.5). Save it as `tools/vina` in the repository, then run:

```sh
chmod +x tools/vina
tools/vina --version
```

Run a standalone batch or launch the heat-controlled job:

```sh
python3 src/jobs/docking_job.py --arbeitsordner messungen/docking_test
python3 src/scheduler/live.py --tag 2025-03-07 --server 8 --sekunden 3 --job docking
```

The job records scores, timings and the checkpoint in `stand.json` in its working directory. Predicted poses are written to `posen/`. The prepared receptor comes from AutoDock Vina's `basic_docking` example. See [AutoDock Vina](https://github.com/ccsb-scripps/AutoDock-Vina) and [PDB 1IEP](https://www.rcsb.org/structure/1IEP).

## Two-laptop screening demo

Connect both laptops to the same Wi-Fi network and check out the same repository revision. Run the commands from the repository root:

1. Sports pool laptop: `python3 prototyp/schwimmbad.py`. Note the six-digit code.
2. House laptop: `python3 prototyp/haus.py`. Enter the code and select **Start screening**.
3. At 10:00 model time, the pool takes over the checkpoint. At 16:00 the house takes it back as the tank has dropped to 32 kWh.

The checkpoint exchange runs live over TLS. This default flow uses the recorded Vina scores and a simulated heat timeline. To open both screens on one machine, run `python3 prototyp/docking_demo.py demo --open`. The lower-level docking demo also accepts `--live` when the Vina Python package is available.
