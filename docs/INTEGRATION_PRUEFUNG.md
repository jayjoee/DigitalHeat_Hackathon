# Prüfung der gemeinsamen Version

21. November 2026. Zusammenführung auf Basis von `1f5db12` einschliesslich Serverbetrieb und Blister-Demo.

## Automatische Prüfungen

- 46 Modelltests bestanden: bisherige Jahres-/Flotten-/Zusage-/Wirtschaftstests einschliesslich der neuen Serverzustände, plus ML- und Gesamtdemo-Prüfungen.
- 12 Tests des Pharma-/Serverhalter-Prototyps bestanden, einschliesslich tatsächlicher lokaler TLS-Verbindungen.
- 8 Tests des Messwerkzeugs bestanden, einschliesslich Abschluss ohne zweite sudo-Anmeldung und unbekannter statt erfundener Energiewerte.

Insgesamt **66 Tests bestanden**. Zusätzlich wurden Python-, JavaScript- und Startskript-Syntax sowie die Patch-Formatierung geprüft.

## Vollständige Funktionsläufe

- Der integrierte ML-Vergleich wurde über 4'416 Stunden Juli–Dezember erneut ausgeführt. Eingangsaufträge und vollendete Arbeitsmenge stimmen mit der Referenz überein; der zusätzliche ML-Effekt bleibt sehr klein.
- Ein vollständiger beschleunigter Echtprozess-Lauf aller drei Demo-Tage verarbeitete 576 Texte und bestätigte 33 Pausen ohne Checkpoint-Fortschritt. Der Worker beendete den Lauf regulär mit Checkpoint.
- Der bestehende Serverbetrieb und der Blister-Code wurden unverändert aus dem neuesten gemeinsamen Stand übernommen.

## Grenzen

Diese Prüfungen bestätigen Softwareabläufe und Modellkonsistenz. Sie bestätigen weder reale NVIDIA-L4-Effizienz noch eine echte Heizungsinstallation, Kundenabnahme oder Pharma-Produktionssicherheit. Die neue Blister-Demo besitzt in dieser Zusammenführung keine zusätzliche Prüfung über zwei physische Geräte.

Zugangsdaten, virtuelle Umgebungen, grosse Vektormatrizen und neue Laufzeitordner werden nicht veröffentlicht. Kompakte Ergebnisse und die neue Laptop-Chipmessung sind als Referenzen enthalten.
