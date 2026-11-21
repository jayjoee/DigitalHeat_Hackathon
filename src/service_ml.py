"""ML daily service hazard + discrete renewal model for direct-to-chip servers.

Synthetic data and post-service recovery assumptions are a demo, not L4 failure rates.
No model pickle loading, remote control, or access to customer payloads.
"""
from dataclasses import dataclass, asdict
from datetime import date, timedelta
import csv
import hashlib
import json
import math

import numpy as np
from sklearn import __version__ as sklearn_version
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import brier_score_loss, log_loss, average_precision_score
from threadpoolctl import threadpool_limits

FEATURES = ['server_age_days', 'operating_hours', 'days_since_service',
            'load_fraction', 'gpu_temp_c', 'coolant_inlet_c', 'flow_lpm',
            'pump_current_a', 'ecc_errors_24h', 'ssd_wear_percent',
            'power_on_fraction', 'compute_hours', 'starts_24h', 'starts_total']
TARGET = 'unplanned_service_next_24h'
BOUNDS = [(0, 3650), (0, 87600), (0, 1095), (0, 1), (0, 115),
          (0, 85), (0, 100), (0, 50), (0, 1000000), (0, 100),
          (0, 1), (0, 87600), (0, 10000), (0, 10000000)]


@dataclass(frozen=True)
class ServiceConfig:
    horizon_days: int = 365
    intervals: tuple = (30, 60, 90, 180, 365)
    max_interval_days: int = 365  # user assumption; no manufacturer authorization
    planned_chf: float = 400.
    unplanned_chf: float = 900.
    planned_downtime_h: float = 2.
    unplanned_downtime_h: float = 12.
    lost_margin_chf_h: float = 0.

    def __post_init__(self):
        for name in ('horizon_days', 'max_interval_days'):
            v = getattr(self, name)
            if type(v) is not int or not 1 <= v <= 1095:
                raise ValueError(f'{name}: 1 bis 1095 ganze Tage erforderlich.')
        if not self.intervals or any(type(i) is not int or not 1 <= i <= self.max_interval_days for i in self.intervals):
            raise ValueError('Intervalle müssen zwischen 1 und der erlaubten Obergrenze liegen.')
        for name in ('planned_chf', 'unplanned_chf', 'planned_downtime_h', 'unplanned_downtime_h', 'lost_margin_chf_h'):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
                raise ValueError(f'Ungültiger Kosten-/Zeitparameter: {name}')
        if max(self.planned_downtime_h, self.unplanned_downtime_h) > 24:
            raise ValueError('Das Tagesmodell unterstützt höchstens 24 h Ausfall pro Eingriff.')


def validate_rows(rows, history=False):
    if not rows:
        raise ValueError('Leere Eingabedatei.')
    clean = []; seen = set()
    for row in rows:
        r = dict(row)
        if not isinstance(r.get('server_id'), str) or not r['server_id'].strip():
            raise ValueError('server_id fehlt.')
        try:
            when = date.fromisoformat(r['date'])
        except (KeyError, ValueError, TypeError):
            raise ValueError('date muss YYYY-MM-DD sein.')
        key = (r['server_id'], when) if history else r['server_id']
        if key in seen:
            raise ValueError('Doppelte Server-/Tageszeile oder mehrere aktuelle Zustände desselben Servers.')
        seen.add(key)
        for name, (low, high) in zip(FEATURES, BOUNDS):
            try:
                if isinstance(r[name], bool): raise ValueError()
                v = float(r[name])
            except (KeyError, ValueError, TypeError):
                raise ValueError(f'Fehlender oder ungültiger Messwert: {name}')
            if not math.isfinite(v) or not low <= v <= high:
                raise ValueError(f'Messwert ausserhalb Modellbereich: {name}')
            r[name] = v
        if r['days_since_service'] > r['server_age_days'] or r['operating_hours'] > r['server_age_days']*24+24:
            raise ValueError('Betriebsstunden/Servicealter passen nicht zum Gerätealter.')
        if r['compute_hours'] > r['operating_hours']+1e-8 or r['starts_24h'] > r['starts_total']:
            raise ValueError('Rechenstunden oder Starts widersprechen den Gesamtzählern.')
        if history:
            # A zero label is valid only when the complete following day was observed.
            for name in (TARGET, 'observed_24h'):
                if str(r.get(name)) not in ('0', '1'):
                    raise ValueError(f'{name} muss 0 oder 1 sein.')
                r[name] = int(r[name])
            if not r['observed_24h']:
                continue
        clean.append(r)
    if not clean:
        raise ValueError('Keine vollständig beobachteten Tagesfenster.')
    return clean


