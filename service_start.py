#!/usr/bin/env python3
"""Train and run DigitalHeat's maintenance planning model.

python3 service_start.py --demo --output daten/ergebnisse/service_ml
python3 service_start.py --history history.csv --fleet fleet.csv --output report
Dependencies: requirements-ml.txt. All inputs are CSV, no external model execution.
"""
import argparse
import csv
import html
import json
from pathlib import Path
import webbrowser
from src.service_ml import ServiceConfig, calculate, demo_data, read_csv
from src.service_case import case_trace, calendar_operations, case_fleet, site_plan


def write_csv(path, rows):
    with Path(path).open('w', encoding='utf-8', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def save_report(result,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    (output/'service_plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    rows=[];candidates=[]
    for s in result['servers']:
        rows.append(dict(server_id=s['server_id'],status=result['status'],
                         next_routine_date=s['next_routine_date'],
                         next_routine_in_days=s['next_routine_in_days'],
                         risk_next_30_days_without_service=s['risk_next_30_days_without_service'],
                         outside_training_range=','.join(s['outside_training_range']),
                         future_scenario_outside_training_range=','.join(s['future_scenario_outside_training_range']),
                         scenario_inspection_flag=s['scenario_inspection_flag'],**s['selected']))
        rows[-1].update({f'forecast_{k}':s.get('forecast_exposure',{}).get(k) if s.get('forecast_exposure') else None
                        for k in ('powered_hours','compute_hours','starts')})
        rows[-1]['allocated_shared_cooling_chf']=s.get('allocated_shared_cooling_chf')
        for candidate in s['candidates']:
            candidates.append(dict(server_id=s['server_id'],**candidate))
    write_csv(output/'server_service.csv',rows);write_csv(output/'intervalle.csv',candidates)
    def esc(value):return html.escape(str(value),quote=True)
    table=''.join('<tr>'+''.join(f'<td>{esc(v)}</td>' for v in (
        s['server_id'],f"{s['recommended_interval_days']} Tage",s['next_routine_date'],
        f"{s['risk_next_30_days_without_service']*100:.1f} %",
        f"{s['selected']['expected_planned']:.2f}",f"{s['selected']['expected_unplanned']:.2f}",
        f"{s['selected']['expected_total']:.2f}",f"{s['selected']['expected_total_cost_chf']:.0f} CHF",
        'Prüfen' if s['scenario_inspection_flag'] or s['outside_training_range'] or s['future_scenario_outside_training_range'] else 'Szenario'))+'</tr>' for s in result['servers'])
    details=''
    for s in result['servers']:
        candidate_rows=''.join(f"<tr><td>{c['interval_days']} Tage</td><td>{c['expected_planned']:.2f}</td><td>{c['expected_unplanned']:.2f}</td><td>{c['expected_total_cost_chf']:.0f} CHF</td></tr>" for c in s['candidates'])
        details+=f"<details><summary>{esc(s['server_id'])}: alle Intervalle</summary><table><tr><th>Intervall</th><th>Geplant</th><th>Ungeplant</th><th>Kosten</th></tr>{candidate_rows}</table><p>Aktuell ausserhalb Trainingsbereich: {esc(', '.join(s['outside_training_range']) or 'keine Merkmale')}. In zukünftigen Szenariozuständen: {esc(', '.join(s['future_scenario_outside_training_range']) or 'keine Merkmale')}.</p></details>"
    warnings=''.join(f'<li>{esc(v)}</li>' for v in result['limitations'])
    info=result['model'];config=result['config']; totals=result['fleet_totals']
    exposure=''
    if result.get('case_operation'):
        items=''.join(f"<tr><td>{esc(s['server_id'])}</td><td>{s['forecast_exposure']['powered_hours']:.1f}</td><td>{s['forecast_exposure']['compute_hours']:.1f}</td><td>{s['forecast_exposure']['starts']:.0f}</td></tr>" for s in result['servers'])
        exposure=f'<section><h2>Case-Betrieb pro Server</h2><p>Simulierte eingeschaltete Stunden, äquivalente Rechenstunden und Starts im Planungszeitraum. Kalenderalter und Rechenlast werden getrennt geführt. Das Wetterjahr 2025 wird nach Monat und Tag wiederholt; diese Profile sind keine echte Zukunftsprognose. Historische Anfangszähler und Sensoren bleiben Demowerte.</p><table><tr><th>Server</th><th>Eingeschaltete Stunden</th><th>Rechenstunden</th><th>Starts</th></tr>{items}</table></section>'
    site_html=''
    if result.get('site_service'):
        site=result['site_service']
        dates=', '.join(site['scheduled_dates']) or 'keine im Zeitraum'
        site_html=f"<section><h2>Gemeinsame Kühlung separat warten</h2><p>Standort {esc(site['site_id'])}: fester Kalender alle {site['interval_days']} Tage. Termine: {esc(dates)}. {site['scheduled_cooling_visits']} geplante Kühlungsbesuche, {site['cooling_budget_chf']:.0f} CHF Standortbudget, rechnerisch {site['allocated_budget_per_server_chf']:.0f} CHF Anteil pro Server. Ein Servereingriff verschiebt diese Termine nicht.</p><p>{esc(site['assumption'])}</p><p>Servereingriffe und Kühlungsbesuche werden getrennt gezählt. Gemeinsame Anfahrten und Terminbündelung sind noch nicht modelliert. Budget für beide getrennten Leistungsumfänge: {result['separate_budgets']['combined_service_budget_chf']:.0f} CHF. Die bestehende Unternehmensrechnung wird nicht verändert.</p></section>"
    document=f'''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DigitalHeat · Serviceplanung</title>
<style>body{{font:16px system-ui,sans-serif;background:#f4f5f7;color:#202124;margin:0}}main{{max-width:1250px;margin:auto;padding:32px 22px}}h1{{font-size:34px}}.notice{{background:#fff2cf;padding:20px;border-radius:14px}}section,details{{background:white;padding:20px;margin:18px 0;border-radius:14px}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:12px 9px;text-align:left;border-bottom:1px solid #ddd}}.scroll{{overflow:auto}}summary{{cursor:pointer;font-weight:600}}li{{margin:10px 0}}p{{line-height:1.55}}a{{color:#1464c8}}</style>
<main><p>DigitalHeat · Kühlplatten · Wartungsmodell</p><h1>Service pro Server planen</h1>
<div class="notice"><strong>{esc(result['status'])}</strong><p>Die Zahlen sind modellierte Erwartungen, keine Wartungszusagen. {config['horizon_days']} Tage Planung ab dem jeweiligen Serverdatum. Herstellerintervalle und Schutzfunktionen haben Vorrang.</p></div>
<section><h2>Ergebnis pro physischem Server</h2><p>Das gewählte Intervall hat unter den eingegebenen Kosten und Serviceannahmen die niedrigsten erwarteten Gesamtkosten. Der nächste Termin gilt, solange kein ungeplanter Service dazwischenkommt. Das 30-Tage-Risiko gilt ohne Service.</p><div class="scroll"><table><tr><th>Server</th><th>Intervall</th><th>Nächster Termin</th><th>30-Tage-Risiko</th><th>Geplant</th><th>Ungeplant</th><th>Eingriffe gesamt</th><th>Serverkosten / Zeitraum</th><th>Hinweis</th></tr>{table}</table></div>
<p>Flotte: {totals['expected_total']:.2f} erwartete Servereingriffe, {totals['expected_total_cost_chf']:.0f} CHF. Mehrere Eingriffe können bei einem einzigen Standortbesuch erledigt werden. Ungeplante Vollservices ersetzen anstehende Routinen; deshalb können weniger als ein geplanter Eingriff pro Jahr erwartet werden. Bruchteile sind Durchschnittswerte, keine halben Besuche.</p></section>
{exposure}{site_html}<section><h2>Intervalle vergleichen</h2>{details}</section>
<section><h2>Was das ML tatsächlich gelernt hat</h2><p>Gradient Boosting lernt das Ereignis „ungeplanter Servicebedarf innerhalb der nächsten 24 Stunden“. Eine separate Kalibrierung passt die Wahrscheinlichkeiten an. Training, Kalibrierung und Test verwenden verschiedene Server.</p>
<p>Test: {info['rows'][2]} Tagesfenster, {info['events'][2]} Ereignisse. Brier-Fehler: ML {info['test_brier']:.6f}, konstante Basis {info['baseline_brier']:.6f}. Log-Loss: ML {info['test_log_loss']:.5f}, Basis {info['baseline_log_loss']:.5f}. Bei diesen beiden Fehlerwerten ist kleiner besser. Eine gute Bewertung auf künstlichen Daten belegt keinen Nutzen an echter Hardware.</p></section>
<section><h2>Kosten und Annahmen</h2><p>Geplanter Eingriff: {config['planned_chf']:.0f} CHF / {config['planned_downtime_h']:g} h. Ungeplanter Eingriff: {config['unplanned_chf']:.0f} CHF / {config['unplanned_downtime_h']:g} h. Entgangener Deckungsbeitrag: {config['lost_margin_chf_h']:g} CHF/h. Keine automatische Übernahme in die bestehende Gewinnrechnung.</p><ul>{warnings}</ul></section>
<p><a href="server_service.csv">Server-Kennzahlen CSV</a> · <a href="intervalle.csv">Alle Intervalle CSV</a> · <a href="service_plan.json">Vollständige Ergebnisse JSON</a></p></main></html>'''
    (output/'index.html').write_text(document,encoding='utf-8')
    return output/'index.html'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo',action='store_true',help='Explizit künstliche Daten verwenden')
    parser.add_argument('--case',action='store_true',help='Demo mit saisonalem Betrieb der acht Case-Server koppeln')
    parser.add_argument('--history',type=Path);parser.add_argument('--fleet',type=Path)
    parser.add_argument('--output',type=Path,default=Path('daten/ergebnisse/service_ml'))
    parser.add_argument('--intervals',default='30,60,90,180,365')
    parser.add_argument('--max-interval',type=int,default=365)
    parser.add_argument('--days',type=int,default=365)
    parser.add_argument('--planned-cost',type=float,default=400)
    parser.add_argument('--unplanned-cost',type=float,default=900)
    parser.add_argument('--planned-hours',type=float,default=2)
    parser.add_argument('--unplanned-hours',type=float,default=12)
    parser.add_argument('--lost-margin',type=float,default=0)
    parser.add_argument('--seed',type=int,default=2026)
    parser.add_argument('--as-of',default='2026-11-21',help='Planungsbeginn der gekoppelten Case-Demo')
    parser.add_argument('--cooling-interval',type=int,default=180)
    parser.add_argument('--cooling-age',type=int,default=0)
    parser.add_argument('--cooling-cost',type=float,default=600)
    parser.add_argument('--cooling-hours',type=float,default=2)
    parser.add_argument('--open',action='store_true')
    args=parser.parse_args()
    try:
        if args.demo and (args.history or args.fleet):raise ValueError('Demo und echte Eingaben dürfen nicht vermischt werden.')
        if args.case and not args.demo:raise ValueError('--case benötigt --demo: simulierte Profile sind keine echten Messdaten.')
        if not args.demo and not (args.history and args.fleet):raise ValueError('--demo oder beide Dateien --history und --fleet angeben.')
        cfg=ServiceConfig(horizon_days=args.days,intervals=tuple(int(v) for v in args.intervals.split(',')),
                          max_interval_days=args.max_interval,planned_chf=args.planned_cost,unplanned_chf=args.unplanned_cost,
                          planned_downtime_h=args.planned_hours,unplanned_downtime_h=args.unplanned_hours,lost_margin_chf_h=args.lost_margin)
        print('Betriebsdaten vorbereiten …',flush=True)
        history,fleet=demo_data(args.seed) if args.demo else (read_csv(args.history,True),read_csv(args.fleet))
        operations=None;trace=None;site=None
        if args.case:
            print('Bestehenden Jahres-Scheduler pro Server protokollieren …',flush=True)
            trace=case_trace();fleet=case_fleet(trace,args.as_of)
            operations=calendar_operations(trace,args.as_of,max(30,cfg.horizon_days))
            site=site_plan(args.as_of,cfg.horizon_days,len(fleet),args.cooling_interval,args.cooling_age,args.cooling_cost,args.cooling_hours)
        print('ML trainieren, kalibrieren und Wartungsintervalle berechnen …',flush=True)
        result=calculate(history,fleet,cfg,args.demo,args.seed,operations)
        if trace:
            result['case_operation']={k:v for k,v in trace.items() if k!='rows'}
            result['site_service']=site
            server_service=result['fleet_totals']['expected_service_cost_chf']
            server_margin=result['fleet_totals']['expected_total_cost_chf']-server_service
            site_margin=site['server_hours_unavailable']*cfg.lost_margin_chf_h
            result['separate_budgets']=dict(server_interventions_chf=server_service,
                server_lost_margin_chf=server_margin,shared_lost_margin_chf=site_margin,
                shared_cooling_chf=site['cooling_budget_chf'],
                combined_service_budget_chf=server_service+site['cooling_budget_chf'],
                combined_cost_with_margin_chf=result['fleet_totals']['expected_total_cost_chf']+site['cooling_budget_chf']+site_margin,
                overlap_assumption='Keine Terminbündelung oder Überlappung von Server- und Standortausfällen berücksichtigt; keine exakte Technikerfahrtenrechnung.')
            for s in result['servers']:s['allocated_shared_cooling_chf']=site['allocated_budget_per_server_chf']
        page=save_report(result,args.output)
        if trace:
            write_csv(args.output/'case_betrieb_2025.csv',trace['rows'])
            write_csv(args.output/'geplanter_betrieb.csv',[r for rows in operations.values() for r in rows])
            (args.output/'kuehlungskalender.json').write_text(json.dumps(site,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if args.demo:
            write_csv(args.output/'beispiel_historie.csv',history)
            write_csv(args.output/'beispiel_server.csv',fleet)
        print(result['status'])
        for s in result['servers']:
            v=s['selected']
            print(f"{s['server_id']}: Intervall {v['interval_days']} Tage, {v['expected_planned']:.2f} geplante + {v['expected_unplanned']:.2f} ungeplante Eingriffe / {cfg.horizon_days} Tage; {v['expected_total_cost_chf']:.0f} CHF")
        print(f'Bericht: {page.resolve()}')
        if args.open:webbrowser.open(page.resolve().as_uri())
    except (ValueError,OSError) as exc:
        parser.exit(2,f'Fehler: {exc}\n')


if __name__=='__main__':main()
