#!/usr/bin/env python3
"""Four controlled strategies, identical finite jobs and hardware assumptions.

Run: python3 start/vergleich_start.py --days 184 --output daten/ergebnisse/strategievergleich
Dependencies: requirements/ml.txt. Does not change the existing ML dashboard.
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # Repo-Wurzel, damit «src» gefunden wird
import argparse
import csv
import hashlib
import json
from pathlib import Path

from src.ml_system.experiment import compare

LABELS = {
    'uncontrolled': 'Ohne Wärmesteuerung',
    'heat': 'Wärmesteuerung, Leerlauf',
    'heat_off': 'Wärmesteuerung + Abschalten',
    'heat_ml': 'Wärmesteuerung + Abschalten + ML',
}


def write_report(result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    baseline = result['scenarios'][0]
    table = []
    for s in result['scenarios']:
        e = s['energy']
        table.append(dict(
            strategie=LABELS[s['variant']], gesamtstrom_kwh=e['total_kwh'],
            serverstrom_kwh=e['it_kwh'], pumpenstrom_kwh=e['pump_kwh'],
            zusatzheizung_strom_kwh=e['backup_kwh'], ml_strom_kwh=e['ml_kwh'],
            nutzwaerme_kwh=e['useful_heat_kwh'], abwaerme_verworfen_kwh=e['dumped_heat_kwh'],
            speicherverlust_kwh=e['storage_loss_kwh'],
            endbestand_speicher_kwh=s['rows'][-1]['storage_kwh'],
            waermedeckung_prozent=100*s['heat_coverage'],
            auftraege_eingereicht=s['submitted_jobs'], fristgerecht=s['completed_jobs'],
            frist_verpasst=s['missed_jobs'], am_ende_offen=s['pending_jobs'],
            erledigte_referenzarbeit=s['completed_work'],
            kwh_pro_erledigter_referenzarbeit=s['kwh_per_completed_work'],
            stromdifferenz_zur_basis_kwh=e['total_kwh']-baseline['energy']['total_kwh'],
            gleiche_erledigte_auftraege_wie_basis=s['completed_job_ids']==baseline['completed_job_ids'],
        ))
    result['controlled_comparison'] = {
        'same_hardware_and_speed': True, 'active_kw': result['config']['values']['active_kw'],
        'work_per_active_server_hour': 1.0,
        'method': 'EDF ohne Wärmelimit; danach Wärmesteuerung mit Vortagesprognose; danach Abschalten; zuletzt nur Prognose durch ML ersetzt.',
        'scope': 'Ein Haus, endliche Aufträge, Juli–Dezember; keine Flottenmigration oder reale Pharma-GPU-Messung.',
        'boundary': 'Alle Varianten starten mit leerem Speicher und leerer Warteschlange. Kein Nachlauf nach Periodenende; offene Aufträge separat.',
        'interpretation': 'Gleiche Eingaben garantieren keine gleiche Lieferleistung. Stromdifferenzen nur zusammen mit Fristen, Arbeitsmenge und Speicherendbestand bewerten.',
        'baseline': 'Alle Server bleiben an; vorhandene Abwärme wird auch ohne Wärmesteuerung zurückgewonnen. Keine künstliche Rechenarbeit ohne Kundenauftrag.',
    }
    result['table'] = table
    encoded = json.dumps(result, ensure_ascii=False, indent=1, allow_nan=False)
    (output/'vergleich.json').write_text(encoded, encoding='utf-8')
    with (output/'vergleich.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=table[0], lineterminator='\n')
        w.writeheader(); w.writerows(table)
    lines = ['# Vergleich der Betriebsstrategien', '',
             f"Zeitraum: {result['period']['start']} bis {result['period']['end_exclusive']} (exklusiv), {result['period']['hours']} Stunden.", '',
             '**Simulation mit ungemessenen Leistungsprofilen, keine gemessene Einsparung an NVIDIA-Hardware.**', '',
             'Alle Varianten erhalten dieselben Aufträge, Ankünfte, Fristen, Server und Rechengeschwindigkeiten. Auch die Basis nutzt ihre Abwärme. Gesamtstrom enthält Server, Pumpen, elektrische Zusatzheizung (COP 2,5) und bei ML die geschätzte Modellenergie.', '',
             '| Strategie | Gesamtstrom kWh | Nutzwärme kWh | Verworfen kWh | Deckung | Fristgerecht | Verpasst | Offen |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in table:
        lines.append(f"| {r['strategie']} | {r['gesamtstrom_kwh']:.1f} | {r['nutzwaerme_kwh']:.1f} | {r['abwaerme_verworfen_kwh']:.1f} | {r['waermedeckung_prozent']:.1f} % | {r['fristgerecht']} | {r['frist_verpasst']} | {r['am_ende_offen']} |")
    lines += ['', '## So ist der Vergleich zu lesen', '',
              '- Wärmesteuerung verschiebt flexible Arbeit; dringende Aufträge dürfen Überschusswärme erzeugen.',
              '- Die ersten beiden Varianten bleiben eingeschaltet. Die dritte schaltet unbenötigte Server ab, einschliesslich Startverlusten. Nur die vierte verwendet ML.',
              '- Alle vier rechnen mit 1 Referenzarbeitseinheit je aktiver Serverstunde bei derselben Leistung. Das frühere angenommene Sparprofil wird hier nicht verwendet.',
              '- Weniger Strom bei weniger erledigten Aufträgen ist kein Nachweis gleicher Lieferleistung. CSV und JSON enthalten Arbeitsmengen und den Vergleich der erledigten Auftrags-IDs.',
              '- Start: Speicher und Warteschlange leer. Am Ende offene Aufträge werden weder als erledigt noch automatisch als verspätet gezählt. Verbleibende Speicherwärme ist noch keine genutzte Wärme.',
              '- Zusatzheizung stellt in allen Varianten den gleichen Wärmebedarf sicher. Ihre angenommene elektrische Versorgung ist eine Vergleichsannahme, kein Nachweis für den Öl-Pilot.',
              '- Prognosemodell: Training Januar–Mai, Kalibrierung Juni, Auswertung Juli–Dezember 2025. Die Prognose verwendet keine künftigen Ist-Beobachtungen.',
              '- ML-Energie = gemessene Softwarelaufzeit × angenommene Hostleistung; diese kleine Position kann zwischen Läufen schwanken.', '',
              f"Auftrags-Fingerabdruck: `{result['comparison']['jobs_sha256']}`", '',
              'Reproduktion: `python3 start/vergleich_start.py --days 184 --output daten/ergebnisse/strategievergleich`', '',
              'Die vollständigen Stundenwerte und Annahmen stehen in vergleich.json, die Kennzahlen in vergleich.csv.']
    (output/'Bericht.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    manifest = {'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (output/'vergleich.json', output/'vergleich.csv', output/'Bericht.md')}}
    (output/'pruefsummen.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return table


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=184)
    parser.add_argument('--start', default='2025-07-01')
    parser.add_argument('--output', type=Path, default=Path('daten/ergebnisse/strategievergleich'))
    args = parser.parse_args()
    result = compare(days=args.days, start=args.start, progress=lambda s: print(s, flush=True), controlled=True)
    table = write_report(result, args.output)
    for row in table:
        print(f"{row['strategie']}: {row['gesamtstrom_kwh']:.2f} kWh; {row['fristgerecht']} fertig, {row['frist_verpasst']} verspätet, {row['am_ende_offen']} offen")
    print(f'Bericht: {(args.output / "Bericht.md").resolve()}')


if __name__ == '__main__':
    main()
