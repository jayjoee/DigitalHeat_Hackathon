# DigitalHeat – ML-Energieplanung

Stand: 21. November 2026. Lokale Erweiterung auf Basis von GitHub-Commit `2a01199`. Die Erweiterung ist im gemeinsamen Repository enthalten.

## Was funktioniert

Ein tatsächlich trainiertes Gradient-Boosting-Modell prognostiziert den Wärmebedarf der kommenden Stunden. Der Planer verwendet diese Vorhersagen, um das Ziel für den Wärmespeicher festzulegen. Der vorhandene Scheduler entscheidet weiterhin, welche Aufträge rechnen müssen oder warten können. Anschliessend werden echte Zahlen für das Modell berechnet: erledigte Arbeit, Strom, genutzte Wärme, Speicherverluste, Ersatzheizung und ein vereinfachter finanzieller Periodenbeitrag.

Die Oberfläche ist ein eigener Planungsbereich. Sie vermischt weder die Pharma- noch die Serverhalter-Oberfläche. Aufruf: `http://127.0.0.1:18100`. Sie steuert keine physische Heizung und keinen echten GPU-Server.

## Start

Python 3.10 oder neuer. Die neue ML-Erweiterung braucht nicht die vollständige Embedding-Umgebung aus `requirements/embedding_gepinnt.txt`.

```sh
python3 -m venv .venv-ml
.venv-ml/bin/python -m pip install -r requirements/ml.txt
.venv-ml/bin/python start/ml_start.py --open
```

Auf Windows die entsprechenden Programme unter `.venv-ml/Scripts/` verwenden. Auf macOS kann nach Einrichtung `start/ML_starten.command` gestartet werden. Der Dienst bindet nur an `127.0.0.1`. Kein externer Modellanbieter, kein API-Schlüssel und keine Übertragung der Berechnungsdaten an eine Cloud. Die erstmalige Paketinstallation braucht einen Internetzugang; die Berechnung nutzt die mitgelieferten Daten.

Standard: Juli bis Dezember 2025, acht Referenzserver. In der Oberfläche können Startdatum, Zeitraum, Serverzahl und mehrere Energieannahmen geändert werden. Für die Option „Juli bis Dezember“ den Start auf 1. Juli belassen. Ungültige Zeiträume werden abgewiesen. Es läuft höchstens ein Vergleich gleichzeitig.

Ohne Weboberfläche:

```sh
.venv-ml/bin/python start/ml_start.py --compute-only --days 184
.venv-ml/bin/python start/ml_start.py --compute-only --start 2025-10-01 --days 30
```

## Wo ML in der Rechnung sitzt

```text
Historische Daten -> echtes ML-Training -> Wärmeprognose für 1–6 Stunden
                                            |
                                            v
                         Ziel für den Wärmespeicher
                                            |
                                            v
                             vorhandener Scheduler
                                            |
                                            v
                     Rechenarbeit -> Strom und Wärme -> Kosten
```

Für jede Betriebsstunde wird ein neuer Plan gebildet. In beiden sparsamen Varianten ist die Planungsregel gleich: Der Speicher soll höchstens die prognostizierte Wärme der nächsten Stunden zuzüglich einer kalibrierten Reserve aufnehmen. Nur der Prognosewert unterscheidet sich.

### Drei Vergleichsläufe

1. **Heutige Regeln mit realistischem Verbrauchsmodell:** Standardtempo, Server eingeschaltet, ursprünglicher Speicherfüllansatz. Leerlauf und Nebenverbrauch werden zusätzlich erfasst. Das ist nicht die unveränderte historische Case-Rechnung.
2. **Sparsam ohne ML:** angenommener Sparmodus, bedarfsgerechtes Einschalten, Prognose nach dem entsprechenden Zeitpunkt des Vortags.
3. **Sparsam mit ML:** dieselben Energieprofile, Einschaltregeln und derselbe Planungsansatz wie Variante 2, aber mit gelerntem Wärmebedarf.

Der zusätzliche ML-Effekt ist ausschliesslich **Variante 2 minus Variante 3**. Der Unterschied zwischen 1 und 3 darf nicht vollständig als ML-Erfolg bezeichnet werden. Unterschiede unter 0,1 % werden in der Oberfläche als kein belastbarer zusätzlicher Effizienznachweis bezeichnet; diese Schwelle ist eine Darstellungsregel, kein statistischer Signifikanztest.

## Daten und zeitliche Trennung

