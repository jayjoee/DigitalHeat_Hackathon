#!/usr/bin/env python3
"""Run the resource-queue comparison, no GPU or extra Python packages required."""
import argparse
import csv
import json
from pathlib import Path
from src.scheduler.queue_benchmark import compare


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('daten/ergebnisse/queue'))
    args=parser.parse_args();result=compare();args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'vergleich.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    rows=[{k:v for k,v in r.items() if k!='completed_ids'} for r in result['scenarios']]
    with (args.output/'vergleich.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
    text=['# Vergleich der Auftragswarteschlangen','',result['status'],'',
          'Alle Varianten prüfen dieselben Ressourcen- und Sicherheitsbedingungen und erhalten dieselben Aufträge. Geändert werden Reihenfolge, Platzierung und die simulierte Standby-Steuerung.','',
          '| Strategie | Fertig | Frist verpasst | Serverstrom kWh | Strom CHF | Mittlere Wartezeit s |',
          '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        text.append(f"| {r['strategy']} | {r['completed']} | {r['missed']} | {r['it_kwh']:.3f} | {r['electricity_chf']:.3f} | {r['mean_wait_seconds']:.1f} |")
        print(f"{r['strategy']}: {r['completed']}/{r['submitted']} fertig, {r['missed']} Fristen verpasst, {r['it_kwh']:.3f} kWh")
    text+=['',f"Identische fertiggestellte Aufträge: {result['same_completed_jobs']}",'','## Annahmen','']
    text += [f'- **{k}:** {v}' for k,v in result['assumptions'].items()]
    text+=['','Die Ergebnisse dürfen nicht mit der Jahresbilanz oder dem früheren Halbjahresvergleich gleichgesetzt werden. Forschungsgrundlage und übernommene Verfahren stehen in docs/RESSOURCEN_SCHEDULER.md im Projekt.']
    (args.output/'Bericht.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(f'Bericht: {(args.output/"Bericht.md").resolve()}')


if __name__=='__main__':main()
