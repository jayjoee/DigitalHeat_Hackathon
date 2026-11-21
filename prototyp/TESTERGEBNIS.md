# Prüfung der getrennten DigitalHeat-Plattform

Geprüft am 21. November 2026 auf macOS mit Python 3.12. Die Prüfung betrifft den lokalen Demonstrator im selben Ordner.

## Automatische Integrationstests

**12 Tests erfolgreich, Laufzeit rund 12 Sekunden.** Tatsächliche lokale HTTP-/HTTPS-Verbindungen mit temporären Zugangsdaten und zufälligen Ports.

1. Ende-zu-Ende-Textanalyse, Prüfsumme und Entfernen.
2. Fremde Herkunft, falscher Host und falscher Kunden-CSRF-Schlüssel abgewiesen.
3. Wärmebedarf ausgeschaltet: neu gesendeter Auftrag bleibt ohne aktive CPU-Zeit pausiert. Kundenaktion „Fortsetzen“ umgeht die globale Sperre nicht. Nach Freigabe wird der Auftrag beendet.
4. Serverhalter prüft Herkunft, Host, eigenen CSRF-Schlüssel und den booleschen Wärmebedarf.
5. Serverhalter-API enthält ausschliesslich freigegebene aggregierte Felder. Rollenfremde Schnittstellen und Skripte werden auf beiden Diensten abgewiesen.
6. Auftragspause, stabile aktive Zeit während der Pause, Fortsetzen und Abbruch.
7. Alle drei Pharma-Vorlagen bis zum Abschluss ausgeführt; Ergebnisstruktur und Eingabevalidierung geprüft.
8. Grenze von 30 gespeicherten Aufträgen und Ablauf abgeschlossener Aufträge.
9. Aktuelle Kundendateien werden ausgeliefert; Bearer-Token und unbekannte Dateipfade werden nicht ausgeliefert.
10. Nicht vertrauenswürdiges Zertifikat abgewiesen.
11. Eingabegrenzen, unzulässige Dauer und fehlende Texte beziehungsweise unerlaubte Vorlagen zurückgewiesen. Keine Schnittstelle zur Ausführung hochgeladener Programme.
12. Empfänger erfordert Token; die Testverbindung handelt TLS 1.3 aus.

Zusätzlich: Python-Syntaxprüfung und Syntaxprüfung beider JavaScript-Dateien.

## Bedienung im Browser

- Virtuelles Screening über die neue Vorlage gesendet. Das Ergebnis nennt ausdrücklich synthetisches Ranking, keine Docking-Berechnung und keine Bindungsaffinität.
- Auf der separaten Serverhalter-Seite Wärmebedarf ausgeschaltet.
- Cell-Painting-Auftrag mit 384 Demo-Bildern gesendet: bei 0 % pausiert. Nach Freigabe des Wärmebedarfs abgeschlossen.
- Literaturvorlage mit synthetischem Abstract gesendet und abgeschlossen.
- Serverhalter-Oberfläche zeigte nur Betriebszustand und Auftragszahlen; die drei Forschungsprojekttitel erschienen ausschliesslich im Pharma-Arbeitsbereich.
- Ergebnisdialog geöffnet und geschlossen. Ergebnisdarstellung verwendet Textknoten, keine Interpretation von Kundentext als HTML.
- Desktop-Ansichten visuell geprüft. Bei 390 CSS-Pixeln Breite hatten beide Dokumente keine horizontale Überbreite.
- Keine Warnungen oder Fehler in den geprüften Browser-Sitzungen. Temporäre Grössenvorgaben nach der Prüfung zurückgesetzt.

Screenshots der beiden aktuellen Desktop-Oberflächen liegen ausserhalb des Pakets als `DigitalHeat_Pharma.png` und `DigitalHeat_Serverhalter.png` vor.

## Grenzen der Prüfung

Alles lief auf einem physischen Rechner. Eine Übertragung zwischen zwei realen Geräten mit deren Firewall-Einstellungen muss im vorgesehenen Netzwerk noch getestet werden. Kein NVIDIA-/GPU-Test, kein echtes Docking, keine Bildanalyse, keine physische Heizungssteuerung oder Energiemessung. Kein Lasttest, keine vollständige Screenreader-/Kontrastprüfung und kein unabhängiges Sicherheitsaudit.

Die Trennung der Oberflächen schützt nicht gegen Administratorzugriff auf den Empfängerrechner. Es gibt noch keine individuellen Konten oder Mandantentrennung zwischen mehreren Pharma-Kunden. Nur öffentliche oder erfundene Testdaten verwenden.