- **Ziel:** Heiz- und Warmwasserbedarf aus dem bereits vorhandenen synthetischen Referenzhausprofil Basel 2025.
- **Wetter:** mitgelieferte ECMWF-Prognosen (`previous_day1`/`previous_day2`). Für jede Entscheidung wird nur ein Lauf verwendet, dessen angenommene Veröffentlichungszeit vor dem Entscheid liegt. Der bisherige konservative Veröffentlichungsverzug von acht Stunden bleibt eine Projektannahme.
- **Merkmale:** verfügbare Wetterprognose, Uhrzeit, Jahreszeit, vergangener Wärmebedarf und Vorhersagehorizont. Keine zukünftigen tatsächlichen Wärme- oder Temperaturwerte in den Merkmalen.
- **Training:** Januar bis Mai 2025. `HistGradientBoostingRegressor`, feste Zufallssaat, keine zufällig gemischte Validierung.
- **Kalibrierung:** Juni 2025. Für beide Prognoseverfahren wird jeweils eine nicht negative Reserve aus dem 90%-Quantil ihrer Prognosefehler ermittelt. Das garantiert keine 90%-Abdeckung auf späteren Daten.
- **Auswertung:** ausschliesslich Juli bis Dezember. Aktueller Stundenbedarf gilt als beobachtet; der Blick in die Zukunft erfolgt über die Prognose.

Die ML-Qualität wird als mittlerer absoluter Prognosefehler (MAE, kWh Wärme pro Stundenprognose) angegeben. Die synthetische Case-Formel und nur ein Wetterjahr begrenzen die Aussagekraft erheblich. Die Prognose ersetzt keine Messung eines echten Gebäudes.

## Arbeit, Zeit und Strom sind getrennt

Eine Arbeitseinheit entspricht der Rechenarbeit einer Standard-Referenzserverstunde. Die vorhandenen Jobmengen werden aus der früheren 1-kW-Skalierung übernommen. Das ist keine neue Messung auf einer L4-GPU und kein echter Pharma-Benchmark.

Der bestehende Scheduler `kern.entscheide()` wird über einen Einheitenadapter weiterverwendet: Seine historischen Feldnamen `rest_kwh` und `strom_kwh` bedeuten an dieser Schnittstelle Referenzarbeit. Physikalische Energie wird getrennt berechnet und ausschliesslich in den Energiefeldern verbucht. Fristen werden auf Basis der verbleibenden Arbeit und des Tempos geprüft.

Die drei Varianten erhalten dieselbe endliche, Alibaba-basierte Auftragsliste mit gleicher Zufallssaat, Arbeitsmenge und Fristen. Es gibt keinen unbegrenzten Spot-Nachschub. Eine SHA-256-Prüfsumme identifiziert die Eingangsaufträge. Nicht abgeschlossene Aufträge am Periodenende bleiben als offen sichtbar. Deshalb kann Variante 1 eine andere vollendete Arbeitsmenge haben als 2/3. Die Oberfläche prüft die Lieferparität für den eigentlichen ML-Vergleich 2 gegen 3 ausdrücklich.

## Neue Energieannahmen

| Parameter | Standard | Einordnung |
|---|---:|---|
| Server | 8 | Projekt-Referenz |
| Aktive Standardleistung | 1 kW | Case |
| Sparleistung / Tempo | 0,75 kW / 80 % | Ungemessene Testannahme |
| Leerlauf | 0,23 kW je eingeschaltetem Server | Szenarioannahme |
| Ausgeschaltet | 0,005 kW je Server | Szenarioannahme |
| Start | 2 Minuten bei 0,60 kW | Szenarioannahme, reduziert verfügbare Rechenzeit |
| Pumpe | 0,03 kW bei Wärmeproduktion | Szenarioannahme |
| Wärmerückgewinnung | 80 % der aktiven/Leerlauf-/Startenergie | Case vereinfacht; Aus-Verbrauch nicht gutgeschrieben |
| Speicher | 35 kWh | Case |
| Speicherverlust | 0,1 % je Stunde | Szenarioannahme |
| Ersatzheizung | elektrisch, COP 2,5 | Vergleichsannahme; kein Beleg zur realen Pilot-Heizung |
| ML-Rechner | 0,10 kW während gemessener Softwarelaufzeit | Energieabschätzung, keine Steckdosenmessung |

Der Sparmodus wirkt im ersten System auf alle Jobtypen mit demselben angenommenen Faktor. Spätere echte Batching-, Präzisions- und GPU-Benchmarks müssen je Auftragstyp eigene Profile liefern. Temperaturabhängige Wärmerückgewinnung, Leitungsverluste, Starts unterhalb der Stundenskala und Migrationen im erweiterten Mehrstandortmodell sind noch nicht umgesetzt.

### Bilanz je Stunde

- Serverstrom = aktive Energie + Bereitschaft + ausgeschaltete Geräte + Startenergie.
- Gesamtstrom = Serverstrom + Pumpenstrom + ML-Strom + Strom der Ersatzheizung.
- Nutzbare Wärme = Rückgewinnungsanteil der aktiven, Bereitschafts- und Startenergie.
- Speicherstand = vorheriger Stand − Speicherverlust − Entnahme + Ladung.
- Fehlende Wärme wird vollständig als Ersatzheizung erfasst; sie verschwindet nicht aus der Rechnung.

