"""Measured-work-ready energy model using the ORIGINAL scheduler through a unit adapter.

One work unit = one standard reference-server hour. It is not an electrical kWh.
All scenarios receive exactly the same finite arrivals, deadlines and work quantities.
"""
from dataclasses import dataclass
import hashlib
import json
import math
from collections import defaultdict
from src.scheduler.kern import Lage, entscheide
from src.scheduler.jahr import ankuenfte
from src.scheduler import annahmen as A
from src.wirtschaft import variable_bilanz

@dataclass
class WorkJob:
    id: int
    typ: str
    ankunft_h: int
    frist_h: float
    remaining_work: float
    unterbrechbar: bool
    total_work: float
    gelaufen_kwh: float = 0.0  # legacy kernel adapter: reference work, never used as energy
    busy_hours: float = 0.0

    @property
    def rest_kwh(self):
        """Compatibility with the shared scheduler's historical field name."""
        return self.remaining_work


def make_jobs(config, start, end):
    arrivals,_=ankuenfte(config.servers,'alibaba',config.seed)
    return [WorkJob(i,t,h,h+A.wert(f'job_{t.lower()}_frist_h'),
                    A.wert(f'job_{t.lower()}_kwh'),t=='A',A.wert(f'job_{t.lower()}_kwh'))
            for i,(h,t) in enumerate((h,t) for h in range(start,end) for t in arrivals.get(h,[]))]


def schedule(h, demand, storage, target, config, queue, speed, power, slots):
    # Convert kernel units: power -> reference-work/h, eta -> recovered-heat/reference-work.
    # Its decision.strom_kwh is therefore WORK, converted back to real energy below.
    heat_per_work=power*config.recovery/speed
    return entscheide(Lage(h,demand,storage,max(storage,target),slots,speed,heat_per_work),queue,'rechnen')


