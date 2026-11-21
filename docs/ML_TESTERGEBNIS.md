# Prüfung der ML-Erweiterung

21. November 2026, macOS, Python 3.12, scikit-learn 1.6.1.

## Automatisch

34 Tests bestanden, letzter Gesamtlauf rund 10 Sekunden: 22 bestehende Scheduler-/Flotten-/Zusage-/Wirtschaftstests plus zwölf neue ML-, Energie- und Schnittstellentests. Insbesondere bestehen die unveränderten Referenzbilanzen und Stunden-Hashwerte weiterhin.

Die neuen Tests prüfen zeitliche Trennung, Wetterverfügbarkeit, tatsächliche Reaktion des gelernten Modells auf Prognoseeingaben, Unabhängigkeit von zukünftigen Beobachtungen, valide Energieprofile, identische Ergebnisse bei identischen Prognosen, Leerlauf ohne Umsatz, Abschalten, Ersatzheizung, Startverzögerung und lokale Zugriffs-/Eingabegrenzen.

Zusätzliche Laufzeitprüfungen in jeder Stunde: Wärmebilanz, Speichergrenzen, Rechenkapazität und Gesamtarbeitsbilanz. Python- und JavaScript-Syntax geprüft.

## Im Browser

- Vollständiger Halbjahresvergleich geladen: 4'416 Stunden, 22'436 identische Eingangsaufträge.
- Zeitraum über die Oberfläche auf sieben Tage geändert und neu berechnet.
- Sparleistung auf 0,70 kW geändert und neu berechnet; Änderung erscheint in den Ergebnissen und der gespeicherten Konfiguration.
- Anschliessend vollständigen Halbjahresvergleich mit Standardprofil 0,75 kW wiederhergestellt.
- Kleine Darstellung mit 390 CSS-Pixeln geprüft: Dokumentbreite 390, keine horizontale Seitenüberbreite. Vergleichstabelle besitzt einen eigenen horizontalen Scrollbereich.

Keine Browserfehler oder Warnungen in der geprüften Sitzung. Temporäre Bildschirmgrössenvorgabe nach dem Test zurückgesetzt.

## Grenzen

Kein GPU-/L4-Benchmark, kein echtes Pharma-Modell, keine physische Heizungssteuerung. Neue Energieparameter sind Szenarioannahmen. ML-Strom ist aus Softwarelaufzeit und angenommener Hostleistung geschätzt. Die Prüfung bestätigt die Rechen- und Bedienlogik, keine reale Energieeinsparung oder Produktionssicherheit.
