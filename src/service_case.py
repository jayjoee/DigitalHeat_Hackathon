"""Read-only instrumentation of the existing annual server scheduler.

Slots are stable simulated physical server IDs in the scheduler's existing order.
This does not introduce a new dispatch rule or rebalance wear across servers.
"""
from collections import defaultdict
from datetime import date, timedelta
import math

from src.scheduler.jahr import profil_laden
from src.scheduler.serverbetrieb import HausMitServerbetrieb, Leistungsprofil


class TracedHouse(HausMitServerbetrieb):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_days = {}

    def betrieb_verbuchen(self, h, decision, operation):
        previous = self.eingeschaltet
        capacities = operation.lage.server_kapazitaeten_kwh
        occupied = decision.server_belegt_kwh
        if len(occupied) != len(capacities):
            raise AssertionError('Serverbelegung des Schedulers fehlt.')
        result = super().betrieb_verbuchen(h, decision, operation)
        stamp = self.profil[h]['zeit'][:10]
        for i in range(self.n):
            key = (i, stamp)
            row = self.service_days.setdefault(key, dict(server_id=f'DH-H01-S{i+1:02}',
                source_date=stamp, powered_hours=0., compute_hours=0., standby_hours=0.,
                starts=0, it_kwh=0.))
            on = i < len(capacities)
            start = on and i >= previous
            boot = self.leistung.start_minuten/60 if start else 0.
            work = occupied[i] if on else 0.
            active = work / operation.lage.server_kw
            idle = max(0., 1.-boot-active) if on else 0.
            row['powered_hours'] += int(on)
            row['standby_hours'] += int(not on)
            row['compute_hours'] += active
            row['starts'] += int(start)
            row['it_kwh'] += work + idle*self.leistung.leerlauf_watt/1000 + boot*operation.lage.server_kw + (0. if on else self.leistung.standby_watt/1000)
        return result


def case_trace():
    profile = profil_laden()
    house = TracedHouse(8, 'spot', profile, Leistungsprofil(230), abschalten=True)
    for h in range(len(profile)):
        house.schritt(h)
    rows = list(house.service_days.values())
    for field, target in [('it_kwh',house.z['strom']),('starts',house.z['serverstarts']),
                          ('compute_hours',house.z['rechenstrom']),('standby_hours',house.z['server_h_aus'])]:
        if not math.isclose(sum(r[field] for r in rows), target, abs_tol=1e-6):
            raise AssertionError(f'Case-Abgleich verletzt: {field}')
    return dict(source='Basel 2025, bestehender Abschalt-Scheduler, genug flexible Aufträge',
                status='SIMULIERTE BETRIEBSZEITEN, KEINE HARDWAREMESSUNG',
                days=365, servers=8, rows=rows,
                totals={f:sum(r[f] for r in rows) for f in ('powered_hours','compute_hours','standby_hours','starts','it_kwh')},
                assumptions=dict(active_kw=1.,idle_kw=.23,standby_kw=.01,start_minutes=5.,
                                 allocation='Feste Serverpositionen des vorhandenen Schedulers; keine Verschleissrotation'))


def calendar_operations(trace, as_of, days):
    """Reuse the reference year's month/day as a scenario, never a weather forecast."""
    lookup = {(r['server_id'],r['source_date'][5:]):r for r in trace['rows']}
    ids = sorted({r['server_id'] for r in trace['rows']})
    start = date.fromisoformat(as_of); output = {}
    for sid in ids:
        output[sid] = []
        for offset in range(days):
            stamp = start+timedelta(days=offset); key = stamp.isoformat()[5:]
            if key == '02-29':key = '02-28'
            row = dict(lookup[sid,key]);row['date']=stamp.isoformat()
            output[sid].append(row)
    return output


def case_fleet(trace, as_of='2026-11-21'):
    """Initial ages/telemetry remain explicitly synthetic; counters reuse two case years."""
    grouped=defaultdict(list)
    for row in trace['rows']:grouped[row['server_id']].append(row)
    fleet=[]
    for i,(sid,rows) in enumerate(sorted(grouped.items())):
        previous=(date.fromisoformat(as_of)-timedelta(days=1)).isoformat()[5:]
        if previous=='02-29':previous='02-28'
        last=next(r for r in rows if r['source_date'][5:]==previous)
        on=last['powered_hours'];load=last['compute_hours']/on if on else 0.
        inlet=34.;temp=inlet+19+17*load if on else inlet+2
        fleet.append(dict(server_id=sid,date=as_of,site_id='DH-H01',server_age_days=730.,
                          operating_hours=2*sum(r['powered_hours'] for r in rows),
                          compute_hours=2*sum(r['compute_hours'] for r in rows),
                          starts_total=2*sum(r['starts'] for r in rows),starts_24h=last['starts'],
                          power_on_fraction=on/24,days_since_service=30+i*20,
                          load_fraction=load,gpu_temp_c=temp,coolant_inlet_c=inlet,
                          flow_lpm=4.,pump_current_a=1.1,ecc_errors_24h=0,ssd_wear_percent=10.))
    return fleet


def site_plan(as_of, horizon_days, server_count, interval_days=180, days_since_service=0,
              cost_chf=600., downtime_h=2., site_id='DH-H01'):
    """A fixed cooling calendar. A server repair cannot reset it."""
    if any(type(v) is not int for v in (horizon_days,server_count,interval_days,days_since_service)):
        raise ValueError('Standortkalender braucht ganze Tages-/Serverzahlen.')
    if not 1<=horizon_days<=1095 or server_count<1 or interval_days<1 or days_since_service<0:
        raise ValueError('Ungültiger Standortkalender.')
    if not math.isfinite(cost_chf) or cost_chf<0 or not math.isfinite(downtime_h) or not 0<=downtime_h<=24:
        raise ValueError('Ungültige Standortkosten oder Ausfallzeit.')
    first=max(0,interval_days-days_since_service)
    offsets=list(range(first,horizon_days,interval_days))
    dates=[(date.fromisoformat(as_of)+timedelta(days=i)).isoformat() for i in offsets]
    return dict(site_id=site_id,interval_days=interval_days,scheduled_dates=dates,
                cost_per_visit_chf=cost_chf,downtime_per_visit_h=downtime_h,
                scheduled_cooling_visits=len(dates),cooling_budget_chf=len(dates)*cost_chf,
                allocated_budget_per_server_chf=len(dates)*cost_chf/server_count,
                site_downtime_hours=len(dates)*downtime_h,
                server_hours_unavailable=len(dates)*downtime_h*server_count,
                assumption=f'{interval_days} Tage sind ein Betreiber-Szenario, keine ausgewählte Herstellervorgabe. CoolIT nennt typischerweise sechs Monate. {cost_chf:g} CHF und {downtime_h:g} h pro Besuch sind Testwerte.',
                resets_only='Gemeinsamer Kühlungskalender; unabhängig von Servereingriffen',
                source='https://www.coolitsystems.com/products-services/global-professional-services/')
