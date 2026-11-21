# Prüfung der Gesamtdemo

21. November 2026, vorhandener Apple-M1-Pro-Rechner.

- 38 automatische Tests bestanden. Die Jahresbilanz entspricht unverändert der gespeicherten Referenz.
- Im Browser wurde ein tatsächlicher CPU-Auftrag gestartet und im Winter-/Sommerablauf angezeigt. Ein angehaltener Lauf speicherte seinen Checkpoint.
- Ein separater vollständiger Prüflauf absolvierte alle drei Tage mit 0,25 Sekunden je Modellstunde: 1152 Texte tatsächlich verarbeitet, 33 bestätigte Pausen ohne Checkpoint-Fortschritt, regulärer Abschluss und gespeicherter Checkpoint.
- Nachweis: `messungen/gesamtdemo_nachweis/demo.json`. Der echte Worker-Checkpoint liegt daneben; grosse Vektormatrizen bleiben lokal.
- Die Gesamtdemo benötigt kein sudo und keine Energiemessung. Wärme und Serverplätze sind simuliert; die Textverarbeitung und Prozesspausen sind echt.

Die Prüfung bestätigt den Funktionsablauf, keine reale Wärmeerzeugung eines NVIDIA-Servers, keine Pharma-Sicherheit und keinen wirtschaftlichen Produktivbetrieb.

Die Oberflächenprüfung ergab keine Browserwarnungen oder -fehler. Bei 390 CSS-Pixeln Breite war das Dokument ebenfalls 390 Pixel breit; temporäre Grössenvorgaben wurden zurückgesetzt.
