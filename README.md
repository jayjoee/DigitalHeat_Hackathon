# Rechnen, das heizt

**DigitalHeat erledigt Rechenaufträge und nutzt ihre Abwärme zum Heizen von Häusern und im Sommer eines Sportbads.** Das Hackathon-Projekt verbindet Jahresmodell, Wärme-Router, echte Laptop-Aufträge und getrennte Produktoberflächen.

**Neu hier?** [Projektübersicht](docs/PROJEKTUEBERSICHT.md) lesen. Sie zeigt, welche Teile vorhanden sind, was gemessen ist und was noch simuliert wird.

## Die geführte Gesamtdemo starten

Die Gesamtdemo beantwortet drei Fragen: Wie viel Wärme decken die Server? Steuert der Wärmebedarf einen echten Auftrag? Unter welchen Annahmen lohnt sich das Geschäft?

Python 3.10 oder neuer, macOS oder Linux. Einmalig eine Umgebung mit FastEmbed und dem öffentlichen Modell einrichten:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-live.txt
.venv/bin/python -c 'from fastembed import TextEmbedding; TextEmbedding("BAAI/bge-small-en-v1.5")'
.venv/bin/python demo_start.py --open
```

Danach reicht auf macOS `Gesamtdemo_starten.command`. Die Oberfläche läuft unter **http://127.0.0.1:18200**. Dort **Live-Demo starten** drücken. Winter, Sommer und voller Speicher werden in etwa 90 Sekunden gezeigt. Der Embedding-Prozess und seine Pausen sind echt; Haus und Wärme sind simuliert.

[Kurze Orientierung](docs/START_HIER.md) · [Ablauf und Methode](docs/GESAMTDEMO.md)

## Welche Ansicht wofür?

| Zweck | Einstieg |
|---|---|
| Projekt als Ganzes verstehen | Gesamtdemo, Port 18200 |
| Jahreszahlen, Flotte und Serverbetrieb untersuchen | `bash dashboard/starten.sh`, Port 8765; alternativ `dashboard/artifact/index.html` mit Aufzeichnung |
| Echten Auftrag im Wärme-Router zeigen | `.venv/bin/python src/scheduler/live.py --flotte --sekunden 3`; mit `--abschalten` auch Serverzustände simulieren |
| Pharma-Kunde und Serverhalter getrennt bedienen | [prototyp/README.md](prototyp/README.md) |
| Tablettenprüfung mit zwei Leinwänden und Checkpoint-Übergabe zeigen | [prototyp/blister/README.md](prototyp/blister/README.md) |
| ML-Energievergleich untersuchen | [docs/ML_SYSTEM.md](docs/ML_SYSTEM.md), eigener Dienst auf Port 18100 |
| Reale Laptop-Laufzeiten und Chip-Energieschätzungen vergleichen | [messwerkzeug/README.md](messwerkzeug/README.md) |

Die Ansichten haben verschiedene Zwecke. Die Blister-Übergabe wird manuell ausgelöst; sie ist noch nicht automatisch an den Jahresrouter angeschlossen. Die Produktoberflächen, Gesamtdemo und ML-Untersuchung bleiben eigenständige Abläufe.

## Die wichtigsten Modellzahlen

| Kennzahl | Einordnung |
|---|---|
| 8 Referenzserver pro Haus | Je 1 kW im Case; 8 L4-Karten pro Server im Hardwarekonzept |
| Rund 93 % Wärmedeckung, 5 kWh weggekühlt | Case-Idealmodell, genügend flexible Aufträge, 0 W Leerlauf |
| Rund 90,5 % Wärmedeckung mit Abschalten | Erweiterte Rechnung mit angenommenen Betriebszuständen |
| Rund 5'200 kWh weniger Strom pro Jahr durch Abschalten statt Prozesspause | Simulationsvergleich bei angenommenen 230 W Leerlauf |
| Rund CHF 290'000 Investition pro Haus | Hardware-/Einbauannahmen, keine gemessene Pilotinstallation |
| CHF 4,80 pro Serverstunde | Angenommener Vertragspreis, kein belegter Kundenauftrag |
| Rund CHF 29'400 jährliches Modellergebnis mit Abschalten | Vor Day-ahead-Gutschriften; Annahmen zu Absatz und Preisen gelten weiterhin |

Die Unternehmenskennzahl wird als jährliches Kapitalwertäquivalent berechnet. Sie ist kein bereits erzielter realer Jahresgewinn. Bei knapper Nachfrage kann das System Verlust machen. [Ergebnisse und Grenzen](docs/ERGEBNISSE.md)

## Was ist echt und was ist simuliert?

- **Echt:** Text-Embeddings auf dem Laptop, Prozesspause/Weiterlauf, Checkpoint-Neustart, gemessene Laufzeiten und macOS-Chip-Leistungsschätzungen.
- **Echt auf künstlichen Daten:** Die Blister-Demo prüft Pixel mit einer Helligkeitsregel und übergibt den Bearbeitungsstand per TLS. Kein trainiertes oder validiertes Pharma-Modell.
- **Simuliert:** Häuser, Sportbad, Heizsystem, NVIDIA-Leistung, Rechenauftragsmengen und viele Kosten-/Vertragswerte.
- **ML tatsächlich trainiert:** Das zusätzliche Modell lernt den berechneten Case-Wärmebedarf. Im bisherigen Vergleich ist der zusätzliche Energieeffekt sehr klein und kein belastbarer Effizienznachweis.
- **Noch offen:** Verbindliche Kundenabnahme, echte L4-Messungen, geeignete Heiztemperatur und vollständige Sicherheit für vertrauliche Pharma-Daten.

Transportverschlüsselung und getrennte Oberflächen schützen nicht automatisch vor Administratorzugriff auf den verarbeitenden Rechner.

## Rechnen und prüfen

Der bisherige Jahres-Scheduler benötigt keine zusätzlichen Python-Pakete. Für die ML-Tests separat `requirements-ml.txt` installieren; das Embedding-Setup bleibt in `.venv`.

```sh
python3 src/scheduler/jahr.py --server 8
python3 -m src.scheduler.serverbetrieb --ausgabe daten/ergebnisse/serverbetrieb.json
python3 src/scheduler/zusage.py
python3 src/scheduler/flotte.py --abschalten

