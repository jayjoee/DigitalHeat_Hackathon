# DigitalHeat – Messung auf dem vorhandenen Rechner

Vorbereitet für den vorhandenen MacBook Pro mit Apple M1 Pro, acht CPU-Kernen und 16 GB RAM. Es wird der echte, bereits im Projekt verwendete Text-Embedding-Auftrag ausgeführt: `BAAI/bge-small-en-v1.5`, FastEmbed/ONNX auf der CPU, öffentliche AG-News-Texte.

## Jetzt starten

Nach der Einrichtung sucht der Start eine FastEmbed-Umgebung im Messwerkzeug oder im Repository-Stamm. Auf dem ursprünglichen M1-Pro-Rechner kann er zusätzlich die bestehende Desktop-Projektumgebung verwenden. Das Modell muss lokal zwischengespeichert sein; Einrichtung siehe unten.

- **`Start_ohne_Strommessung.command`**: Laufzeit und numerischen Ergebnisvergleich messen.
- **`Start_mit_Chipmessung.command`**: zusätzlich macOS-Leistungsschätzungen erfassen. Im Terminal fragt `sudo` nach dem Mac-Passwort. Das Passwort selbst im Terminal eingeben.

Ein Doppelklick startet jeweils den längeren Vergleich mit 2'048 Texten je Durchlauf und drei Wiederholungen. Je nach Rechnerlast dauert das einige Minuten. Die Ergebnisse erscheinen in einem neuen Ordner unter `laeufe/`. Einen laufenden Messablauf mit `Ctrl+C` beenden.

Der vollständige Referenzlauf mit neun Durchläufen ist unter `../messungen/vergleich_2026-11-21/BERICHT.md` dokumentiert. Die Abschlusslogik nutzt einen beim Start berechtigten Helfer und ein Stoppsignal; eine erneute sudo-Anmeldung nach einem langen Lauf ist nicht nötig. Es werden keine macOS-Energieeinstellungen geändert und keine anderen Programme beendet.

## Drei Varianten

| Variante | CPU-Threads | Paketgrösse |
|---|---:|---:|
| Standard | 6 | 16 Texte |
| Weniger CPU-Threads | 2 | 16 Texte |
| Grössere Verarbeitungspakete | 6 | 64 Texte |

Weniger Threads ist ein Softwarevergleich auf der CPU. Er entspricht weder einem GPU-Power-Limit noch einer garantierten Ausführung auf Effizienzkernen. Grössere Pakete testen Batching; das Abschalten ungenutzter Server lässt sich auf diesem einzelnen Laptop damit nicht messen. Der Laptop wird nicht ausgeschaltet oder in einen anderen Energiemodus versetzt.

Jede Variante verarbeitet exakt dieselben Eingabetexte mit demselben Modell. Sie läuft in einem eigenen Prozess. Die erste Variante dient als Referenz; ab der zweiten Wiederholung wird die Reihenfolge mit fester Zufallssaat gemischt. Der Ablauf macht zwischen Versuchen kurze Pausen. Das kontrolliert nicht die Temperatur vollständig; für belastbare Messungen längere Abkühlphasen und mehrere Durchläufe verwenden.

## Was wird gemessen?

- **Modellladezeit**, Aufwärmphase, reine Rechenzeit und gesamte Prozesslaufzeit getrennt.
- Texte pro Sekunde, Prozess-CPU-Zeit, Python-/Bibliotheksversionen und Eingabe-Prüfsumme.
- Numerische Ergebnisähnlichkeit durch Kosinusvergleich und maximale absolute Abweichung der Vektoren.
- Optional: über das Zeitfenster integrierte macOS-Schätzungen für CPU, GPU und ANE. Der kombinierte Summenwert wird nicht noch einmal addiert.
- Optional: externe Steckdosen-Energiemesswerte für den gesamten Prozess, sofern sie zu genau demselben Zeitfenster gehören.

