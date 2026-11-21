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
| 3D-Ansicht: Häuser im Schnitt, Holzofen statt Öl, Sportbad, Cloud mit ML-Prognose, Pausieren vs. Abschalten, Thermostat, Tour für den Pitch | `bash dashboard/starten.sh`, dann http://localhost:8765/3d/ (läuft ohne Internet; Daten neu: `python3 src/dashboard3d_daten.py`) |
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

### Confidential-Computing-Integration

`confidential_start.py` verschlüsselt Testaufträge auf dem Kundengerät, plant Kata/CoCo-Jobs
und berechnet angenommene Mehrkosten. Ein separater Worker-Endpunkt nimmt nur verschlüsselte
Pakete an; Schlüssel kommen ausschliesslich vom externen Trustee nach dessen Attestierung.
Die Softwareintegration ist getestet, eine echte TDX-/Confidential-GPU-Umgebung ist noch
nicht eingerichtet. **L4 ist für diesen GPU-Schutzpfad nicht unterstützt.**
[Architektur, Quellen, Annahmen und reale Bereitstellung](docs/CONFIDENTIAL_COMPUTING.md).

### Ressourcenbasierte Auftragsvergabe

Die getrennte Pharma-/Host-Demo (`python3 prototyp/digitalheat.py demo --pharma --open`)
verwendet jetzt eine Warteschlange mit GPU-/VRAM-, RAM-, CPU-, Standort- und Freigabeprüfung,
Kundenpriorität, Kontingenten, Backfill und Wartungssperren. CPU-Demoaufträge laufen;
GPU-Aufträge warten auf einen echten GPU-Worker. Nur öffentliche/synthetische Inhalte sind zugelassen.
`python3 queue_start.py` vergleicht die Vergabestrategien und simuliertes Schlafenlegen.
[Recherche, Annahmen, Grenzen und Betreiberkonfiguration](docs/RESSOURCEN_SCHEDULER.md).

### ML-Serviceplanung

`python3 service_start.py --demo --case --open` trainiert ein ML-Risikomodell und berechnet
Serviceintervalle, erwartete geplante/ungeplante Eingriffe und Kosten pro physischem
Server. Voraussetzung: `requirements-ml.txt`. HTML, CSV und JSON entstehen unter
`daten/ergebnisse/service_ml/`. Eigene CSV-Dateien sind über `--history` und `--fleet`
anschliessbar. Der Case-Modus übernimmt getrennte Betriebsstunden, Rechenstunden und
Starts je Server aus dem bestehenden Jahres-Scheduler. Die gemeinsame Kühlung hat
einen unabhängigen Wartungskalender. **Die Demo nutzt künstliche Trainingsdaten und angenommene Servicewirkungen;
sie ist kein realer L4-Wartungsnachweis.** [Methode und Datenschema](docs/SERVICE_ML.md)

### Kontrollierter Vergleich der Betriebsstrategien

`python3 vergleich_start.py --days 184` berechnet vier Varianten mit identischen
endlichen Aufträgen, Fristen und aktiven Leistungs-/Geschwindigkeitsprofilen.
Voraussetzung: `requirements-ml.txt`. Bericht, Kennzahlen-CSV und vollständiges JSON
entstehen unter `daten/ergebnisse/strategievergleich/`; das bisherige ML-Dashboard bleibt erhalten.

Referenzlauf Juli–Dezember 2025 (4’416 Stunden, acht Server):

| Strategie | Gesamtstrom inkl. Zusatzheizung | Fristgerecht / eingereicht |
|---|---:|---:|
| Ohne Wärmesteuerung, Abwärme wird trotzdem genutzt | 21’618,1 kWh | 22’436 / 22’436 |
| Wärmesteuerung, Server bleiben an | 21’559,0 kWh | 22’436 / 22’436 |
| Wärmesteuerung + Abschalten | 18’121,5 kWh | 22’436 / 22’436 |
| Zusätzlich ML-Prognose | 18’121,6 kWh | 22’436 / 22’436 |

Keine verpassten oder am Ende offenen Aufträge; identische erledigte Auftrags-IDs.
Rund 16,2 % weniger Gesamtstrom durch Wärmesteuerung mit Abschalten gegenüber der
Basis, unter diesen **ungemessenen Szenarioannahmen**. Weniger Leerlaufwärme erhöht
den Zusatzheizbedarf; dieser ist mit COP 2,5 im Gesamtstrom enthalten. Das ist kein
Öl-Pilot-Nachweis. ML bringt in diesem Lauf keinen zusätzlichen Stromvorteil.
Die Auswertung ist ein Halbjahresvergleich eines Hauses, keine Jahres- oder Flottenbilanz.

[Dokumentenverzeichnis](docs/README.md) · [Case](docs/CASE.md) · [Pitch](docs/PITCH.md) · [Pharma-Sicht](docs/PHARMA_SICHT.md) · [Kundensicht](docs/CustomerView_Joel.md) · [Kosten](docs/KOSTEN_DH.md) · [Nächste Aufgaben](docs/TODO_KURZ.md) · [Abgabevorschläge](submission/SUBMISSION.md) · [Firmenrechnung](docs/FIRMA.md)

Code, Analysen und Texte wurden mit Claude Code und Codex erarbeitet. Der ursprüngliche Wärme-Router, die neue Serverbetriebssimulation und die Blister-Demo sind erhalten; Gesamtdemo, ML-Untersuchung und Messwerkzeug ergänzen diesen gemeinsamen Stand.
