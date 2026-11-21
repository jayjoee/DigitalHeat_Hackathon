# ML-Serviceplanung pro physischem Server

Diese Ergänzung rechnet Serviceintervalle, geplante und ungeplante Eingriffe,
Ausfallstunden und Kosten pro Server. Zielhardware: Server mit Kühlplatten,
geschlossenem Kühlmittelkreislauf und Wärmetauscher zur Heizung.

**Es gibt noch keine echten L4-/Kühlplatten-Servicehistorien im Projekt. Der
Demo-Modus trainiert auf künstlichen Daten. Seine Zahlen sind Szenarien und dürfen
nicht als reale Wartungsprognosen oder Einsparnachweise verkauft werden.**

## Start

Im Projektordner, mit Python 3.10 oder neuer und den ML-Abhängigkeiten:

```sh
python3 -m venv .venv-ml
.venv-ml/bin/python -m pip install -r requirements-ml.txt
.venv-ml/bin/python service_start.py --demo --open
```

Falls die Pakete bereits installiert sind: `python3 service_start.py --demo --open`.
Auf macOS lässt sich die Demo auch mit `Service_Demo_starten.command` starten.
Das Programm erzeugt eine lokal lesbare HTML-Auswertung, JSON und CSV unter
`daten/ergebnisse/service_ml/`. Es startet keinen Netzwerkdienst und steuert keine
Hardware. Eine Eingabe ohne `--demo` oder vollständige CSV-Dateien wird abgelehnt.

## Was das ML macht

Ein `HistGradientBoostingClassifier` lernt für ein vollständig beobachtetes
24-Stunden-Fenster die Wahrscheinlichkeit eines **ungeplanten Servicebedarfs**.
Temperatur, Last, Durchfluss, Pumpenstrom, Gerätealter, Betriebsstunden,
Servicealter, ECC-Signal und SSD-Verschleiss sind die Eingaben.

60 % der historischen Server dienen zum Training, 20 % zur separaten
Sigmoid-Kalibrierung und 20 % zum Test. Ein Server erscheint nur in einer Gruppe.
ID und Datum sind keine Lernmerkmale. Ein Zufallssplit einzelner Tageszeilen würde
denselben Server in Training und Test bringen und wird deshalb vermieden.
Diese Gruppentrennung ersetzt keine spätere prospektive zeitliche Validierung.

Das Testprotokoll vergleicht Brier-Fehler und Log-Loss mit einem konstanten
Ereignisrisiko aus der Trainingsgruppe. Weniger Fehler ist besser. Average Precision
und Ereignishäufigkeit werden ebenfalls gespeichert. Eine Verbesserung auf
künstlichen Daten ist kein Hardware-Nachweis und keine garantierte Erkennung.