**Keine angenommene Wattzahl wird als Messwert eingesetzt.** Ohne Leistungsdaten steht Energie auf „Nicht gemessen“. Fehlende Samples und unzureichende Abdeckung liefern ebenfalls keinen scheinbar vollständigen Energiewert. Ab 90 % Zeitabdeckung wird eine Chip-Energieschätzung angegeben; die Abdeckung bleibt im JSON sichtbar. Messfenster unter zehn Sekunden werden zusätzlich als kurz markiert. Zeitstempelauflösung und Sampling begrenzen die Genauigkeit kurzer Fenster.

`powermetrics` liefert geschätzte Leistungswerte einzelner Chipbereiche. Das ist keine vollständige Steckdosenmessung. Display, Netzteilverluste und weitere Verbraucher fehlen; andere Programme können die Werte beeinflussen. Die Schätzungen sind für Vergleiche auf demselben Gerät gedacht und dürfen nicht direkt auf einen NVIDIA-Server übertragen werden.

„Numerisch ähnlich“ bedeutet minimale Kosinusähnlichkeit von mindestens 0,999. Es ist keine wissenschaftliche, medizinische oder nachgelagerte Retrieval-Qualitätsvalidierung. Die maximale absolute Abweichung wird ebenfalls gespeichert.

## Erster Funktionstest

Ein kurzer Test mit 256 Texten und einer Wiederholung wurde tatsächlich ausgeführt:

| Variante | Reine Rechenzeit | Numerisch ähnlich | Energie |
|---|---:|---|---|
| Standard | 3,537 s | Ja | Nicht gemessen |
| Weniger Threads | 7,954 s | Ja | Nicht gemessen |
| Grössere Pakete | 5,045 s | Ja | Nicht gemessen |

Das bestätigt die Funktion. Eine Wiederholung und kurze Fenster reichen nicht für eine belastbare Rangfolge. Insbesondere zeigt der Test **keine Energieeinsparung**. Weniger Threads beziehungsweise grössere Pakete waren hier langsamer.

Die vollständige neuere Messreihe steht unter `../messungen/vergleich_2026-11-21/BERICHT.md`. Die acht automatischen Tests prüfen zusätzlich den Energieparser, Zeitfenster, fehlende Werte, Eingabeidentität und externe Messwerte.

## Auf einen ruhigen Messlauf vorbereiten

Den Rechner am Netzteil betreiben. Während des Vergleichs Stromsparmodus, Displayhelligkeit und andere Einstellungen gleich lassen. Andere rechenintensive Arbeiten möglichst vor dem Messlauf beenden; das Skript beendet sie nicht selbst. Öffentliche Testdaten beibehalten. Der bisherige Ausgangszustand kann durch weitere offene Programme belastet sein.

Die ersten zehn Sekunden werden als Ausgangszustand protokolliert. Das ist kein garantiert unbelasteter Geräte-Leerlauf. Die Chip-Energie wird brutto integriert; es wird kein möglicherweise unpassender Leerlaufwert stillschweigend abgezogen.

## Terminalbefehle

Im entpackten Ordner:

```sh
# Vollständiger Lauf ohne Leistungsaufzeichnung
python3 start.py

# Mit macOS-Chipschätzung; Passwortabfrage im Terminal
python3 start.py --powermetrics

# Kurzer Funktionstest
python3 start.py --texts 256 --repeats 1 --idle-seconds 1 --cooldown 1

# Vorhandenen Lauf erneut auswerten
python3 start.py --analyse laeufe/DEIN_LAUF

# Separates powermetrics-Protokoll dem richtigen Lauf zuordnen
python3 start.py --analyse laeufe/DEIN_LAUF --power-log laeufe/DEIN_LAUF/powermetrics.txt
```