Wärme-, Arbeits- und Kapazitätsbilanzen werden im Programm geprüft. Der ML-Strom enthält Training und Prognoseberechnungen. Die Laufzeit wird gemessen und mit der angenommenen Hostleistung multipliziert; physisch gemessene Energie kann später diese Schätzung ersetzen. Hilfsenergie wird hier konservativ nicht als nutzbare Heizwärme angerechnet.

## Kosten und Erlöse

`src/wirtschaft.py` enthält zusätzlich `variable_bilanz()`. Sie nimmt tatsächliche Modell-kWh und verkaufte Referenz-GPU-Stunden getrennt entgegen. Leerlauf erzeugt keine verkauften Stunden. Für den Vergleich wird der Erlös auf dieselbe vollendete Referenzarbeit normalisiert: Langsameres Rechnen erhöht den Erlös nicht automatisch.

Das Ergebnis ist ein **Periodenbeitrag vor Fixkosten, Investition und Steuern**, kein Jahresgewinn oder Kapitalwert. Es wird angenommen, dass alle fertiggestellte Referenzarbeit verkauft wird und alle Karten eines Referenzservers genutzt werden. Der Preis wird aus dem bisherigen Fest-/Spot-Mix abgeleitet. Eine reale Nachfrage oder ein entsprechender Vertrag ist damit nicht nachgewiesen.

Die System-Stromkosten enthalten auch die Ersatzheizung. Der Unternehmensbeitrag zieht dagegen den Strom am Rechenstandort inklusive Pumpe und ML ab; Ersatzheizung ist in diesem Vergleich beim Gebäude verortet. Diese Abgrenzung ist vor einem realen Vertragsmodell anzupassen. Der neue Serverbetriebsansatz des gemeinsamen Repositorys bleibt erhalten. Die historische Case-Referenz wird durch Regressionstests geprüft. Der separate ML-Vergleich verwendet sein eigenes transparentes Verbrauchsprofil; Ergebnisse der beiden Betriebsmodelle nicht ungeprüft gleichsetzen.

## Dateien und Integration

- `src/ml_system/forecast.py`: Training, zeitlich verfügbare Merkmale, Prognose und Vergleich mit Vortag.
- `src/ml_system/simulation.py`: Energiezustände, Arbeit, Speicher, Wärme- und Arbeitsbilanz.
- `src/ml_system/experiment.py`: identische Vergleichsläufe und Exporte.
- `src/ml_system/config.py`: validierte Szenarioannahmen.
- `start/ml_start.py`: lokale Bedienoberfläche und Kommandozeile.
- `dashboard/ml/`: eigenständiger Planungsbereich, auch als gespeicherte Ansicht lesbar.
- `daten/ergebnisse/ml/`: JSON sowie tägliche und stündliche CSV-Dateien.
- `tests/test_ml_system.py`: zwölf zusätzliche Tests.

Das bisherige Dashboard besitzt einen Link zum gespeicherten Vergleich. Das neue ML-System verändert den bisherigen Flottenrouter, die Day-ahead-Zusage und die echte Embedding-Live-Demo nicht. Eine Übernahme der ML-Entscheidungen in diese Mehrstandort-/Live-Systeme ist ein eigener nächster Integrationsschritt.

## Prüfung

```sh
.venv-ml/bin/python -m unittest discover -s tests -v
```

34 Tests bestanden: 22 bestehende Modelltests und zwölf neue Tests für Trainingsgrenzen, verfügbare Wetterläufe, Auswirkung der ML-Eingaben auf die Prognose, fehlenden Zugriff auf zukünftige Zielwerte, Energie-/Arbeitslogik, Erlösabgrenzung, Startverzögerung und lokale Schnittstellengrenzen. Ausserdem besitzt die Simulation Laufzeitprüfungen für Wärme, Arbeit und Kapazität.

Der lokale Webdienst prüft Host, Browserherkunft und einen CSRF-Schlüssel für Neuberechnungen. Er liefert nur explizit freigegebene Dateien aus. Keine Anmeldung für mehrere Benutzer und keine öffentliche Produktionsbereitstellung.

## Fachliche Grundlagen

- [scikit-learn: Zeitreihen und Gradient Boosting](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html)
- [Google: Prognose und Optimierung flexibler Rechenlast](https://arxiv.org/abs/2106.11750)
- [DOE: Energieeffiziente Rechenzentren](https://www.energy.gov/sites/default/files/2024-07/best-practice-guide-data-center-design.pdf)
- [Zeus: Messung und Optimierung von ML-Energie](https://ml.energy/zeus/)

Zeus und GPU-Power-Capping sind hier noch nicht angeschlossen. Das erste System stellt die Modell- und Vergleichsstruktur bereit, in die ihre späteren Messwerte eingehen können.

## Gespeicherte Referenzauswertung

`daten/ergebnisse/ml/zusammenfassung.json` und `tage.csv` enthalten die kompakte Referenz. Die vollständigen Stundenwerte `vergleich.json` und `stunden.csv` werden bei einer Neuberechnung erzeugt und nicht mit Git versioniert. Das Messwerkzeug für reale Laptopprofile liegt unter `messwerkzeug/`.