Die ML-API und Kalibrierung folgen den verwendeten scikit-learn-1.6-Schnittstellen:
[Klassifikator](https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html),
[Kalibrierung und FrozenEstimator](https://scikit-learn.org/1.6/modules/generated/sklearn.calibration.CalibratedClassifierCV.html).

## Von Risiko zu Serviceeinsätzen

Das ML liefert tägliche Risiken. Ein diskretes Erneuerungsmodell führt danach für
jeden möglichen Serviceabstand die Wahrscheinlichkeitsverteilung des Servicealters
über den Planungszeitraum fort. Es berechnet Erwartungswerte ohne Monte-Carlo-Rauschen.

- Ein geplanter Vollservice erfolgt, sobald das Servicealter das Intervall erreicht.
- Ein ungeplanter Eingriff setzt den Servicezähler zurück und ersetzt damit den
  anstehenden Routineeingriff. Dafür wird vorausgesetzt, dass er den vollständigen
  vorgesehenen Service beinhaltet. Reine Teilreparaturen dürfen real nicht einfach
  den gesamten Servicezähler zurücksetzen.
- Pro Server und Tag wird höchstens ein Eingriff gezählt. An einem Tag mit geplantem
  Service wird kein weiterer ungeplanter Eingriff modelliert.
- Gerätealter, ECC-Signal und SSD-Verschleiss werden durch einen Kühlungsservice
  nicht auf Neuzustand gesetzt.
- Der Planungszeitraum beginnt am aktuellen Serverdatum und schliesst den Tag nach
  `--days` aus. Ein genau am Enddatum fälliger Eingriff zählt erst im nächsten Zeitraum.
- Der nächste Routinetermin gilt nur, solange kein ungeplanter Vollservice dazwischenkommt.

Der Vorschlag minimiert unter den zulässigen Kandidaten:

```
geplante Eingriffe × geplanter Preis
+ ungeplante Eingriffe × ungeplanter Preis
+ erwartete Ausfallstunden × entgangener Deckungsbeitrag je Stunde
```

Alle Preise sind frei veränderbare Testannahmen. Standard: 400 CHF geplant,
900 CHF ungeplant, zwei bzw. zwölf Stunden Ausfall, keine automatisch angenommene
entgangene Marge. Nicht enthalten sind pauschal GPU-Ersatz, gemeinsame Hydraulik,
Monitoring-/ML-Betrieb oder Finanzierung. Kostenobergrenzen sind keine Herstellervorgabe.

```sh
python3 service_start.py --demo --intervals 60,90,180,365 \
  --max-interval 365 --planned-cost 400 --unplanned-cost 900 \
  --planned-hours 2 --unplanned-hours 12 --lost-margin 0
```

Die maximale Zeit zwischen Services ist eine vom Betreiber einzutragende Grenze.
Herstellerauflagen können kürzere Intervalle verlangen. Das Modell darf sie nicht
verlängern. Kein Service ohne zwingenden Anlass und kein Kalenderintervall allein
werden als erwiesen optimal vorausgesetzt.
Bei numerisch gleichen Kosten wird das längere zulässige Intervall gewählt.
Optimiert wird der eingegebene endliche Zeitraum, nicht eine unbegrenzte Lebensdauer.

## Zentrale ungemessene Annahme: Wirkung der Wartung

Die Fortschreibung verändert gegenüber dem aktuellen Messpunkt je zusätzlichem
Tag seit dem Service die Chiptemperatur um +0,033 °C, den Durchfluss um −0,004 l/min
und den Pumpenstrom um +0,001 A. Ein Vollservice setzt diesen angenommenen Anteil
zurück. Last und Kühlmitteleintrittstemperatur bleiben im Szenario konstant;
SSD-Verschleiss steigt um 1/70 Prozentpunkt pro Tag. Werte werden an den Modellgrenzen
begrenzt. Diese Koeffizienten stehen auch im JSON.

**Diese Wirkungen sind nicht aus Daten gelernt und nicht durch die bisherigen
Wärme- oder Laptopmessungen belegt.** Das ML lernt das bedingte Ereignisrisiko;
die Wirkung eines geänderten Wartungsplans ist eine zusätzliche Szenarioannahme.
Reale Nutzung benötigt validierte Zustandsübergänge, Wartungsbefunde und passende
Fehlerklassen. Die Prognoseintervalle im Bericht sind keine Konfidenzintervalle.

## Echte Daten importieren

```sh
python3 service_start.py --history historie.csv --fleet server.csv --open
```

Die Demo exportiert `beispiel_historie.csv` und `beispiel_server.csv` als Vorlagen.
Die Historie enthält eine Zeile pro Server und Tag, jeweils aus vor dem Zielereignis
bekannten Messwerten. Für die aktuelle Flotte gilt genau eine Zeile pro physischem
Server; ein geteilter 16-GPU-Host darf nicht als zwei unabhängig wartbare Server zählen.

| Spalte | Bedeutung / Einheit |
|---|---|
| `server_id` | Stabile physische Geräte-ID |
| `date` | Datum des Messpunkts, YYYY-MM-DD |
| `server_age_days` | Alter des Geräts in Tagen |
| `operating_hours` | Kumulierte Betriebsstunden |
| `days_since_service` | Ganze Tage seit letztem vollständigem Service |
| `load_fraction` | Rechenlast 0 bis 1 |
| `gpu_temp_c` | Definierte GPU-Temperaturstatistik in °C, z. B. Tagesmaximum |
| `coolant_inlet_c` | Kühlmitteleintrittstemperatur in °C |
| `flow_lpm` | Kühlmitteldurchfluss in l/min |
| `pump_current_a` | Zugeordneter Pumpenstrom in Ampere |
| `ecc_errors_24h` | Neu beobachtete ECC-Ereignisse der vorangegangenen 24 h |
| `ssd_wear_percent` | Verbrauchte SSD-Lebensdauer in Prozent |
| `unplanned_service_next_24h` | Nur Historie: 1 bei ungeplantem Servicebedarf im folgenden Tag, sonst 0 |
| `observed_24h` | Nur Historie: 1 bei vollständig beobachtetem Ergebnisfenster, sonst 0 |

Unvollständige Ergebnisfenster werden ausgeschlossen, nicht als ereignisfrei
gezählt. Auch bei einem geplanten Service innerhalb des Ergebnisfensters ist
`observed_24h=0` zu setzen, da der unveränderte Betrieb nicht beobachtet wurde.
Die Definition des Ereignisses und die Aggregation der Sensoren müssen konsistent
sein. Nur zuvor bekannte Messwerte verwenden; keine nach dem Ausfall gemessenen
Temperaturen in die Eingabe desselben Zielereignisses schreiben.

Mindestens zwölf historische Server und in jeder der drei Gruppen mindestens fünf
Ereignisse sowie fünf ereignisfreie Tage sind technisch erforderlich. Das ist eine
Mindestprüfung, keine Aussage über ausreichende Datenqualität. Unbekannte Werte
werden nicht still durch erfundene Normalwerte ersetzt. Historische Zielfenster
müssen vor dem aktuellen Flottenzustand enden.

## Betriebsgrenzen und Anschluss an DigitalHeat

Der Bericht zählt **Servereingriffe, nicht Technikerfahrten**. Mehrere Server können
bei einer gemeinsamen Fahrt gewartet werden. Gemeinsame Pumpe, Wärmetauscher und
Standortwartung benötigen ein zusätzliches Standortmodell; ihre Ausfälle dürfen
nicht achtmal als unabhängige Serverfehler gezählt werden.

Eine aktuelle Eingabe ausserhalb des Trainingsbereichs wird markiert. Eine
Chiptemperatur ab 90 °C oder fehlender Durchfluss erzeugt zusätzlich einen
Szenario-Prüfhinweis. Diese Testschwelle ist keine L4-Herstellergrenze und kein
Schutzsystem. Zukünftige Sensorzustände können ebenfalls ausserhalb der bislang
beobachteten Verteilung liegen. Jede Empfehlung bleibt manuell zu prüfen.

Die bestehende Unternehmensrechnung wird absichtlich nicht automatisch verändert.
Nach Validierung können erwartete Services deren bisherige Servicepauschale
ersetzen. Sie dürfen nicht zusätzlich zu denselben bestehenden Wartungskosten
aufgeschlagen werden. Eine spätere Scheduler-Anbindung könnte vor einer Wartung
neue Aufträge sperren und laufende Arbeit kontrolliert verlagern; das ist hier
noch nicht implementiert.

## Prüfen

```sh
python3 -m unittest discover -s tests -p test_service_ml.py -v
```

Die Tests prüfen analytisch bekannte Einsatzmengen, Service-Reset, Kosten,
Wahrscheinlichkeitsgrenzen, fehlende Messwerte, unvollständige Beobachtung,
getrennte Servergruppen und den tatsächlichen Einfluss des ML-Risikos auf die Planung.
