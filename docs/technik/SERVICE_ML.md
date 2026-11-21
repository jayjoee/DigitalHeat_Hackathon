# ML Serviceplanung mit dem simulierten Case Betrieb

Die Serviceplanung verwendet einen trainierten Klassifikator für das tägliche Risiko
ungeplanten Servicebedarfs. Sie berechnet individuelle Serverintervalle, erwartete
Eingriffe, Ausfallstunden und Kosten. Die gemeinsame Kühlung hat einen eigenen Kalender.

**Die Trainingsdaten, Serviceereignisse, Sensorwerte und Wartungswirkungen sind noch
synthetisch. Die Simulation des Case-Betriebs macht daraus keinen realen L4-Wartungsnachweis.**

## Start

Mit Python 3.10 oder neuer und den Paketen aus `requirements/ml.txt`:

```sh
python3 -m venv .venv-ml
.venv-ml/bin/python -m pip install -r requirements/ml.txt
.venv-ml/bin/python start/service_start.py --demo --case --open
```

Bei bereits installierten Paketen: `python3 start/service_start.py --demo --case --open`.
Auf macOS startet `start/Service_Demo_starten.command` dieselbe gekoppelte Demo.
HTML, CSV und JSON entstehen unter `daten/ergebnisse/service_ml/`.
Es gibt keinen neuen Netzwerkdienst oder Zugriff auf die Hardware.
Ohne `--case` bleibt die bisherige reine Szenario-Demo verfügbar.

## Annahmen und Quellen im Bericht

Jede Auswertung enthält eine eigene Tabelle mit Wert, Einordnung, Quelle und
Geltungsgrenze. Die Werte werden aus der tatsächlichen Konfiguration des Laufs
übernommen, auch wenn Kosten oder Intervalle geändert wurden. Die Tabelle wird
zusätzlich als `Annahmen_und_Quellen.md`, `annahmen.csv` und im Ergebnis-JSON gespeichert.
Der Case wird für die gekoppelte Auswertung unter `quellen/CASE.md` mitgeliefert.

Case-Vorgaben, Simulationsergebnisse und übertragene Vergleichswerte sind getrennt
von unseren eigenen Annahmen gekennzeichnet. Frei gesetzte Kosten, Sensordaten und
Ereignisformeln tragen ausdrücklich den Hinweis **Keine empirische Quelle**.
Die vollständige synthetische Ereignisformel und die Erzeugung der Sensorwerte
sind enthalten. Die NVIDIA-MTBF wird nur als Referenz aufgeführt und kalibriert
weder die künstlichen Labels noch das trainierte Risikomodell.

## Case Betrieb pro Server

Der vorhandene Jahres-Scheduler wird mit acht Servern, genug flexiblen Aufträgen,
230 W Leerlauf, 10 W Standby und fünf Minuten Startzeit protokolliert. Die Steuerung
wird nicht verändert. Feste Serverpositionen bekommen stabile IDs; es wird keine
Verschleissrotation hinzugefügt. Pro Gerät und Tag entstehen getrennte Zähler für:

- Eingeschaltete Stunden einschliesslich Leerlauf und Startzeit.
- Äquivalente Rechenstunden unter Vollauslastung.
- Standby-Stunden, Startvorgänge und Serverstrom.

Die Summen stimmen mit der bestehenden Jahresrechnung überein: 717 Starts,
rund 34’511,6 Rechenstunden und 35’662,1 kWh Serverstrom für alle acht Server.
Die Geräte haben unterschiedliche Belastungen. Der Export ersetzt diese nicht
mit einem Flottenmittelwert. `case_betrieb_2025.csv` enthält die Tageswerte.

Das Referenzjahr wird für den Planungszeitraum nach Monat und Tag wiederholt.
Ein 29. Februar verwendet den 28. Februar. Das ist ein saisonales Szenario,
keine echte Wetter- oder Auftragsprognose. `geplanter_betrieb.csv` dokumentiert
jede Zuordnung. `--as-of YYYY-MM-DD` ändert den Beginn der Case-Demo.

Die Anfangszähler nehmen zwei Wiederholungen des Referenzjahrs und 730 Tage
Gerätealter an. Sensorwerte und bisheriges Servicealter bleiben Demowerte.
Die Profile wirken einseitig auf die Wartungsplanung. Erwartete Wartungsausfälle
werden noch nicht in Wärmebilanz oder Jobfristen zurückgerechnet.

## ML und Validierung

