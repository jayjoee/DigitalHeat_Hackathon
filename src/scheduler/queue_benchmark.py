"""Matched small fleet simulation, not a measurement or replacement of case balance."""
import hashlib
import json
import random
import time
from dataclasses import asdict

from src.scheduler.resource_queue import Customer,Node,Requirements,ResourceQueue


def workload(seed=2026):
    rng=random.Random(seed);jobs=[]
    for hour in range(6):
        for i in range(8):
            arrival=hour*3600+rng.randrange(0,31)*10
            duration=rng.randrange(18,61)*10
            jobs.append(dict(id=f'{hour}-{i}',customer=('standard','priority','batch')[i%3],
                             arrival=arrival,runtime_seconds=duration,deadline=arrival+3600,
                             gpu_count=1 if i%4 else 2,ram_gb=16))
    return sorted(jobs,key=lambda j:(j['arrival'],j['id']))


def run(strategy,jobs,horizon=8*3600,step=10):
    now=[0.]
    nodes=[Node(f'house-{i}',ram_gb=192,cpu_cores=16,gpu_memory_gb=(24,)*8,gpu_model='L4',slots=8,
                executor='plan_only',region='CH',approved_customers=('standard','priority','batch'),heat_need_kw=.8) for i in range(3)]
    customers=[Customer('standard',priority=2,max_running=4),Customer('priority',priority=0,max_running=4),Customer('batch',priority=3,max_running=4)]
    optimized=strategy!='fifo_spread';sleep=strategy=='priority_pack_sleep'
    q=ResourceQueue(nodes,customers,clock=lambda:now[0],placement='pack' if optimized else 'spread',
                    queue_order='priority' if optimized else 'fifo',backfill=optimized)
    next_job=0;booting={};started={};completed={};energy=0.;starts=0;dispatch_seconds=0.;active_node_seconds=0.
    demand_reservations=0
    for tick in range(0,horizon,step):
        now[0]=float(tick)
        for nid,ready in list(booting.items()):
            if tick>=ready:q.nodes[nid].power_state='on';q.idle_since[nid]=float(tick);del booting[nid]
        for j in list(q.jobs.values()):
            if j.state=='running' and tick>=j.finish_by:
                q.finish(j.id);completed[j.id]=tick
        while next_job<len(jobs) and jobs[next_job]['arrival']<=tick:
            j=jobs[next_job]
            q.submit(j['id'],j['customer'],Requirements(gpu_count=j['gpu_count'],gpu_memory_gb=24,ram_gb=j['ram_gb'],cpu_cores=1,region='CH'),
                     runtime_seconds=j['runtime_seconds'],deadline_at=j['deadline'])
            next_job+=1
        before=time.perf_counter();assigned=q.dispatch();dispatch_seconds+=time.perf_counter()-before
        for j in assigned:started[j.id]=tick
        if sleep:
            # Simulation-only controller: acknowledge modeled wake after five minutes.
            for advice in q.power_advice():
                n=q.nodes[advice['node']]
                if advice['action']=='sleep_recommended':n.power_state='sleep'
            # Wake one compatible node at a time; do not boot the entire fleet for a small queue.
            if not booting:
                advice=next((a for a in q.power_advice() if a['action']=='wake_recommended'),None)
                if advice:
                    n=q.nodes[advice['node']];n.power_state='starting';booting[n.id]=tick+300;starts+=1
        for n in nodes:
            held=q._held(n.id)
            if n.power_state=='sleep':kw=n.standby_kw
            elif n.power_state=='starting':kw=n.active_kw
            else:
                load=sum(max(j.requirements.gpu_count/8,j.requirements.cpu_cores/16) for j in held)
                kw=n.idle_kw+(n.active_kw-n.idle_kw)*min(1,load)
                if held:active_node_seconds+=step
            energy+=kw*step/3600
    # Inclusive final completion observation; no extra energy beyond the exclusive horizon.
    for j in q.jobs.values():
        if j.state=='running' and j.finish_by<=horizon:completed[j.id]=horizon
    waits=[started[j['id']]-j['arrival'] for j in jobs if j['id'] in started]
    finished_work=sum(j['gpu_count']*j['runtime_seconds']/3600 for j in jobs if j['id'] in completed)
    return dict(strategy=strategy,submitted=len(jobs),completed=len(completed),completed_ids=sorted(completed),
                missed=sum(j['id'] not in completed or completed[j['id']]>j['deadline'] for j in jobs if j['deadline']<=horizon),
                pending=sum(j['id'] not in completed and j['deadline']>horizon for j in jobs),
                completed_reference_gpu_hours=finished_work,it_kwh=energy,electricity_chf=energy*.3325,
                simulated_starts=starts,mean_wait_seconds=sum(waits)/len(waits) if waits else 0,
                max_wait_seconds=max(waits,default=0),active_node_hours=active_node_seconds/3600,
                scheduler_cpu_seconds=dispatch_seconds,
                limits='Serverstrommodell, keine echte GPU-Ausführung; keine Pumpen-/Backup-/Wärmebilanz oder Servicekosten.')


def compare():
    jobs=workload()
    results=[run(s,jobs) for s in ('fifo_spread','priority_pack','priority_pack_sleep')]
    return dict(schema=1,status='SYNTHETISCHER FUNKTIONSVERGLEICH – KEIN GEMESSENER EFFIZIENZNACHWEIS',
                jobs=jobs,jobs_sha256=hashlib.sha256(json.dumps(jobs,sort_keys=True).encode()).hexdigest(),
                period_hours=8,scenarios=results,same_completed_jobs=all(r['completed_ids']==results[0]['completed_ids'] for r in results),
                assumptions={'workload':'48 frei erzeugte Metadatenaufträge, keine Pharma-Nachfrage',
                             'nodes':'3 simulierte Hosts mit je 8 L4, 24 GB je GPU, 192 GB Host-RAM, 16 CPU-Kernen; Ressourcenwerte sind Teamannahmen',
                             'energy':'1 kW aktiv, 230 W Leerlauf, 10 W Standby, 5 Minuten Start aus bestehendem Serverbetriebsmodell; nicht an L4 gemessen',
                             'power_curve':'Leerlauf + (Aktiv−Leerlauf) × Ressourcenbelegung; lineare Testannahme, keine gemessene Kennlinie',
                             'sleep':'Nach 300 Sekunden ohne passende Arbeit; eigener Testwert. Aufwachen wird ausschliesslich im Simulator bestätigt.',
                             'runtime':'Bekannte Laufzeiten und perfekte Einhaltung im Simulator; reale Überschreitungen können Backfill-Zusagen verschieben',
                             'price':'0,3325 CHF/kWh als Projektwert; nur Stromkosten, keine Unternehmensrendite',
                             'exclusions':'Steuerungsenergie, Datenübertragung, Speicherung, reale Wärmeabnahme, Pumpen, Ersatzheizung und Wartungsausfälle fehlen.'})