def simulate(profile, config, jobs, start, end, variant, forecasts=None, margin=0):
    if variant not in ('standard','efficient','ml'):raise ValueError('Unbekanntes Szenario.')
    efficient=variant!='standard'
    speed=config.economy_speed if efficient else 1.0
    power=config.economy_kw if efficient else config.active_kw
    queue=[]; by_hour=defaultdict(list)
    for j in jobs:by_hour[j.ankunft_h].append(WorkJob(**vars(j)))
    failed_remaining=0.0
    storage=0.0; on=config.servers if not efficient else 0
    rows=[]; completed=failed=0; billed_hours=finished_work=processed_work=0.0
    for h in range(start,end):
        queue.extend(by_hour[h])
        opening=storage
        loss=storage*config.storage_loss_per_hour
        storage-=loss
        p=profile[h]; demand=p['heizung']+p['ww']
        target=config.storage_kwh
        if efficient:
            prediction=forecasts[h]
            # Same control rule in both efficient arms. Only the heat predictor differs.
            target=min(config.storage_kwh,sum(max(0,v+margin) for v in prediction))
        e=schedule(h,demand,storage,target,config,queue,speed,power,config.servers)
        work=sum(amount for _,amount in e.laeufe)
        wanted=min(config.servers,math.ceil(work/speed-1e-10)) if efficient else config.servers
        starts=max(0,wanted-on)
        boot_hours=starts*config.startup_minutes/60
        if efficient and boot_hours:
            e=schedule(h,demand,storage,target,config,queue,speed,power,max(0,wanted-boot_hours))
            work=sum(amount for _,amount in e.laeufe)
        busy=work/speed
        idle=max(0,wanted-busy-boot_hours)
        active_energy=busy*power
        idle_energy=idle*config.idle_kw
        off_energy=(config.servers-wanted)*config.off_kw
        startup_energy=boot_hours*config.startup_kw
        it=active_energy+idle_energy+off_energy+startup_energy
        heat=(it-off_energy)*config.recovery
        direct=min(heat,demand)
        discharged=min(storage,demand-direct)
        storage-=discharged
        pump=config.pump_kw if heat>1e-12 or discharged>1e-12 else 0.0
        backup_heat=max(0,demand-direct-discharged)
        charged=min(max(0,heat-direct),config.storage_kwh-storage)
        storage+=charged
        dumped=max(0,heat-direct-charged)
        for j,amount in e.laeufe:
            j.remaining_work=max(0,j.remaining_work-amount)
            j.gelaufen_kwh+=amount
            j.busy_hours+=amount/speed
            processed_work+=amount
            if j.remaining_work<=1e-9:
                completed+=1; billed_hours+=j.busy_hours; finished_work+=j.total_work
        queue=[j for j in queue if j.remaining_work>1e-9]
        late=[j for j in queue if h+1>=j.frist_h]
        failed+=len(late)
        failed_remaining+=sum(j.remaining_work for j in late)
        queue=[j for j in queue if h+1<j.frist_h]
        backup_electricity=backup_heat/config.backup_cop
        # Independent conservation of energy, storage and physical server capacity.
        if abs(opening+heat-(direct+discharged+loss+dumped+storage))>1e-7:
            raise AssertionError('Wärmebilanz verletzt')
        if busy+idle+boot_hours>wanted+1e-8 or not -1e-8<=storage<=config.storage_kwh+1e-8:
            raise AssertionError('Kapazität oder Speicher verletzt')
        rows.append(dict(time=p['zeit'],hour=h,demand_kwh=demand,it_kwh=it,pump_kwh=pump,
                         ml_kwh=0.0,backup_kwh=backup_electricity,backup_heat_kwh=backup_heat,
                         total_kwh=it+pump+backup_electricity,useful_heat_kwh=direct+discharged,
                         storage_kwh=storage,storage_loss_kwh=loss,dumped_heat_kwh=dumped,
                         active_kwh=active_energy,idle_kwh=idle_energy,off_kwh=off_energy,
                         startup_kwh=startup_energy,on_servers=wanted,starts=starts,
                         active_server_hours=busy,work=work,queue=len(queue),reserve_target_kwh=target,
                         next_hour_heat_prediction=forecasts[h][0] if efficient and forecasts[h] else None))
        on=wanted
    remaining=sum(j.remaining_work for j in queue)
    if abs(sum(j.total_work for j in jobs)-processed_work-remaining-failed_remaining)>1e-6:
        raise AssertionError('Arbeitsbilanz verletzt')
    result=dict(pending_work=remaining,failed_remaining_work=failed_remaining,variant=variant,completed_jobs=completed,missed_jobs=failed,pending_jobs=len(queue),
                submitted_jobs=len(jobs),submitted_work=sum(j.total_work for j in jobs),
                completed_work=finished_work,processed_work=processed_work,
                billed_server_hours=billed_hours,rows=rows)
    return summarise(result,config)


def summarise(result,config):
    rows=result['rows']
    keys=['it_kwh','pump_kwh','ml_kwh','backup_kwh','backup_heat_kwh','total_kwh','useful_heat_kwh',
          'storage_loss_kwh','dumped_heat_kwh','active_kwh','idle_kwh','off_kwh','startup_kwh','demand_kwh','active_server_hours','starts']
    result['energy']={k:sum(row[k] for row in rows) for k in keys}
    energy=result['energy']
    result['heat_coverage']=energy['useful_heat_kwh']/energy['demand_kwh'] if energy['demand_kwh'] else 0
    result['missed_fraction']=result['missed_jobs']/result['submitted_jobs'] if result['submitted_jobs'] else 0
    result['kwh_per_completed_work']=energy['total_kwh']/result['completed_work'] if result['completed_work'] else None
    result['system_electricity_chf']=energy['total_kwh']*config.electricity_chf_kwh
    # Active, completed jobs only. Idle energy never creates saleable GPU hours.
    result['business']=variable_bilanz(energy['it_kwh']+energy['pump_kwh']+energy['ml_kwh'],
                          result['completed_work']*A.wert('karten_pro_server'),
                          config.electricity_chf_kwh)
    return result


def jobs_digest(jobs):
    return hashlib.sha256(json.dumps([vars(j) for j in jobs],sort_keys=True).encode()).hexdigest()
