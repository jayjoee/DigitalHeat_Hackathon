"""Reproducible matched experiment: rules vs efficient rules vs efficient ML."""
from dataclasses import asdict
from datetime import datetime,timedelta
import csv
import hashlib
import json
import time
from pathlib import Path
from threadpoolctl import threadpool_limits
from src.ml_system.config import Config
from src.ml_system.forecast import Forecast
from src.ml_system.simulation import make_jobs,simulate,summarise,jobs_digest
from src.scheduler.jahr import profil_laden

ROOT=Path(__file__).resolve().parents[2]

def compare(config=None,days=30,start='2025-07-01',progress=lambda text:None,controlled=False):
    config=config or Config()
    if type(days) is not int or not 1<=days<=184:raise ValueError('Zeitraum: 1 bis 184 Tage.')
    try:begin=datetime.strptime(start,'%Y-%m-%d'); finish=begin+timedelta(days=days)
    except (ValueError,TypeError):raise ValueError('Ungültiges Startdatum.')
    if begin<datetime(2025,7,1) or finish>datetime(2026,1,1):
        raise ValueError('Auswertung muss vollständig zwischen Juli und Dezember 2025 liegen.')
    profile=profil_laden()
    indices=[i for i,p in enumerate(profile) if start<=p['zeit'][:10]<finish.strftime('%Y-%m-%d')]
    if not indices:raise ValueError('Keine Daten für den Zeitraum.')
    first,last=indices[0],indices[-1]+1
    progress('ML-Modell trainieren · Januar bis Mai')
    model=Forecast(profile).fit()
    progress('Prognosen berechnen · ausschliesslich zeitlich verfügbare Informationen')
    # Calibrate both forecast methods on the same held-out June observations.
    cx,cy,ct=model.dataset('2025-06-01','2025-07-01')
    import numpy as np
    persistence_margin=max(0,float(np.quantile(cy-np.array([model.heat[t-24] for t in ct]),.90)))
    ml={}; persistence={}; ml_errors=[]; persistence_errors=[]; forecast_rows=[]
    for h in indices:
        ml[h]=model.predict(h,config.horizon_hours)
        persistence[h]=model.persistence(h,config.horizon_hours)
        for offset,(m,p) in enumerate(zip(ml[h],persistence[h]),1):
            target=h+offset
            if target>=last:continue
            actual=float(model.heat[target])
            ml_errors.append(abs(m-actual)); persistence_errors.append(abs(p-actual))
            forecast_rows.append({'origin':profile[h]['zeit'],'target':profile[target]['zeit'],
                                  'horizon_hours':offset,'actual_kwh':actual,'ml_kwh':m,'persistence_kwh':p})
    jobs=make_jobs(config,first,last)
    progress('Energie- und Auftragsbilanzen berechnen')
    original=simulate(profile,config,jobs,first,last,'uncontrolled' if controlled else 'standard')
    heat=simulate(profile,config,jobs,first,last,'heat',persistence,persistence_margin) if controlled else None
    efficient=simulate(profile,config,jobs,first,last,'heat_off' if controlled else 'efficient',persistence,persistence_margin)
    learned=simulate(profile,config,jobs,first,last,'heat_ml' if controlled else 'ml',ml,model.margin)
    # Timed software execution × assumed host power. Not a wall-meter measurement.
    ml_energy=model.seconds/3600*config.ml_host_kw
    learned['rows'][0]['ml_kwh']+=ml_energy
    learned['rows'][0]['total_kwh']+=ml_energy
    summarise(learned,config)
    a,b=efficient['energy']['total_kwh'],learned['energy']['total_kwh']
    savings=a-b
    comparable=abs(efficient['completed_work']-learned['completed_work'])<1e-7
    result={'schema':1,'period':{'start':start,'end_exclusive':finish.strftime('%Y-%m-%d'),'hours':len(indices)},
            'config':config.public(),'model':{**model.info,'timed_compute_seconds':model.seconds,
                'compute_energy_kwh_estimate':ml_energy,'energy_method':'Gemessene Softwarelaufzeit × angenommene Hostleistung; Training und Prognosen enthalten',
                'persistence_safety_margin_kwh':persistence_margin},
            'forecast_metrics':{'ml_mae_kwh':float(np.mean(ml_errors)) if ml_errors else None,
                'persistence_mae_kwh':float(np.mean(persistence_errors)) if persistence_errors else None,
                'scored_predictions':len(ml_errors),'horizon_hours':config.horizon_hours},
            'comparison':{'additional_ml_savings_kwh':savings,'additional_ml_savings_percent':100*savings/a if a else 0,
                'changed_reserve_hours':sum(abs(x['reserve_target_kwh']-y['reserve_target_kwh'])>1e-8 for x,y in zip(efficient['rows'],learned['rows'])),
                'changed_dispatch_hours':sum(abs(x['work']-y['work'])>1e-8 for x,y in zip(efficient['rows'],learned['rows'])),
                'same_completed_work':comparable,'identical_input_jobs':True,'jobs_sha256':jobs_digest(jobs),
                'verdict':(('Unterschied unter 0,1 %: kein belastbarer zusätzlicher Effizienznachweis für ML.' if abs(savings/a*100)<0.1 else ('ML spart in diesem Szenario zusätzlich Strom.' if savings>0 else 'ML spart in diesem Szenario keinen zusätzlichen Strom.')))+
                           ('' if comparable else ' Achtung: Vollendete Arbeitsmenge unterscheidet sich; kein Vergleich bei gleicher Lieferleistung.')},
            'scenarios':[original,heat,efficient,learned] if controlled else [original,efficient,learned],
            'limitations':[
                'Nur Referenzhaus; bestehender Flottenrouter und Live-Prototyp bleiben unverändert. Keine physische Steuerung.',
                'Echtes trainiertes ML-Modell auf synthetischem Case-Wärmebedarf; kein Nachweis an echten Häusern.',
                'Neue Verbrauchs-, Effizienz-, Start- und Verlustprofile sind ungemessene Szenarioannahmen.',
                'Arbeitsmengen aus bisherigen Referenzjobs, keine gemessenen L4- oder echten Pharma-Modelle.',
                'Identische endliche Alibaba-basierte Ankünfte, kein unbegrenzter Spot-Nachschub. Aktueller Stundenbedarf gilt als beobachtet.',
                'Veröffentlichung historischer Wetterläufe wird mit dem bisherigen 8-h-Verzug angenähert.',
                'Auswertung nur Juli–Dezember 2025; Saisonverschiebung und geringe Datenbasis. Kein Vergleich an unabhängigen Gebäuden.',
                'ML-Strom geschätzt aus Softwarelaufzeit und Hostleistungsannahme; keine Steckdosenmessung.',
                'Finanzkennzahl ist ein Periodenbeitrag vor Fixkosten/Investition/Steuern, keine neue Jahresgewinnprognose.',
                'Vergleichserlös pro fertiggestellter Referenzarbeit normalisiert; keine bewiesene Nachfrage oder reale Abrechnung.'
            ]}
    result['forecast_samples']=forecast_rows[::max(1,len(forecast_rows)//1200)]
    return result


def daily_rows(result):
    out={}
    for scenario in result['scenarios']:
        for r in scenario['rows']:
            key=(scenario['variant'],r['time'][:10])
            d=out.setdefault(key,{'variant':key[0],'date':key[1],**{k:0.0 for k in ['total_kwh','it_kwh','pump_kwh','ml_kwh','backup_kwh','demand_kwh','useful_heat_kwh','work']}})
            for k in d:
                if k not in ('variant','date'):d[k]+=r[k]
    return list(out.values())


def save(result,directory=None):
    directory=Path(directory) if directory else ROOT/'daten'/'ergebnisse'/'ml'
    directory.mkdir(parents=True,exist_ok=True)
    # Data-only formats; model deserialization/upload is intentionally not exposed.
    (directory/'vergleich.json').write_text(json.dumps(result,ensure_ascii=False,indent=1,allow_nan=False),encoding='utf-8')
    for name,rows in [('tage.csv',daily_rows(result)),('stunden.csv',[{'variant':s['variant'],**r} for s in result['scenarios'] for r in s['rows']])]:
        with (directory/name).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    # Standalone page works from a file as well as from the local server.
    template=(ROOT/'dashboard'/'ml'/'template.html').read_text(encoding='utf-8')
    public={**result,'scenarios':[{k:v for k,v in s.items() if k!='rows'} for s in result['scenarios']], 'daily':daily_rows(result)}
    encoded=json.dumps(public,ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
    (ROOT/'dashboard'/'ml'/'index.html').write_text(template.replace('<!--RESULT_DATA-->',encoded),encoding='utf-8')
    return public
