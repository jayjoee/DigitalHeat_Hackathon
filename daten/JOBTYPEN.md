# Workload definitions

Run `python3 src/jobtypen.py` to generate `daten/jobtypen.json`, which the scheduler reads.

| | A · Molecular docking | B · Microscopy image analysis |
|---|---|---|
| Work | Virtual screening campaign, scheduled in energy batches | Urgent analysis of one million microscopy images per batch |
| Share of server-hours, 8-server case model | 95% | 5% |
| Energy per batch | 0.941 kWh, **proxy** | 0.121 kWh, **proxy** |
| Runtime on 1 kW reference server | 56.5 minutes | 7.3 minutes |
| Interruptible | Pause anytime, checkpoint after every molecule | Switch between batches |
| Deadline | None with plentiful work, 24 hours in the limited-demand scenario | 2 hours |
| Evidence for the energy | Our measurement of a different CPU job: embedding 10 million texts with BGE-small-en-v1.5 at 10.6 million texts/kWh, from 85.4 texts/s at 28.9 W on an M1 Pro (macOS powermetrics) | MLPerf Inference 5.0, result 5.0-0023: general object detection with RetinaNet on OpenImages, 11'106 images/s at 4'849 W (Fujitsu, eight H100 NVL) |
| Local execution | Real AutoDock Vina process under scheduler control | Benchmark-based job in the annual model |

**What the proxies mean.** Docking energy and microscopy-specific energy have not been measured. The scheduler works in kWh and server-hours, so the job name does not enter the calculation. The 93% case coverage holds across the Type A batch sizes we tested. The power-down model is sensitive to them: batches of 0.785 kWh give 88.1% coverage and about CHF 31'200 a year, batches of 1 kWh give about 92.1% and CHF 37'500, compared with 90.5% and CHF 35'000 at 0.941 kWh. The [customer analysis](../docs/kunden/PHARMA_SICHT.md) proposes a 12-hour deadline for microscopy. The model keeps the stricter 2 hours.

The conversion assumes the same amount of work per kWh on the 1 kW reference server as in the measurement or benchmark. Under this proportional scaling, 1 kW generates 0.8 kW of useful heat. The calculation does not establish production L4 throughput. MLPerf was measured in the benchmark's offline configuration, and field performance could be lower.

The plentiful-work scenario assumes unlimited flexible Type A jobs and limits Type B to 40 jobs per day. The constrained scenario draws arrivals from the Alibaba trace. Its workload calibration uses approximately 3.6 jobs per server per day and a median runtime of 11 minutes.

## Molecular docking

AutoDock Vina tests each candidate against a model of the Abl kinase binding pocket. The reference run screened 28 distinct molecules in 384 seconds on a four-core Linux test machine. The median runtime was 5.5 seconds per molecule. It can pause mid-job and saves a checkpoint after every molecule. The screening campaign is Type A. A separate sensitivity tests deadlines of weeks to months. Energy per molecule has not been measured. Use the [docking guide](docking/README.md) to run the job.
