# Rechnen, das heizt

**DigitalHeat erledigt Rechenaufträge und nutzt ihre Abwärme zum Heizen von Häusern und im Sommer eines Sportbads.** Das Hackathon-Projekt verbindet Jahresmodell, Wärme-Router, echte Laptop-Aufträge und getrennte Produktoberflächen.

Damit das funktioniert, müssen drei Dinge zusammenpassen:

1. Die Wärme wird im Haus tatsächlich gebraucht.
2. Die Rechenaufträge werden sinnvoll und rechtzeitig erledigt.
3. Die Einnahmen decken Hardware und Betrieb.

Diese README ist der einzige Einstieg. Alle weiteren Dokumente stehen unten unter [Dokumente](#dokumente).

## Was liegt wo?

| Ordner | Inhalt |
|---|---|
| `start/` | Alle Startskripte, die Doppelklick-Dateien für macOS (`*.command`) und `alles_neu_rechnen.py` |
| `src/` | Programmcode: Scheduler, Wärme-Router, Wirtschaftlichkeit, Jobs, ML |
| `docs/` | Case, Pitch, Aufgaben; Unterordner `ergebnisse/`, `wirtschaft/`, `kunden/`, `technik/` |
| `daten/` | Eingangsdaten mit Quellen, `ergebnisse/` mit allen erzeugten Ergebnisdateien |
| `dashboard/` | Analyse-, 3D-, Gesamtdemo- und ML-Oberflächen |
| `prototyp/` | Pharma-/Serverhalter-Oberflächen und Blister-Demo mit zwei Laptops |
| `messungen/`, `messwerkzeug/` | Gemessene Laufzeiten und Energie, Werkzeug zum Messen |
| `tests/` | Tests für Scheduler, Wirtschaft, Demos, ML und Confidential Computing |
| `requirements/` | Python-Pakete je Umgebung (`live`, `ml`, `confidential`, gepinnte Embedding-Umgebung) |
| `deploy/` | Vorlagen für die Confidential-Computing-Bereitstellung |

## Die geführte Gesamtdemo starten

Die Gesamtdemo beantwortet drei Fragen: Wie viel Wärme decken die Server? Steuert der Wärmebedarf einen echten Auftrag? Unter welchen Annahmen lohnt sich das Geschäft?

Python 3.10 oder neuer, macOS oder Linux. Einmalig eine Umgebung mit FastEmbed und dem öffentlichen Modell einrichten:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements/live.txt
.venv/bin/python -c 'from fastembed import TextEmbedding; TextEmbedding("BAAI/bge-small-en-v1.5")'
.venv/bin/python start/demo_start.py --open
```

Danach reicht auf macOS `start/Gesamtdemo_starten.command`. Die Oberfläche läuft unter **http://127.0.0.1:18200**. Dort **Live-Demo starten** drücken. Winter, Sommer und voller Speicher werden in etwa 90 Sekunden gezeigt. Der Embedding-Prozess und seine Pausen sind echt; Haus und Wärme sind simuliert.

[Was die Demo zeigt, Ablauf und Methode](docs/technik/GESAMTDEMO.md)

## Welche Ansicht wofür?

| Zweck | Einstieg |
|---|---|
| Projekt als Ganzes verstehen | Gesamtdemo, Port 18200 |
| 3D-Ansicht: Häuser im Schnitt, Holzofen statt Öl, Sportbad, Cloud mit ML-Prognose, Pausieren vs. Abschalten, Thermostat, Tour für den Pitch | `bash dashboard/starten.sh`, dann http://localhost:8765/3d/ (läuft ohne Internet; Daten neu: `python3 src/dashboard3d_daten.py`) |
| Jahreszahlen, Flotte und Serverbetrieb untersuchen | `bash dashboard/starten.sh`, Port 8765; alternativ `dashboard/artifact/index.html` mit Aufzeichnung |
| Echten Auftrag im Wärme-Router zeigen | `.venv/bin/python src/scheduler/live.py --flotte --sekunden 3`; mit `--abschalten` auch Serverzustände simulieren |
| Pharma-Kunde und Serverhalter getrennt bedienen | [prototyp/README.md](prototyp/README.md) |
| Tablettenprüfung mit zwei Leinwänden und Checkpoint-Übergabe zeigen | [prototyp/blister/README.md](prototyp/blister/README.md) |
| ML-Energievergleich untersuchen | [docs/technik/ML_SYSTEM.md](docs/technik/ML_SYSTEM.md), eigener Dienst auf Port 18100 |
| Reale Laptop-Laufzeiten und Chip-Energieschätzungen vergleichen | [messwerkzeug/README.md](messwerkzeug/README.md) |

Der Blister-Batch wechselt im Demo-Wärmeverlauf automatisch vom Haus zum Sportbad und bei erneutem Wärmebedarf zurück. Die Produktoberflächen, Gesamtdemo und ML-Untersuchung bleiben eigenständige Abläufe.

## Die wichtigsten Modellzahlen

| Kennzahl | Einordnung |
|---|---|
| 8 Referenzserver pro Haus | Je 1 kW im Case; 8 L4-Karten pro Server im Hardwarekonzept |
| Rund 93 % Wärmedeckung, 5 kWh weggekühlt | Case-Idealmodell, genügend flexible Aufträge, 0 W Leerlauf |
| Rund 90,5 % Wärmedeckung mit Abschalten | Erweiterte Rechnung mit angenommenen Betriebszuständen |
| Rund 5'200 kWh weniger Strom pro Jahr durch Abschalten statt Prozesspause | Simulationsvergleich bei angenommenen 230 W Leerlauf |
| Rund CHF 290'000 Investition pro Haus | Hardware-/Einbauannahmen, keine gemessene Pilotinstallation |
| CHF 0,50 pro L4-Stunde (Roche, 60 %) und 0,55 für den Rest | Angenommene Zielpreise, kein belegter Kundenauftrag |
| Rund CHF 35'000 jährliches Modellergebnis mit Abschalten | Nur wenn jede Stunde verkauft ist; bei 66 % verkauften Stunden null |
| Rund CHF 27'500 mit Roche und einem Winterkunden | 82 % der Rechenstunden fallen in die Heizsaison; der Sommerrest darf unverkauft bleiben |
| Pilot: 1 Haus, 2 Server, ein Winter, CHF 81'500 | Klare Schwellen für den Ausbauentscheid in [PILOTPLAN.md](docs/wirtschaft/PILOTPLAN.md) |

Massgebend sind [KOSTEN_DH.md](docs/wirtschaft/KOSTEN_DH.md) und [ERGEBNISSE.md](docs/ergebnisse/ERGEBNISSE.md); diese Tabelle fasst sie nur zusammen. Die Unternehmenskennzahl wird als jährliches Kapitalwertäquivalent berechnet. Sie ist kein bereits erzielter realer Jahresgewinn. Bei knapper Nachfrage kann das System Verlust machen.

## Was ist echt und was ist simuliert?

- **Echt:** Text-Embeddings auf dem Laptop, Prozesspause/Weiterlauf, Checkpoint-Neustart, gemessene Laufzeiten und macOS-Chip-Leistungsschätzungen.
- **Echt auf künstlichen Daten:** Die Blister-Demo prüft Pixel mit einer Helligkeitsregel und übergibt den Bearbeitungsstand per TLS. Kein trainiertes oder validiertes Pharma-Modell.
- **Simuliert:** Häuser, Sportbad, Heizsystem, NVIDIA-Leistung, Rechenauftragsmengen und viele Kosten-/Vertragswerte.
- **ML tatsächlich trainiert:** Das zusätzliche Modell lernt den berechneten Case-Wärmebedarf. Im bisherigen Vergleich ist der zusätzliche Energieeffekt sehr klein und kein belastbarer Effizienznachweis.
- **Noch offen:** Verbindliche Kundenabnahme, echte L4-Messungen, geeignete Heiztemperatur und vollständige Sicherheit für vertrauliche Pharma-Daten.

Transportverschlüsselung und getrennte Oberflächen schützen nicht automatisch vor Administratorzugriff auf den verarbeitenden Rechner.

## Die Bausteine

| Baustein | Zweck | Ort |
|---|---|---|
| Jahresmodell | Wärmebedarf, Speicher, Rechenlast, Fristen und Kosten über 8'760 Stunden berechnen | `src/scheduler/jahr.py`, `kern.py` |
| Wärme-Router | Aufträge zwischen Häusern und einem Sportbad als Sommer-Wärmeabnehmer verteilen | `src/scheduler/router.py`, `flotte.py` |
| Zusage am Vortag | Rechenkapazität anhand der Wetterprognose mit Reserve zusagen | `src/scheduler/zusage.py` |
| Serverbetrieb | Leerlauf, Startzeit, Standby und Abschalten in Häusern und Sportbad simulieren | `src/scheduler/serverbetrieb.py` |
| Unternehmensrechnung | Investition, Erlöse, laufende Kosten, Steuern und Restwert abbilden | `src/wirtschaft.py`, `src/kosten_dh.py`, `src/firma.py` |
| Annahmen | Alle Modellannahmen an einem Ort, jede mit Quelle | `src/scheduler/annahmen.py` |
| Echter KI-Auftrag | Öffentliche Nachrichtentexte auf der CPU in Suchvektoren umwandeln | `src/jobs/embedding_job.py` |
| Live-Steuerung | Prozesspause, Weiterlauf und Checkpoint-Neustart aus dem Wärme-Router steuern | `src/scheduler/live.py`, `live_flotte.py` |
| Analyse-Dashboard | Jahresresultate, Tagesverläufe, Flotte und Serverbetrieb untersuchen | `dashboard/` |

**Die Demonstratoren:**

| Demonstrator | Was tatsächlich passiert | Grenze |
|---|---|---|
| Geführte Gesamtdemo | Die Jahresbilanz und drei Tagesausschnitte steuern einen echten Embedding-Prozess; Pausen werden anhand stabiler Checkpoints geprüft | Laptop repräsentiert einen modellierten Serverplatz; keine echte Heizung |
| Pharma- und Serverhalter-Oberflächen | Aufträge und Ergebnisse sind von der einfachen Betriebsansicht getrennt; Übertragung mit TLS | Gemeinsamer Demo-Kundenzugang, keine vollständige Mandanten-/Pharma-Sicherheit |
| Blisterprüfung | Helligkeitsprüfung auf 30 synthetischen Bildern; automatische Checkpoint-Übergabe per TLS anhand einer aufgezeichneten Router-Entscheidung | Wärme und Vorlauftemperatur dienen der Simulation; die Bildprüfung verwendet eine Helligkeitsregel |

Die allgemeine Pharma-Oberfläche enthält Screening-, Cell-Painting- und Literaturvorlagen. Screening und Cell Painting erzeugen dort synthetische Ergebnisse; Literatur liefert echte Textstatistik.

**Ergänzende Untersuchungen:**

- **ML-Energievergleich:** Ein Gradient-Boosting-Modell prognostiziert den berechneten Case-Wärmebedarf (Training Januar–Mai, Kalibrierung Juni, Auswertung ab Juli). Gegenüber derselben sparsamen Steuerung ohne ML spart es im Referenzversuch zusätzlich rund 0,77 kWh oder 0,0045 % Strom. Das ist kein belastbarer Effizienznachweis. [ML_ERGEBNISSE.md](docs/ergebnisse/ML_ERGEBNISSE.md)
- **Laptop-Messung:** Neun Durchläufe mit je 2'048 Texten auf dem M1 Pro. Standard hatte den niedrigsten Median: rund 22,8 Sekunden und 0,178 Wh geschätzte Chip-Energie. Weniger Threads und grössere Pakete sparten nichts. macOS-Chipschätzungen, keine Steckdosenmessung und kein L4-Nachweis. [messungen/MESSUNG.md](messungen/MESSUNG.md)
- **Weitere Bausteine:** gewähltes L4-Angebot, Confidential-Computing-Recherche, ressourcenbasierte Auftragsvergabe, ML-Serviceplanung und kontrollierter Vergleich der Betriebsstrategien. [WEITERE_BAUSTEINE.md](docs/technik/WEITERE_BAUSTEINE.md)

## Rechnen und prüfen

Alle Ergebnisdateien und alle Zahlen der Wirtschaftlichkeit mit einem Befehl neu erzeugen, zum Beispiel nach einer Änderung in `src/scheduler/annahmen.py`. Es braucht keine zusätzlichen Python-Pakete:

```sh
python3 start/alles_neu_rechnen.py
```

Einzelne Schritte und Tests:

```sh
python3 src/scheduler/jahr.py --server 8
python3 src/kosten_dh.py
python3 -m unittest discover -s tests -v

# ML-Umgebung separat einrichten
python3 -m venv .venv-ml
.venv-ml/bin/python -m pip install -r requirements/ml.txt
.venv-ml/bin/python -m unittest discover -s tests -v

# Produktprototyp und Messauswertung separat prüfen
python3 -m unittest discover -s prototyp/tests -v
python3 -m unittest discover -s messwerkzeug/tests -v
```

Die vollständige stündliche ML-Auswertung und neue Live-Vektoren werden lokal erzeugt. Kompakte Referenzergebnisse und Messprotokolle sind versioniert; Zugangsdaten und virtuelle Umgebungen nicht.

## Was noch offen ist

Die gemeinsame Aufgabenliste steht in [docs/TODO.md](docs/TODO.md). Die wichtigsten Punkte: einen zahlenden Kunden mit konkreter Arbeitsmenge finden, echte NVIDIA-Server messen, einen realen Wärmestandort erproben und den Schutz vertraulicher Pharma-Daten nachweisen.

## Dokumente

| Ordner | Datei | In einem Satz |
|---|---|---|
| `docs/` | [CASE.md](docs/CASE.md) | Die Aufgabe von DigitalHeat, so wie wir sie bekommen haben |
| | [PITCH.md](docs/PITCH.md) | Was wir im 5-Minuten-Pitch sagen, Demo-Befehle und Antworten auf Fragen der Jury |
| | [TODO.md](docs/TODO.md) | Die nächsten Aufgaben und bewusst verschobene Punkte |
| `docs/ergebnisse/` | [RESULTATE_EINFACH.md](docs/ergebnisse/RESULTATE_EINFACH.md) | Alle Resultate ohne Fachbegriffe erklärt. **Hier anfangen** |
| | [ERGEBNISSE.md](docs/ergebnisse/ERGEBNISSE.md) | Alle Ergebnisse mit Zahlen, Tabellen und Grenzen, für Fachleute |
| | [ML_ERGEBNISSE.md](docs/ergebnisse/ML_ERGEBNISSE.md) | Der kleine zusätzliche ML-Effekt im bisherigen Szenario |
| `docs/wirtschaft/` | [KOSTEN_DH.md](docs/wirtschaft/KOSTEN_DH.md) | Was DigitalHeat investiert, was es kostet und was es verdient |
| | [FIRMA.md](docs/wirtschaft/FIRMA.md) | Rechnung für die ganze Firma über 10 Jahre mit Ausbauplan und Finanzierung |
| | [PILOTPLAN.md](docs/wirtschaft/PILOTPLAN.md) | Ein Winter, ein Haus: was gemessen wird und ab welchen Werten ausgebaut wird |
| | [ANNAHMEN_PRUEFUNG.md](docs/wirtschaft/ANNAHMEN_PRUEFUNG.md) | Jede Annahme kritisch geprüft: Hält sie, und was passiert, wenn nicht? |
| `docs/kunden/` | [L4_ANGEBOT.md](docs/kunden/L4_ANGEBOT.md) | Gewählte Ausrichtung: L4 für öffentliche/synthetische oder kundenseitig anonymisierte und freigegebene Aufgaben |
| | [PHARMA_SICHT.md](docs/kunden/PHARMA_SICHT.md) | Wer die Rechenzeit kauft, was Kunden heute zahlen und welche Verträge üblich sind |
| | [CustomerView_Joel.md](docs/kunden/CustomerView_Joel.md) | Die Sicht des Hausbesitzers: Was hat der Haushalt davon? |
| `docs/technik/` | [GESAMTDEMO.md](docs/technik/GESAMTDEMO.md) | Was die Gesamtdemo zeigt, Start, Prozesssteuerung und Grenzen |
| | [waerme-router-basel.md](docs/technik/waerme-router-basel.md) | Bauplan für den Wärme-Router und unsere Entscheide |
| | [RESSOURCEN_SCHEDULER.md](docs/technik/RESSOURCEN_SCHEDULER.md) | Vergabecode, Wettbewerbsrecherche, Quellen, Annahmen und Grenzen der Ressourcenwarteschlange |
| | [ML_SYSTEM.md](docs/technik/ML_SYSTEM.md) | Aufbau und Aussagekraft der separaten ML-Untersuchung |
| | [SERVICE_ML.md](docs/technik/SERVICE_ML.md) | ML-Serviceplanung: Methode und Datenschema |
| | [CONFIDENTIAL_COMPUTING.md](docs/technik/CONFIDENTIAL_COMPUTING.md) | Verschlüsselte Aufträge, externer Schlüsseldienst, Hardwarevoraussetzungen, Mehrkosten und offene Hardware-Abnahme |
| | [WEITERE_BAUSTEINE.md](docs/technik/WEITERE_BAUSTEINE.md) | L4-Angebot, Confidential Computing, Auftragsvergabe, Serviceplanung und Strategievergleich in Kürze |

Weitere Hintergründe liegen bei den Daten: [HALLENBAD.md](daten/HALLENBAD.md) (Wärmebedarf Sportbad), [PREISE.md](daten/PREISE.md), [QUELLEN.md](daten/QUELLEN.md), [ALIBABA_AUSWERTUNG.md](daten/ALIBABA_AUSWERTUNG.md), [MESSUNG.md](messungen/MESSUNG.md).

Code, Analysen und Texte wurden mit Claude Code und Codex erarbeitet. Der ursprüngliche Wärme-Router, die neue Serverbetriebssimulation und die Blister-Demo sind erhalten; Gesamtdemo, ML-Untersuchung und Messwerkzeug ergänzen diesen gemeinsamen Stand.