def read_csv(path, history=False):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return validate_rows(list(csv.DictReader(f)), history)


def demo_data(seed=2026, servers=120, days=540):
    """Independent synthetic daily observations with shared per-server environments."""
    rng = np.random.default_rng(seed); rows = []
    for sid in range(servers):
        inlet = rng.uniform(25, 46); load = rng.uniform(.25, .95)
        base_on=rng.uniform(.35,1.);starts_per_day=rng.uniform(.05,1.)
        age0 = int(rng.integers(365, 1500))
        operating=age0*24*base_on;computed=operating*load;total_starts=math.ceil(age0*starts_per_day)
        for day in range(days):
            age = age0+day; since = int(rng.integers(0, 366))
            on_fraction=float(np.clip(base_on+.35*math.cos(2*math.pi*day/365)+rng.normal(0,.1),0,1))
            if on_fraction<.1:on_fraction=0.
            observed_load=load if on_fraction else 0.
            loss = since/1000 + rng.uniform(0, .08)
            temp = inlet + 19 + 17*observed_load + 33*loss + rng.normal(0, 2) if on_fraction else inlet+2
            ecc = int(rng.poisson(.1 + max(0, temp-75)*.08))
            starts=int(rng.poisson(starts_per_day)) if on_fraction else 0
            r = dict(server_id=f'train-{sid:03}', date=(date(2023, 1, 1)+timedelta(days=day)).isoformat(),
                     server_age_days=age, operating_hours=operating,
                     compute_hours=computed,power_on_fraction=on_fraction,
                     starts_total=total_starts+starts,starts_24h=starts,
                     days_since_service=since, load_fraction=observed_load,
                     gpu_temp_c=temp, coolant_inlet_c=inlet,
                     flow_lpm=4*(1-loss), pump_current_a=1.1+loss,
                     ecc_errors_24h=ecc, ssd_wear_percent=min(99, age/70))
            # These rates are invented, explicit generator assumptions, NOT empirical failure evidence.
            hazard=.0005+.0000003*age+.000012*max(0,since-60)+.0005*max(0,temp-74)+.0005*ecc+.00015*starts
            r[TARGET]=int(rng.random()<1-math.exp(-hazard));r['observed_24h']=1
            rows.append(r)
            operating+=24*on_fraction;computed+=24*on_fraction*observed_load;total_starts+=starts
    fleet=[]
    for i, (since, inlet, load) in enumerate(((20,30,.45),(90,34,.65),(170,39,.8),(250,43,.9))):
        age=700+i*200; loss=since/1000
        fleet.append(dict(server_id=f'DH-{i+1:02}', date='2026-11-21', server_age_days=age,
                          operating_hours=age*24*.6,compute_hours=age*24*.6*load,
                          power_on_fraction=.6,starts_total=age*.25,starts_24h=1,
                          days_since_service=since,
                          load_fraction=load, gpu_temp_c=inlet+19+17*load+33*loss,
                          coolant_inlet_c=inlet, flow_lpm=4*(1-loss), pump_current_a=1.1+loss,
                          ecc_errors_24h=i//2, ssd_wear_percent=age/70))
    return validate_rows(rows, True), validate_rows(fleet)


class ServiceModel:
    def fit(self, rows, seed=2026):
        rows=validate_rows(rows, True)
        ids=sorted({r['server_id'] for r in rows})
        if len(ids)<12:
            raise ValueError('Mindestens 12 historische Server für getrennte Trainings-, Kalibrierungs- und Testgruppen erforderlich.')
        rng=np.random.default_rng(seed); rng.shuffle(ids)
        n=len(ids); parts=[set(ids[:int(.6*n)]),set(ids[int(.6*n):int(.8*n)]),set(ids[int(.8*n):])]
        sets=[[r for r in rows if r['server_id'] in group] for group in parts]
        arrays=[(np.array([[r[f] for f in FEATURES] for r in part]),np.array([r[TARGET] for r in part])) for part in sets]
        if any(sum(y)<5 or sum(1-y)<5 for _, y in arrays):
            raise ValueError('Jede Datengruppe braucht mindestens fünf Ereignisse und fünf ereignisfreie Tage.')
        base=HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=12,min_samples_leaf=150,
                                            l2_regularization=10,early_stopping=False,random_state=seed)
        with threadpool_limits(limits=1):
            base.fit(*arrays[0])
            self.model=CalibratedClassifierCV(FrozenEstimator(base),method='sigmoid')
            self.model.fit(*arrays[1])
            x,y=arrays[2]; p=self.model.predict_proba(x)[:,1]
        constant=np.full(len(y),float(np.mean(arrays[0][1])))
        self.bounds=np.array([[min(r[f] for r in sets[0]),max(r[f] for r in sets[0])] for f in FEATURES])
        self.info=dict(model='HistGradientBoostingClassifier + separate sigmoid calibration',
                       seed=seed, features=FEATURES, target=TARGET,
                       split='60/20/20 nach Server-ID; keine gemeinsame Hardware zwischen den Gruppen',
                       groups=[sorted(p) for p in parts], rows=[len(y) for _,y in arrays],
                       events=[int(sum(y)) for _,y in arrays],
                       test_brier=float(brier_score_loss(y,p)),baseline_brier=float(brier_score_loss(y,constant)),
                       test_log_loss=float(log_loss(y,p)),baseline_log_loss=float(log_loss(y,constant)),
                       test_average_precision=float(average_precision_score(y,p)),
                       test_event_rate=float(np.mean(y)))
        return self

    def probability(self, x):
        with threadpool_limits(limits=1):
            p=self.model.predict_proba(np.asarray(x))[:,1]
        if not np.all(np.isfinite(p)) or np.any((p<0)|(p>1)):
            raise ValueError('Ungültige ML-Wahrscheinlichkeiten.')
        return p


def trajectory(server, days, service_ages, operations=None):
    """Project counters from separate powered/compute/start exposure scenarios.

    No invented daily flow loss or pump recovery. Server service resets only the
    individual service-age feature, never shared fluid sensors or SSD/ECC history.
    """
    days, ages=np.broadcast_arrays(np.asarray(days,dtype=float),np.asarray(service_ages,dtype=float))
    values={f:np.full(days.shape,server[f],dtype=float) for f in FEATURES}
    values['server_age_days']+=days
    if operations is None:
        values['operating_hours']+=days*24*server['power_on_fraction']
        values['compute_hours']+=days*24*server['power_on_fraction']*server['load_fraction']
        values['starts_total']+=days*server['starts_24h']
    else:
        count=int(days.max())+1
        validate_operations(operations,count)
        index=days.astype(int)
        powered=np.array([r['powered_hours'] for r in operations[:count]],dtype=float)
        work=np.array([r['compute_hours'] for r in operations[:count]],dtype=float)
        starts=np.array([r['starts'] for r in operations[:count]],dtype=float)
        values['operating_hours']+=np.r_[0,np.cumsum(powered)[:-1]][index]
        values['compute_hours']+=np.r_[0,np.cumsum(work)[:-1]][index]
        values['starts_total']+=np.r_[0,np.cumsum(starts)[:-1]][index]
        # Model features describe the preceding day's exposure, as in historical inputs.
        values['power_on_fraction']=np.r_[server['power_on_fraction'],powered[:-1]/24][index]
        load=np.divide(work,powered,out=np.zeros_like(work),where=powered>0)
        values['load_fraction']=np.r_[server['load_fraction'],load[:-1]][index]
        values['starts_24h']=np.r_[server['starts_24h'],starts[:-1]][index]
        values['gpu_temp_c']=np.clip(server['gpu_temp_c']+17*(values['load_fraction']-server['load_fraction']),0,115)
        values['gpu_temp_c']=np.where(values['power_on_fraction']>0,values['gpu_temp_c'],server['coolant_inlet_c']+2)
    values['days_since_service']=ages
    return np.stack([values[f] for f in FEATURES],axis=-1)


def validate_operations(operations,count):
    if len(operations)<count:raise ValueError('Betriebsprofil kürzer als Planung/Risikozeitraum.')
    for r in operations[:count]:
        try:values=[float(r[k]) for k in ('powered_hours','compute_hours','starts')]
        except (KeyError,ValueError,TypeError):raise ValueError('Betriebsstunden, Rechenstunden oder Starts fehlen.')
        on,work,starts=values
        if not all(math.isfinite(v) for v in values) or not 0<=work<=on+1e-8 or not 0<=on<=24 or starts<0:
            raise ValueError('Ungültige tägliche Betriebsexposition.')


def renewal(hazards, initial_age, interval, config):
    """Exact expectation in the daily model; at most one service per server/day.

    hazards[day, age_since_service]. An unplanned repair substitutes the pending
    routine service and restarts the service clock. No duplicate yearly count.
    """
    horizon=config.horizon_days; maxage=max(initial_age,interval)+1
    if hazards.shape[0]!=horizon or hazards.shape[1]<maxage:
        raise ValueError('Unvollständige Risikomatrix.')
    if not np.all(np.isfinite(hazards)) or np.any((hazards<0)|(hazards>1)):
        raise ValueError('Ungültiges Risiko.')
    state=np.zeros(maxage);state[initial_age]=1.
    planned=unplanned=0.
    for day in range(horizon):
        due=state[interval:].sum(); planned+=due
        working=state.copy();working[interval:]=0
        fail=working*hazards[day,:maxage];unplanned+=fail.sum()
        nxt=np.zeros_like(state);nxt[1:]=(working-fail)[:-1]
        nxt[1]+=due+fail.sum()  # service today -> one day since service tomorrow
        if abs(nxt.sum()-1)>1e-9:raise AssertionError('Wahrscheinlichkeitsmasse verloren.')
        state=nxt
    downtime=planned*config.planned_downtime_h+unplanned*config.unplanned_downtime_h
    return dict(interval_days=interval,expected_planned=float(planned),expected_unplanned=float(unplanned),
                expected_total=float(planned+unplanned),expected_downtime_h=float(downtime),
                expected_service_cost_chf=float(planned*config.planned_chf+unplanned*config.unplanned_chf),
                expected_total_cost_chf=float(planned*config.planned_chf+unplanned*config.unplanned_chf+downtime*config.lost_margin_chf_h))


def plan_server(model, server, config, operations=None):
    server=validate_rows([server])[0]
    initial=int(server['days_since_service'])
    if initial!=server['days_since_service']:
        raise ValueError('days_since_service muss für die Tagesplanung ganzzahlig sein.')
    maxage=max(initial,max(config.intervals))+1
    days=np.arange(config.horizon_days)[:,None]; ages=np.arange(maxage)[None,:]
    x=trajectory(server,days,ages,operations)
    hazards=model.probability(x.reshape(-1,len(FEATURES))).reshape(config.horizon_days,maxage)
    options=[renewal(hazards,initial,i,config) for i in sorted(set(config.intervals))]
    # Do not prefer extra routine maintenance when costs are numerically identical.
    best=min(options,key=lambda r:(round(r['expected_total_cost_chf'],8),-r['interval_days']))
    baseline=next((r for r in options if r['interval_days']==365),None)
    riskx=trajectory(server,np.arange(30),initial+np.arange(30),operations)
    risk30=float(-np.expm1(np.log1p(-np.clip(model.probability(riskx),0,1-1e-15)).sum()))
    raw=np.array([server[f] for f in FEATURES]); outside=[f for f,v,b in zip(FEATURES,raw,model.bounds) if not b[0]<=v<=b[1]]
    future_outside=[f for i,f in enumerate(FEATURES)
                    if x[...,i].min()<model.bounds[i,0] or x[...,i].max()>model.bounds[i,1]]
    urgent=server['flow_lpm']<=0 or server['gpu_temp_c']>=90  # scenario flag only, not manufacturer limit
    return dict(server_id=server['server_id'],as_of=server['date'],current=server,
                risk_next_30_days_without_service=risk30,
                recommended_interval_days=best['interval_days'],
                next_routine_in_days=max(0,best['interval_days']-initial),
                next_routine_date=(date.fromisoformat(server['date'])+timedelta(days=max(0,best['interval_days']-initial))).isoformat(),
                scenario_inspection_flag=urgent,outside_training_range=outside,
                future_scenario_outside_training_range=future_outside,
                operation_profile='Case-Abschaltbetrieb, saisonal' if operations is not None else 'Konstantes Expositionsszenario',
                forecast_exposure={k:sum(float(r[k]) for r in operations[:config.horizon_days]) for k in ('powered_hours','compute_hours','starts')} if operations is not None else None,
                selected=best,annual_reference=baseline,candidates=options)


def calculate(history,fleet,config=None,synthetic=False,seed=2026,operations=None):
    config=config or ServiceConfig();history=validate_rows(history,True);fleet=validate_rows(fleet)
    if max(date.fromisoformat(r['date'])+timedelta(days=1) for r in history)>min(date.fromisoformat(r['date']) for r in fleet):
        raise ValueError('Historische Ergebnisfenster müssen vor dem aktuellen Flottenzustand enden.')
    model=ServiceModel().fit(history,seed)
    if operations is not None:
        if set(operations)!={s['server_id'] for s in fleet}:raise ValueError('Betriebsprofile müssen genau zur Flotte passen.')
        for s in fleet:
            validate_operations(operations[s['server_id']],max(30,config.horizon_days))
            if any(r.get('date')!=(date.fromisoformat(s['date'])+timedelta(days=i)).isoformat() for i,r in enumerate(operations[s['server_id']])):
                raise ValueError('Betriebsprofil und Serverdatum sind nicht zeitlich ausgerichtet.')
    servers=[plan_server(model,s,config,None if operations is None else operations[s['server_id']]) for s in fleet]
    input_hash=hashlib.sha256(json.dumps({'history':history,'fleet':fleet,'operations':operations},sort_keys=True).encode()).hexdigest()
    return dict(schema=2,status='SYNTHETISCHES SZENARIO – KEINE REALE WARTUNGSPROGNOSE' if synthetic else 'IMPORTIERTE DATEN – UNVALIDIERTE PLANUNG, ANGENOMMENE SERVICEWIRKUNG',
                data_origin='generated_synthetic' if synthetic else 'user_supplied_unverified',
                runtime={'numpy':np.__version__,'scikit_learn':sklearn_version},
                synthetic=synthetic,input_sha256=input_hash,config=asdict(config),model=model.info,servers=servers,
                future_sensor_assumptions={'gpu_temperature_per_load_fraction':17,'off_gpu_above_inlet_c':2,
                                           'coolant_flow_pump_ecc_ssd':'konstant; keine unbelegte tägliche Verschleissrate',
                                           'operation_profile':'simuliertes Referenzjahr wiederholt, keine echte Prognose' if operations is not None else 'konstantes Szenario',
                                           'service':'setzt nur individuellen Servicealterzähler zurück; keine Verjüngung von Hardware oder gemeinsamer Kühlung'},
                fleet_totals={k:sum(s['selected'][k] for s in servers) for k in servers[0]['selected'] if k.startswith('expected_')},
                limitations=[
                    'Ereignis = ungeplanter Servicebedarf im nächsten vollständig beobachteten 24-h-Fenster; kein exakter Ausfalltermin.',
                    'Nur getrennte Server-Testgruppen; keine prospektive Validierung am realen L4-/Kühlplattensystem.',
                    'Serverwartung setzt nur individuelles Servicealter zurück; Gerätealter, ECC, SSD, Durchfluss, Pumpenstrom und gemeinsamer Kühlungskalender bleiben.',
                    'Temperaturantwort auf Last ist eine Szenarioannahme; keine gemessene Kühlplattenkennlinie oder gelernte kausale Wartungswirkung.',
                    'Erwartungswerte bedingt auf ML und Szenario, keine Konfidenzintervalle oder garantierten Einsatzmengen.',
                    'Zählung pro physischem Server. Standortbesuche können mehrere Server bedienen; summierte Eingriffe sind keine Zahl von Technikerfahrten.',
                    'Keine gemeinsamen Pumpen-/Wärmetauscher-Ausfälle oder Korrelationen modelliert. Separate Standortwartung erforderlich.',
                    'Kosten enthalten nur konfigurierte Servicekosten und optional Ausfallmarge; Hardwareersatz, ML-Betrieb und gemeinsame Hydraulik sind nicht automatisch enthalten.',
                    'Kein Eingriff in bestehende Gewinnrechnung: Wartungsposten dürfen nicht doppelt gezählt werden.',
                    'Keine automatische Serversteuerung; harte Schutzfunktionen und Herstellerintervalle bleiben verbindlich.',
                    '30-Tage-Risiko unter dem gewählten Expositionsszenario ohne Server-Service.',
                    'Betriebsprofile sind einseitige Eingaben. Erwartete Wartungsausfälle werden noch nicht in Wärmebilanz und Jobfristen zurückgerechnet.'
                ])