# ML-Umgebung separat einrichten
python3 -m venv .venv-ml
.venv-ml/bin/python -m pip install -r requirements-ml.txt
.venv-ml/bin/python -m unittest discover -s tests -v

# Produktprototyp und Messauswertung separat prüfen
python3 -m unittest discover -s prototyp/tests -v
python3 -m unittest discover -s messwerkzeug/tests -v
```

Die vollständige stündliche ML-Auswertung und neue Live-Vektoren werden lokal erzeugt. Kompakte Referenzergebnisse und Messprotokolle sind versioniert; Zugangsdaten und virtuelle Umgebungen nicht.

## Dokumente und Abgabe

[Dokumentenverzeichnis](docs/README.md) · [Case](docs/CASE.md) · [Pitch](docs/PITCH.md) · [Pharma-Sicht](docs/PHARMA_SICHT.md) · [Kundensicht](docs/CustomerView_Joel.md) · [Kosten](docs/KOSTEN_DH.md) · [Nächste Aufgaben](docs/TODO_KURZ.md) · [Abgabevorschläge](submission/SUBMISSION.md)

Code, Analysen und Texte wurden mit Claude Code und Codex erarbeitet. Der ursprüngliche Wärme-Router, die neue Serverbetriebssimulation und die Blister-Demo sind erhalten; Gesamtdemo, ML-Untersuchung und Messwerkzeug ergänzen diesen gemeinsamen Stand.
