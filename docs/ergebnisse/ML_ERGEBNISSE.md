# ML-Vergleich – erste Ergebnisse

Berechnet am 21. November 2026. Zeitraum: 1. Juli bis 31. Dezember 2025, acht Referenzserver, identische endliche Alibaba-basierte Aufträge. Es handelt sich um eine Modellrechnung mit ungemessenen neuen Hardwareprofilen.

| Variante | Gesamtstrom inkl. Ersatzheizung | Fertige Aufträge | Fristen verpasst |
|---|---:|---:|---:|
| Regeln mit Verbrauchsmodell | 21564.47 kWh | 22436 | 0 |
| Sparsam ohne ML | 17284.75 kWh | 22432 | 0 |
| Sparsam mit ML | 17283.97 kWh | 22432 | 0 |

Der **zusätzliche ML-Effekt** wird nur zwischen den beiden sparsamen Varianten verglichen. Er beträgt 0.774 kWh beziehungsweise 0.00448 %. Das ist **kein belastbarer zusätzlicher Effizienznachweis für ML**. Die Profile sind ungemessen, und die ML-Energie ist nur geschätzt.

Die mittleren absoluten Wärme-Prognosefehler betragen 0.531 kWh mit ML und 0.593 kWh mit dem Vortagsvergleich. Eine bessere Prognose führt hier nur zu einer sehr kleinen Energieänderung: Viele Aufträge werden bereits wegen ihrer Fristen ausgeführt.

ML verändert die Auftragsverteilung in 149 von 4416 Stunden. Die beiden sparsamen Varianten liefern dieselbe vollendete Arbeitsmenge. Gegenüber der ersten Variante bleiben vier zusätzliche Aufträge am Periodenende offen; der Vergleich zwischen erster und sparsamen Varianten ist daher nicht exakt liefergleich. Offene Arbeit wird nicht als erledigt ausgegeben.

**Interpretation:** Unter diesen Annahmen liegen die grossen Hebel beim Betrieb und bei den Leistungsprofilen. Die ML-Struktur funktioniert, ihr zusätzlicher Effizienzvorteil muss erst mit echten Messdaten und weiteren Jahren/Standorten nachgewiesen werden.

ML wird mit Januar–Mai trainiert, mit Juni kalibriert und ab Juli ausgewertet. Der Prognosezielwert stammt aus der Case-Formel, nicht aus echten Häusern. Der Vergleich enthält Strom für die angenommene elektrische Ersatzheizung und eine Laufzeit-basierte Schätzung des ML-Stroms.

Der dargestellte finanzielle Periodenbeitrag ist **kein Jahresgewinn**. Vergütung wird auf die fertiggestellte Referenzarbeit normalisiert; tatsächliche Kundenabnahme ist eine Annahme.

Die Kurzfassung steht in `daten/ergebnisse/ml/zusammenfassung.json`. Alle Einzelwerte erzeugt `python3 start/ml_start.py --compute-only` lokal (`vergleich.json`, wegen der Grösse nicht im Repo); die Methode ist in `docs/technik/ML_SYSTEM.md` beschrieben.