Die Aufzeichnung ist auf 1'800 Samples begrenzt. Ein beim Start privilegierter Helfer beendet seinen eigenen Messprozess auf ein lokales Stoppsignal; nach langen Läufen ist dafür keine zweite sudo-Anmeldung nötig. Diese Abschlusslogik ist mit einem Test-Messprozess geprüft. Falls der Start oder das Beenden der Messung fehlschlägt, meldet das Programm einen Fehler. Es signalisiert ausschliesslich den selbst gestarteten Messprozess.

## Externes Messgerät

Jeder abgeschlossene Lauf enthält `steckdose_vorlage.csv` mit den Durchlaufkennungen und Start-/Endzeiten des **gesamten Prozesses**, einschliesslich Python-Start, Modellladen, Warm-up und Ausgabe. Diese Vorlage kopieren und echte Energie in Wh aus genau diesen Zeitfenstern eintragen. Leere Felder bedeuten unbekannt. Ein Messgerät mit zeitaufgelöster Aufzeichnung ist dafür vorzuziehen; bei kurzen Jobs sind grobe manuelle Zählerstände ungeeignet.

```sh
python3 start.py --analyse laeufe/DEIN_LAUF --wall-csv meine_steckdosenwerte.csv
```

Mit einer vorhandenen Chip-Aufzeichnung zusätzlich `--power-log` angeben. Die externe Messung wird getrennt von der Chip-Energie der reinen Rechenphase ausgewiesen. Diese unterschiedlichen Messgrenzen dürfen nicht direkt gleichgesetzt werden. Einträge mit falscher Durchlaufkennung, falscher Messgrenze, doppelten Kennungen oder ungültigen Werten werden abgewiesen. Die importierten Gerätewerte sind Nutzereingaben und werden nicht unabhängig verifiziert.

## Dateien je Lauf

- `BERICHT.md`: verständliche Zusammenfassung.
- `ergebnisse.json`: Messwerte, Zeitfenster, Qualitätsvergleich und Grenzen.
- `ergebnisse.csv`: tabellarische Einzelversuche.
- `run.json`: Reihenfolge und Prozess-Zeitfenster.
- `steckdose_vorlage.csv`: Vorlage für externe Energiemesswerte.
- Je Versuch: Vektoren, Messmetadaten und Prozessprotokoll.
- Optional: `powermetrics.txt`, wenn die Chipmessung aktiviert wurde.

## Einrichtung auf einem anderen Rechner

Die vorhandene Umgebung wird nur auf diesem Rechner automatisch gefunden. Für einen anderen Rechner eine eigene Umgebung erstellen:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# Einmaliger Download des öffentlichen Modells, sofern noch nicht im Cache
.venv/bin/python messung.py --texts 64 --repeats 1 --idle-seconds 1 --cooldown 0 --download
```

Danach verwenden die Startdateien `.venv` und den lokalen Cache. Unter Windows ist eine passende Umgebung direkt aufzurufen; die `.command`-Dateien und die Chipmessung sind für macOS vorgesehen.

## Übergang zum NVIDIA-Server

Die Laptopdaten werden **nicht automatisch** als L4-Profil in die Jahresrechnung übernommen. Auf dem späteren Server denselben fachlichen Auftrag und geeignete Hardwareeinstellungen erneut messen. Erst dann tatsächliche Leistung, Tempo, Leerlauf, Start und Nebenverbrauch in das Modell übernehmen. Ein GPU-Leistungslimit und das Abschalten ganzer Server sind separate spätere Tests.

## Prüfen

```sh
python3 -m unittest discover -s tests -v
```

Acht Tests bestanden. Parser und Auswertung benötigen nur Python; Vektorvergleich und echter Auftrag benötigen NumPy/FastEmbed. Der Start kann eine bestehende FastEmbed-Umgebung nutzen, ohne sie zu verändern. Modell-Downloads sind standardmässig deaktiviert.

Fachliche Grundlage: [FastEmbed](https://qdrant.github.io/fastembed/Getting%20Started/), [ONNX-Threadverwaltung](https://onnxruntime.ai/docs/performance/tune-performance/threading.html) und die auf diesem Mac verfügbare Hilfe von `powermetrics`.
