"""Evidence register for service reports; values follow the actual run configuration.

A source for a method is never a source for our invented hardware failure rates.
"""
from src.service_ml import FEATURES, BOUNDS

CASE='quellen/CASE.md'
COOLIT='https://www.coolitsystems.com/products-services/global-professional-services/'
NVIDIA='https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/l4/PB-11316-001_v01.pdf'
LATIF='https://arxiv.org/html/2412.08602v2'
SKLEARN='https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html'
CALIBRATION='https://scikit-learn.org/1.6/modules/generated/sklearn.calibration.CalibratedClassifierCV.html'


def assumption_register(result):
    c=result['config']; rows=[]
    def add(key,parameter,value,category,source,scope,url='',used=True):
        rows.append(dict(id=key,parameter=parameter,value=str(value),category=category,
                         source=source,source_url=url,scope=scope,used_in_calculation=used))
    def own(key,parameter,value,scope):
        add(key,parameter,value,'Eigene Annahme','Keine empirische Quelle; von uns gesetzter Testwert / Modellentscheid',scope)

    own('horizon','Planungszeitraum',f"{c['horizon_days']} Tage",'Vom Benutzer konfigurierter Rechenhorizont; kein Wartungsstandard.')
    own('server_intervals','Verglichene Serverintervalle',', '.join(map(str,c['intervals']))+' Tage','Nur diese Kandidaten werden verglichen; das Ergebnis ist kein globales Optimum.')
    own('server_limit','Maximales Serverintervall',f"{c['max_interval_days']} Tage",'Betreibergrenze; keine Herstellerfreigabe. Reale Vorgaben haben Vorrang.')
    own('planned_cost','Geplanter Server-Service',f"{c['planned_chf']:g} CHF / {c['planned_downtime_h']:g} h",'Keine Offerte oder gemessene Einsatzdauer; je individuellem Servereingriff.')
    own('unplanned_cost','Ungeplanter Server-Service',f"{c['unplanned_chf']:g} CHF / {c['unplanned_downtime_h']:g} h",'Keine Offerte oder gemessene Reparaturdauer; Ersatzteile sind nicht automatisch vollständig enthalten.')
    own('margin','Entgangener Deckungsbeitrag',f"{c['lost_margin_chf_h']:g} CHF je Server-Ausfallstunde",'Kein GPU-Umsatz und keine empirische Verlustmessung; 0 bedeutet, dass dieser Posten nicht bewertet wird.')
    own('server_recovery','Wirkung eines Servereingriffs','Nur individueller Servicealterzähler wird auf 0 gesetzt','Voraussetzung: vollständiger individueller Service. Kein Reset von Gerätealter, Betriebs-/Rechenstunden, Starts, ECC, SSD oder gemeinsamer Kühlung. Keine kausal validierte Risikosenkung.')
    own('daily_renewal','Tagesmodell','Höchstens ein Servereingriff je Tag; geplanter Service unterdrückt ungeplanten Eingriff am selben Tag','Diskrete Vereinfachung. Ausfallstunden werden als Kosten addiert, nicht als exakter untertägiger Prozess simuliert.')
    own('boundaries','Zeitraum und Kostenvergleich','Enddatum exklusiv; bei gleichen Kosten längeres Intervall','Endliche Planung statt Lebensdaueroptimierung; keine Modellunsicherheit oder Konfidenzintervalle.')
    info=result['model']
    add('ml_method','ML-Verfahren','HistGradientBoostingClassifier mit separater Sigmoid-Kalibrierung',
        'Dokumentierte Methode','scikit-learn 1.6','Die Quelle erklärt die Softwaremethode, nicht die Wartungsrate unserer Server.',SKLEARN)
    add('calibration','Kalibrierung','Sigmoid auf separaten Servern',
        'Dokumentierte Methode','scikit-learn CalibratedClassifierCV / FrozenEstimator','Separate Kalibrierungsdaten; keine Hardwarevalidierung.',CALIBRATION)
    own('split','Datenaufteilung','60 % Training / 20 % Kalibrierung / 20 % Test, nach Server-ID','Von uns gewählte Aufteilung. Derselbe Server ist nie in mehreren Gruppen; keine prospektive Feldvalidierung.')
    params=info.get('estimator_parameters',{'max_iter':100,'max_leaf_nodes':12,'min_samples_leaf':150,'l2_regularization':10,'early_stopping':False})
    own('hyperparameters','ML-Einstellungen',', '.join(f'{k}={v}' for k,v in params.items()),'Technische Konfiguration von uns; kein Nachweis optimaler Einstellungen oder Ausfallwahrscheinlichkeiten.')
    own('data_minimum','Mindestmenge für Import','12 Server; je Gruppe 5 Ereignisse und 5 ereignisfreie Tage','Technische Plausibilitätsprüfung; keine statistisch begründete Mindeststichprobe.')
    own('alarm','Szenario-Prüfhinweis','GPU-Temperatur ≥ 90 °C oder Durchfluss ≤ 0 l/min','Keine L4-Herstellergrenze und kein Schutzsystem. Echte Schutzgrenzen müssen aus der gewählten Hardware stammen.')
    own('input_bounds','Eingabegrenzen','; '.join(f'{f}: {lo} bis {hi}' for f,(lo,hi) in zip(FEATURES,BOUNDS)),
        'Software-Prüfbereiche, keine zulässigen Hersteller-Betriebsgrenzen. Die Trainingsbereichsprüfung ist zusätzlich und enger.')

    if result.get('synthetic'):
        add('training_data','Trainingsdaten',f"{sum(info['rows'])} künstliche Tageswerte; Gruppen {info['rows']}",
            'Synthetisch','Eigener Datengenerator; keine empirische Quelle','Standardgenerator: 120 fiktive Server × 540 Tage ab 01.01.2023. Keine echte Wartungshistorie.')
        own('seed','Zufallssaat',info.get('seed','nicht gespeichert'),'Dient Reproduzierbarkeit, nicht der Realitätsnähe.')
        own('generator_environment','Künstliche Umgebungen','Eintritt 25–46 °C; Lastbasis 0,25–0,95; Einschaltbasis 0,35–1; Startbasis 0,05–1 pro Tag; Anfangsalter 365–1499 Tage','Gleichverteilungen im Generator. Saison = 0,35 × cos(2π × Tag/365), Einschalt-Rauschen σ=0,1; Begrenzung auf 0–1, unter 0,1 wird ausgeschaltet. Alle Werte frei gesetzt.')
        own('generator_service_age','Künstliches Servicealter','Je Zeile zufällig 0–365 Tage','Unabhängig gezogene Zustände, keine durchgehend konsistente Wartungsereignis-Historie je Gerät. Nicht zur Schätzung kausaler Serviceeffekte geeignet.')
        own('generator_sensors','Künstliche Kühlung und Fehler',
            'loss = Servicealter/1000 + U(0; 0,08); Durchfluss = 4 × (1−loss) l/min; Pumpenstrom = 1,1 + loss A',
            'Temperatur bei Betrieb = Eintritt + 19 + 17 × Last + 33 × loss + Rauschen σ=2 °C; ausgeschaltet Eintritt+2 °C. ECC aus Poisson(0,1 + 0,08 × max(0; Temperatur−75)); Starts aus Poisson(Startbasis), bei ausgeschaltetem Gerät 0. SSD-Verschleiss = min(99; Alter/70). Sämtliche Beziehungen sind erfunden, keine Herstellerdaten.')
        own('generator_hazard','Formel für künstliche Serviceereignisse',
            'λ = 0,0005 + 0,0000003 × Alter + 0,000012 × max(0; Servicealter−60) + 0,0005 × max(0; Temperatur−74) + 0,0005 × ECC + 0,00015 × Starts',
            'Alle Koeffizienten sind frei gesetzt. Zufälliges Ereignis mit p=1−exp(−λ). NVIDIA-MTBF, Meta-Ausfallzahlen und CoolIT-Intervalle kalibrieren diese Formel ausdrücklich nicht.')
    else:
        add('training_data','Importierte Trainingsdaten',f"{sum(info['rows'])} vollständig beobachtete Tagesfenster",'Benutzerdaten, ungeprüft',
            'Vom Benutzer übergebene CSV-Datei','Herkunft, Repräsentativität und Ereignisdefinition werden nicht durch den Dateiimport bestätigt.')

    own('sensor_future','Künftige Sensorzustände','Durchfluss, Pumpenstrom, ECC und SSD bleiben konstant',
        'Keine künftigen Messwerte verfügbar. Im Case-Modus vereinfachte Temperaturänderung um 17 °C je Lastanteil; ausgeschaltet Eintritt+2 °C. Keine gemessene Kühlplattenkennlinie.')
    own('feedback','Rückkopplung','Wartungsausfälle ändern die Wärme- und Auftragsbilanz bisher nicht','Einseitige Szenariokopplung. Gemeinsame Ausfälle, Fahrtbündelung und Ausfallüberlappungen fehlen; kein Ausweis exakter Technikerfahrten.')

    if result.get('case_operation'):
        trace=result['case_operation']; a=trace['assumptions']
        add('case_heat','Case-Vorgaben','1 kW Referenzserver; 80 % Wärmerückgewinnung; 35 kWh Speicher',
            'Case-Vorgabe','DigitalHeat Case, Starting assumptions / Reference house','Vereinfachungen für die Referenzrechnung, keine eigene Messung der L4-Anlage.',CASE)
        add('case_weather','Wetter und Wärmebedarf','Basel 2025, 8’760 Stunden; Heizformel max(0; 10 × (20−T)/25,6), Heiztag bei Tagesmittel < 12 °C; 12 kWh Warmwasser/Tag',
            'Case-Vorgabe','DigitalHeat Case und bereitgestelltes Referenzprofil','Historisches Wetter und modellierter Wärmebedarf; keine gemessene Hausheizung.',CASE)
        own('case_design','Flotten- und Hardwareentscheidung',f"{trace['servers']} simulierte Server; Projektziel 8 L4 je physischem Host; Kühlplatten",
            'Teamentscheidungen. Case schreibt weder acht Server noch L4 oder Kühlplatten vor. Keine bestätigte 8-L4-Kühlplattenofferte.')
        add('idle','Leerlauf',f"{a['idle_kw']*1000:g} W pro Referenzserver",'Übertragene Vergleichsannahme',
            'Latif et al. 2024: H100-Knoten, 1,86 kW Leerlauf / 7,92 kW Trainingsmedian',
            'Ungefähr 23 % auf 1 kW übertragen. 230 W sind weder direkt gemessen noch eine L4-Spezifikation.',LATIF)
        own('boot','Standby und Start',f"{a['standby_kw']*1000:g} W Standby, {a['start_minutes']:g} Minuten Start, {a['active_kw']:g} kW Startleistung",'Werte aus dem bestehenden Serverbetriebsmodell; keine Messung von Starts der gewählten Hardware.')
        own('dispatch','Schaltregel','1 h Nachlauf; Speicher-Einschaltgrenze 35 %, Ausschaltgrenze 85 %; feste Slotreihenfolge',
            'Bisherige Scheduler-Regel. Keine Wartungsoptimierung der Gerätebelegung. Nicht mit den 2 Minuten / 5 W des separaten Strategievergleichs verwechseln.')
        own('future_case','Künftiges Betriebsprofil','Monat/Tag aus 2025 wiederholen; 29. Februar verwendet 28. Februar',
            'Saisonales Szenario statt Wetter- oder Nachfrageprognose. Bestehende Spot-Variante mit unbegrenzten flexiblen Füllaufträgen; keine gebuchte Pharma-Nachfrage.')
        own('case_initial','Anfangszustand der Case-Server','730 Tage Gerätealter; Anfangszähler = 2 × simuliertes Referenzjahr; Servicealter 30, 50, …, 170 Tage',
            'Keine gemessene Inventarhistorie. Historische Anfangszähler und Servicealter sind von uns gesetzt.')
        own('case_initial_sensors','Anfangssensoren der Case-Server','Eintritt 34 °C; Durchfluss 4 l/min; Pumpe 1,1 A; ECC 0; SSD-Verschleiss 10 %',
            'Keine empirische Quelle für diese Werte. Starttemperatur bei Betrieb 34+19+17×Last °C, ausgeschaltet 36 °C; vorherige Tageslast stammt aus dem wiederholten Case-Profil.')
        add('case_totals','Abgeleitete Betriebszähler',str(trace['totals']),'Simulationsergebnis',
            'Bestehender Jahres-Scheduler, täglicher Export case_betrieb_2025.csv','Ergebnisse der genannten Annahmen, keine zusätzlichen Messdaten. Summen gegen die Jahresbilanz geprüft.')

    if result.get('site_service'):
        s=result['site_service']
        own('cooling_initial_age','Anfangsalter der gemeinsamen Kühlungswartung',f"{s.get('days_since_service','im älteren Ergebnis nicht gespeichert')} Tage seit Service",
            'Von uns beziehungsweise vom Benutzer gesetzter Anfangswert; keine vorhandene Standort-Servicehistorie.')
        add('cooling_schedule','Gemeinsame Kühlung',f"{s['interval_days']} Tage; {s['scheduled_cooling_visits']} Termine im Zeitraum",
            'Eigene Näherung mit Herstellervergleich','CoolIT: vorbeugende Servicebesuche typischerweise alle sechs Monate',
            'CoolIT belegt weder unseren konkreten Tagesabstand noch die Eignung der ausgewählten Anlage. 180 Tage nähern sechs Monate an. Individuelle Servereingriffe verändern diesen Kalender nicht.',COOLIT)
        own('cooling_cost','Kühlungsbesuch',f"{s['cost_per_visit_chf']:g} CHF / {s['downtime_per_visit_h']:g} h",'Keine Offerte. Gemeinsamer Aufwand je Standort, nicht pro Server. Ausfall aller Server gleichzeitig wird für die Ausfallmarge angenommen.')
        own('cooling_allocation','Kostenverteilung',f"{s['cooling_budget_chf']:g} CHF Standortbudget / {len(result['servers'])} Server",
            'Gleiche rechnerische Kostenverteilung, keine zusätzlichen Einsätze. Keine Fahrtbündelung; mögliche Ausfallüberschneidungen werden nicht abgezogen.')
    add('l4_reference','L4-Vergleichswert, nicht ins ML übernommen','MTBF 2’147’604 bzw. 2’785’669 Stunden bei 35 °C',
        'Nur Referenz, nicht verwendet','NVIDIA L4 Product Brief, Tabelle 4',
        'Herstellerkennzahl für die beschriebene Serienkarte und Umgebungen. Keine gemessene Servicequote ganzer Server; kein Nachweis für einen Kühlplattenumbau. Nicht in der synthetischen Ereignisformel verwendet.',NVIDIA,False)
    return rows


def assumptions_markdown(rows):
    lines=['# Annahmen und Quellen der Serviceplanung','',
           'Die Liste unterscheidet Case-Vorgaben, übertragene Hersteller-/Studienangaben, Simulationsergebnisse und eigene Annahmen. „Keine empirische Quelle“ bedeutet: Der Wert wurde von uns gesetzt. Ein Quellenlink belegt nur den jeweils genannten Sachverhalt.','']
    for r in rows:
        source=f"[{r['source']}]({r['source_url']})" if r['source_url'] else r['source']
        lines += [f"## {r['parameter']}",'',f"**Wert:** {r['value']}",'',f"**Einordnung:** {r['category']}",'',f"**Quelle:** {source}",'',r['scope'],'']
    return '\n'.join(lines)
