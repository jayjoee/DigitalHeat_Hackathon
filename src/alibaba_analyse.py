"""Auswertung des Alibaba PAI GPU Cluster Trace 2020 für den DigitalHeat-Case.

Fragen:
- Wie lange laufen Jobs, wie viel GPU fordern sie an, wie viele kommen pro Tag?
- Welcher Anteil der GPU-Stunden liegt in kurzen Jobs (passt in Wärmefenster)?
- Wie verteilen sich die Ankünfte über Tag und Woche?
- Wie lange warten Jobs heute schon (wie viel Verzögerung tolerieren Nutzer)?

Aufruf: python3 src/alibaba_analyse.py  -> daten/alibaba_auswertung.json + Ausgabe
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ROH = ROOT / "daten" / "roh" / "alibaba"
AUS = ROOT / "daten" / "alibaba_auswertung.json"

JOB = ["job_name", "inst_id", "user", "status", "start_time", "end_time"]
TASK = ["job_name", "task_name", "inst_num", "status", "start_time", "end_time",
        "plan_cpu", "plan_mem", "plan_gpu", "gpu_type"]
TAG = ["inst_id", "user", "gpu_type_spec", "group", "workload"]
SPEC = ["machine", "gpu_type", "cap_cpu", "cap_mem", "cap_gpu"]

DAUER_KLASSEN = [0, 60, 600, 3600, 4 * 3600, 24 * 3600, np.inf]
DAUER_NAMEN = ["< 1 min", "1–10 min", "10–60 min", "1–4 h", "4–24 h", "> 24 h"]


def q(s, ps=(0.1, 0.25, 0.5, 0.75, 0.9, 0.99)):
    return {f"p{int(p * 100)}": round(float(s.quantile(p)), 1) for p in ps}


def main():
    jobs = pd.read_csv(ROH / "pai_job_table.csv", names=JOB)
    tasks = pd.read_csv(ROH / "pai_task_table.csv", names=TASK)
    tags = pd.read_csv(ROH / "pai_group_tag_table.csv", names=TAG)
    spec = pd.read_csv(ROH / "pai_machine_spec.csv", names=SPEC)
    r = {}

    # --- Cluster ---
    r["cluster"] = {
        "maschinen": int(len(spec)),
        "gpus": int(spec.cap_gpu.sum()),
        "gpus_nach_typ": spec.groupby("gpu_type").cap_gpu.sum().astype(int).to_dict(),
    }

    # --- Jobs ---
    r["jobs_status"] = jobs.status.value_counts().to_dict()
    t0, t1 = jobs.start_time.min(), jobs.start_time.max()
    tage = (t1 - t0) / 86400
    r["zeitraum_tage"] = round(tage, 1)
    r["jobs_pro_tag"] = round(len(jobs) / tage)

    # --- Tasks auf Job-Ebene: GPU-Bedarf, Laufzeit, Wartezeit ---
    tasks["laufzeit_s"] = tasks.end_time - tasks.start_time
    tasks["gpu"] = tasks.plan_gpu.fillna(0) / 100 * tasks.inst_num.fillna(1)
    tasks["gpu_h"] = tasks.gpu * tasks.laufzeit_s / 3600
    j = tasks.groupby("job_name").agg(
        task_start=("start_time", "min"), task_ende=("end_time", "max"),
        gpu=("gpu", "sum"), gpu_h=("gpu_h", "sum"), cpu=("plan_cpu", "sum"),
        gpu_typ=("gpu_type", "first"), tasks=("task_name", "count"),
    )
    j = j.join(jobs.set_index("job_name")[["inst_id", "status", "start_time", "user"]], how="inner")
    j["laufzeit_s"] = j.task_ende - j.task_start
    j["warten_s"] = (j.task_start - j.start_time).clip(lower=0)
    ok = j[(j.status == "Terminated") & j.laufzeit_s.notna() & (j.laufzeit_s >= 0)]
    gpu_ok = ok[ok.gpu > 0]
    r["erfolgreiche_jobs"] = int(len(ok))
    r["anteil_ohne_gpu"] = round(float((ok.gpu == 0).mean()), 3)

    r["laufzeit_min"] = {k: round(v / 60, 1) for k, v in q(gpu_ok.laufzeit_s).items()}
    r["wartezeit_min"] = {k: round(v / 60, 1) for k, v in q(gpu_ok.warten_s).items()}
    r["gpu_pro_job"] = q(gpu_ok.gpu)
    r["anteil_bruchteil_gpu"] = round(float((gpu_ok.gpu < 1).mean()), 3)

    klasse = pd.cut(gpu_ok.laufzeit_s, DAUER_KLASSEN, labels=DAUER_NAMEN, right=False)
    tab = pd.DataFrame({
        "jobs": gpu_ok.groupby(klasse, observed=False).size(),
        "gpu_h": gpu_ok.groupby(klasse, observed=False).gpu_h.sum(),
    })
    tab["anteil_jobs"] = (tab.jobs / tab.jobs.sum()).round(3)
    tab["anteil_gpu_h"] = (tab.gpu_h / tab.gpu_h.sum()).round(3)
    r["dauerklassen"] = tab[["jobs", "anteil_jobs", "anteil_gpu_h"]].to_dict(orient="index")

    # GPU-Stunden-Nachfrage pro Tag vs. Kapazität
    gpu_h_tag = gpu_ok.gpu_h.sum() / tage
    r["gpu_h_pro_tag"] = round(float(gpu_h_tag))
    r["nachfrage_auslastung"] = round(float(gpu_h_tag / (r["cluster"]["gpus"] * 24)), 3)

    # --- Ankünfte über Tag und Woche (UTC+8 laut README) ---
    zeit = pd.to_datetime(jobs.start_time, unit="s", utc=True).dt.tz_convert("Asia/Shanghai")
    pro_stunde = zeit.dt.hour.value_counts().sort_index()
    r["ankunft_stunde_utc8_anteil"] = (pro_stunde / pro_stunde.sum()).round(4).to_dict()
    pro_wtag = zeit.dt.dayofweek.value_counts().sort_index()
    r["ankunft_wochentag_anteil"] = (pro_wtag / pro_wtag.sum()).round(3).to_dict()
    tag_n = zeit.dt.floor("D").value_counts()
    r["jobs_pro_tag_verteilung"] = q(tag_n, (0.1, 0.5, 0.9))

    # --- Workload-Tags ---
    w = ok.merge(tags[["inst_id", "workload"]], on="inst_id", how="left")
    w = w[w.workload.notna() & (w.gpu > 0)]
    r["workloads"] = (
        w.groupby("workload").agg(
            jobs=("laufzeit_s", "size"),
            laufzeit_median_min=("laufzeit_s", lambda s: round(float(s.median()) / 60, 1)),
            laufzeit_p90_min=("laufzeit_s", lambda s: round(float(s.quantile(0.9)) / 60, 1)),
            gpu_median=("gpu", "median"),
            gpu_h_summe=("gpu_h", "sum"),
        ).sort_values("jobs", ascending=False).round(2).to_dict(orient="index")
    )
    r["anteil_jobs_mit_workload_tag"] = round(len(w) / len(gpu_ok), 3)

    # Wiederholte Jobs (gleiche Gruppe) = planbare, wiederkehrende Last
    g = tags.group.value_counts()
    r["anteil_instanzen_in_wiederholten_gruppen"] = round(float(g[g > 1].sum() / g.sum()), 3)

    # --- Tatsächliche GPU-Nutzung (Sensor, Mittel über die Lebensdauer der Instanz) ---
    sensor_pfad = ROH / "pai_sensor_table.csv"
    if sensor_pfad.exists():
        s = pd.read_csv(sensor_pfad, header=None, usecols=[0, 1, 6, 7],
                        names=["job_name", "task_name", "cpu_usage", "gpu_wrk_util"])
        t = tasks[["job_name", "task_name", "plan_gpu", "inst_num", "laufzeit_s"]].copy()
        t["plan_gpu_inst"] = t.plan_gpu  # plan_gpu gilt pro Instanz
        s = s.merge(t[["job_name", "task_name", "plan_gpu_inst", "laufzeit_s"]],
                    on=["job_name", "task_name"], how="inner")
        s = s[(s.plan_gpu_inst > 0) & s.gpu_wrk_util.notna() & (s.laufzeit_s > 0)]
        s["genutzt_anteil"] = (s.gpu_wrk_util / s.plan_gpu_inst).clip(upper=1.5)
        gew = s.plan_gpu_inst / 100 * s.laufzeit_s
        r["gpu_nutzung"] = {
            "instanzen": int(len(s)),
            "gpu_wrk_util_prozent": q(s.gpu_wrk_util),
            "genutzt_von_angefordert": q(s.genutzt_anteil, (0.25, 0.5, 0.75, 0.9)),
            "genutzt_von_angefordert_gpu_h_gewichtet": round(
                float(np.average(s.genutzt_anteil.clip(upper=1), weights=gew)), 3),
        }

    AUS.write_text(json.dumps(r, indent=2, ensure_ascii=False, default=float))
    print(json.dumps(r, indent=1, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
