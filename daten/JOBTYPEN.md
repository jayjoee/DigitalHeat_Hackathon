# Workload definitions

Run `python3 src/jobtypen.py` to generate `daten/jobtypen.json`, which the scheduler reads.

| | A · Archive embeddings | B · Image analysis batch |
|---|---|---|
| Work per job | Embed 10 million texts for a search index | Detect objects in one million images |
| Model | BGE-small-en-v1.5 | RetinaNet, OpenImages (37.3 mAP) |
| Estimated work per kWh | 10.6 million texts | 8.2 million images |
| Energy per job | 0.941 kWh | 0.121 kWh |
| Runtime on 1 kW reference server | 56.5 minutes | 7.3 minutes |
| Interruptible | Pause anytime or stop at a checkpoint every 128 texts | Switch between jobs at batch boundaries |
| Deadline | 24 hours, modelling overnight indexing | 2 hours, modelling same-morning results |
| Energy evidence | M1 Pro measurement: 85.4 texts/s at 28.9 W using macOS powermetrics | MLPerf Inference 5.0, result 5.0-0023: 11'106 images/s at 4'849 W on a Fujitsu system with eight H100 NVL accelerators |
| Local execution | Actual CPU workload under scheduler control | Benchmark-based job in annual model |

The conversion assumes the same amount of work per kWh on the 1 kW reference server as in the measurement or benchmark. Under this proportional scaling, 1 kW generates 0.8 kW of useful heat. The calculation does not establish production L4 throughput. MLPerf was measured in the benchmark's offline configuration, and field performance could be lower.

The plentiful-work scenario assumes unlimited flexible Type A jobs and limits Type B to 40 jobs per day. The constrained scenario draws arrivals from the Alibaba trace. Its workload calibration uses approximately 3.6 jobs per server per day and a median runtime of 11 minutes.

## Molecular docking

AutoDock Vina tests each candidate against a model of the Abl kinase binding pocket. The reference run screened 28 distinct molecules in 384 seconds on a four-core Linux test machine. The median runtime was 5.5 seconds per molecule. It can pause mid-job and saves a checkpoint after every molecule. The screening campaign represents Type A with a deadline of weeks to months in the separate deadline sensitivity. Energy per molecule has not been measured. Use the [docking guide](docking/README.md) to run the job.