Ein HistGradientBoostingClassifier lernt die Wahrscheinlichkeit eines ungeplanten
Server-Servicebedarfs im nächsten vollständig beobachteten 24-Stunden-Fenster.
Eingaben sind Sensoren sowie getrennte Alters-, Betriebs-, Rechen- und Startzähler.
Die ID und das Datum sind keine Lernmerkmale.

60 % der historischen Server dienen zum Training, 20 % zur separaten Sigmoid-
Kalibrierung und 20 % zum Test. Ein Gerät erscheint in genau einer Gruppe.
Brier-Fehler und Log-Loss werden mit einem konstanten Trainingsgruppenrisiko
verglichen; kleiner ist besser. Average Precision und Ereignishäufigkeit werden
mitgespeichert. Diese Gruppentrennung ersetzt keine prospektive Validierung.

Das Training verwendet im Demo-Modus 120 künstliche Server mit je 540 Tageswerten.
Auch die Beziehungen zwischen Alter, Sensoren, Startvorgängen und Ereignissen sind
frei gesetzte Generatorannahmen. Das Modell lernt damit keine empirische L4-Ausfallrate.

Technische Grundlage: [Klassifikator](https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html)
und [separate Kalibrierung](https://scikit-learn.org/1.6/modules/generated/sklearn.calibration.CalibratedClassifierCV.html).

## Von Risiken zu Intervallen und Einsätzen

Ein diskretes Erneuerungsmodell führt die Verteilung des individuellen Servicealters
über den Planungszeitraum fort. So entstehen Erwartungswerte ohne Monte-Carlo-Rauschen.
Ein geplanter Eingriff erfolgt beim Erreichen des Intervalls. Ein ungeplanter
vollständiger Server-Service setzt nur den individuellen Server-Servicezähler zurück
und kann damit eine anstehende individuelle Routine ersetzen. Teilreparaturen erfüllen
diese Annahme nicht. Höchstens ein Servereingriff wird je Gerät und Tag gezählt.

Gerätealter, Betriebsstunden, Rechenstunden, Startzähler, ECC, SSD-Verschleiss,
Durchfluss, Pumpenstrom und gemeinsamer Kühlungskalender werden dadurch nicht
zurückgesetzt. Ein GPU-Tausch erledigt insbesondere keine Standortwartung.

Das Modell minimiert je Intervall die erwarteten Servicekosten und optional den
entgangenen Deckungsbeitrag während der Ausfallstunden. Bei numerisch gleichen
Kosten wird das längere erlaubte Intervall gewählt. Optimiert wird nur der
angegebene Zeitraum; ein Eingriff genau am exklusiven Enddatum zählt erst später.

```sh
python3 start/service_start.py --demo --case --intervals 60,90,180,365   --max-interval 365 --planned-cost 400 --unplanned-cost 900   --planned-hours 2 --unplanned-hours 12 --lost-margin 0
```

400/900 CHF, zwei/zwölf Stunden und die maximale Intervallgrenze sind Testannahmen.
Die Intervallgrenze muss den Vorgaben der gewählten Serverhardware entsprechen.
Nächste Routinetermine gelten, solange kein ungeplanter vollständiger Service
stattfindet. Bruchteile von Eingriffen sind Erwartungswerte, keine halben Besuche.

## Gemeinsame Kühlung

Der Standortkalender ist unabhängig von Servereingriffen. Standard sind 180 Tage,
600 CHF und zwei Stunden pro Kühlungsbesuch. Bei frisch gewarteter Kühlung entstehen
in 365 Tagen zwei feste Besuche und 1’200 CHF Standortbudget. Bei acht Servern sind
das rechnerisch 150 CHF Anteil je Server, keine zusätzlichen physischen Besuche.

CoolIT nennt typischerweise Wartungsbesuche alle sechs Monate. 180 Tage sind eine
Vergleichsnäherung, kein ausgewählter Herstellerplan; Preis und Dauer bleiben
unbelegt. [CoolIT Servicebeschreibung](https://www.coolitsystems.com/products-services/global-professional-services/)

```sh
python3 start/service_start.py --demo --case --cooling-interval 180   --cooling-age 0 --cooling-cost 600 --cooling-hours 2
```

`kuehlungskalender.json` enthält Termine und Kosten. Server-Reparaturen können diese
Termine nicht verlängern. Gemeinsame Ausfälle, Notfallfahrten, Reiseaufteilung und
Terminbündelung sind noch nicht modelliert. Die Summe individueller Servereingriffe
ist keine Zahl von Technikerfahrten. Bestehende Kostenpauschalen werden nicht verändert.

## Verbleibende Sensorannahmen

Die unbelegten täglichen Durchflussverluste, Pumpenstromsteigerungen und die
pauschale SSD-Alterung wurden aus der Fortschreibung entfernt. Ohne Messdaten
bleiben diese Werte konstant. Im Case-Szenario wird Chiptemperatur vereinfacht um
17 °C je Änderung des Lastanteils angepasst; bei ausgeschalteten Geräten gelten
Eintrittstemperatur plus 2 °C. Das ist keine gemessene Kühlplattenkennlinie.

Die Merkmale einer künftigen Entscheidung beschreiben jeweils die vorangegangene
Tagesexposition. Kumulierte Zähler steigen anhand der simulierten eingeschalteten
Stunden, Rechenstunden und Starts. Im ungekoppelten Szenario wird der bisherige
Einschaltanteil konstant fortgeschrieben, getrennt vom Rechenlastanteil.

Das zurückgesetzte Servicealter kann im ML das Risiko verändern. Dieser Zusammenhang
bleibt auf synthetischen Daten eine Szenarioannahme, keine gelernte kausale Wirkung
realer Wartung. Abweichungen vom Trainingsbereich werden im Bericht markiert.
Alle Ergebnisse bleiben manuell zu prüfen; es gibt keine automatische Sicherheitssteuerung.

## Daten importieren

```sh
python3 start/service_start.py --history historie.csv --fleet server.csv --open
```

Die Demo exportiert Beispiel-CSV-Dateien. Die Historie enthält eine Zeile pro Gerät
und Datum; die aktuelle Flotte genau eine Zeile je physischem Server.
Datenschema 2 erfordert ausdrücklich die getrennten Expositionsspalten.
Alte CSV-Dateien müssen mit echten beziehungsweise ausdrücklich simulierten Werten
ergänzt werden. Fehlende Messwerte werden nicht durch erfundene Normalwerte ersetzt.

| Spalte | Bedeutung |
|---|---|
| server_id | Stabile physische Geräte-ID |
| date | Datum YYYY-MM-DD |
| server_age_days | Kalenderalter in Tagen |
| operating_hours | Kumulierte eingeschaltete Stunden, nicht Last × Alter |
| compute_hours | Kumulierte äquivalente Rechenstunden, höchstens operating_hours |
| power_on_fraction | Eingeschalteter Zeitanteil der vorangegangenen 24 h, 0 bis 1 |
| load_fraction | Rechenlast während eingeschalteter Zeit, 0 bis 1 |
| starts_24h | Startvorgänge der vorangegangenen 24 h |
| starts_total | Kumulierte Startvorgänge |
| days_since_service | Ganze Tage seit individuellem vollständigem Server-Service |
| gpu_temp_c | Konsistente GPU-Temperaturstatistik, z. B. vorheriges Tagesmaximum, in °C |
| coolant_inlet_c | Kühlmitteleintrittstemperatur in °C |
| flow_lpm | Durchfluss in l/min |
| pump_current_a | Zugeordneter Pumpenstrom in A |
| ecc_errors_24h | Neue ECC-Ereignisse der vorangegangenen 24 h |
| ssd_wear_percent | Verbrauchte SSD-Lebensdauer in Prozent |
| unplanned_service_next_24h | Nur Historie: ungeplanter Server-Servicebedarf im Folgetag, 0 oder 1 |
| observed_24h | Nur Historie: vollständiges Ergebnisfenster, 0 oder 1 |

Unvollständige Zielfenster werden ausgeschlossen. Bei geplanter Intervention im
Zielfenster ebenfalls observed_24h=0 setzen, da unveränderter Betrieb nicht beobachtet
wurde. Keine erst nach einem Ereignis bekannten Messwerte als Eingaben verwenden.
Historische Zielfenster müssen vor dem aktuellen Flottenzustand enden.

Mindestens zwölf historische Server und je Gruppe fünf Ereignisse sowie fünf
ereignisfreie Tage sind technische Mindestprüfungen, keine Garantie ausreichender
Datengrundlage. Der Case-Modus ist explizit auf die synthetische Demo begrenzt.

## Prüfen

```sh
python3 -m unittest discover -s tests -p 'test_service*.py' -v
```

Geprüft werden bekannte Einsatzmengen, getrennte Zähler, identische Case-Bilanzen,
Kalenderzuordnung, Service-Reset, unabhängige Kühlungstermine, Kosten, unvollständige
Beobachtung und der tatsächliche Einfluss der Betriebsexposition auf die Risikoauswertung.
