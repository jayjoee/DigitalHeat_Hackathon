# Gesamtdemo – Start, Ablauf und Nachweis

Stand: 21. November 2026. Die Demo ergänzt den vorhandenen Projektstand lokal. In den gemeinsamen Repository-Stand integriert.

**Bezahlte Rechenaufträge erzeugen Wärme. Können wir damit Häuser sinnvoll mitheizen?** Die Gesamtdemo zeigt in drei Stationen, wie Wärme, Rechenaufträge und Einnahmen zusammenpassen müssen.

## Was die Demo zeigt

### 1. Das Haus

Das bestehende Jahresmodell ergibt für das Referenzhaus: acht Server, rund 93 % Wärmedeckung und 5 kWh weggekühlte Wärme. Diese Ergebnisse setzen genügend flexible Rechenaufträge voraus. Sie sind keine Messung eines realen Hauses.

### 2. Ein echter Auftrag

Ein öffentliches Textarchiv wird auf dem Laptop in Suchvektoren umgewandelt. Dieser Auftrag läuft tatsächlich als eigener Prozess.

- **Winter:** hoher Wärmebedarf, viel Rechenzeit.
- **Sommer:** wenig Wärmebedarf, weniger Rechenzeit.
- **Speicher voll:** Der Prozess wird angehalten und später fortgesetzt.

Das sind drei Ausschnitte aus derselben Jahresrechnung. Der laufende Textzähler stammt aus echten Checkpoints. Dieselbe Scheduler-Funktion steuert Jahresmodell und Prozessfreigabe. In bestätigten Pausen prüft die Demo, dass sich der Checkpoint nicht verändert.

Häuser, Serverplätze, Wärme und die beschleunigte Modellzeit sind simuliert. Der Laptop ersetzt einen repräsentativen Serverplatz. Es wird keine reale Heizung gesteuert. Prozesspause bedeutet keinen ausgeschalteten Rechner. Die Demo misst keine Energie und führt kein Pharma-Screening aus.

### 3. Die wirtschaftliche Voraussetzung

Das Unternehmensmodell braucht zahlende Kunden und passende Hardware. In der Oberfläche stehen zwei unterschiedliche Preisgrenzen:

- rund CHF 0,23 pro Serverstunde für Strom nach Gutschrift der verwendeten Wärme (Case-Definition);
- eine deutlich höhere Grenze im Unternehmensmodell mit Hardware, Betrieb, Steuern und Zinsen. Die aktuellen Werte stehen in [KOSTEN_DH.md](../wirtschaft/KOSTEN_DH.md).

Diese Grenzen nicht verwechseln. Die Rechnung enthält Preis- und Absatzannahmen; tatsächliche Abnahmezusagen und Messungen der vorgesehenen NVIDIA-Hardware fehlen noch.

## Was ist jetzt wichtig?

**Zuerst diese Gesamtdemo verstehen und zeigen.** ML und die Laptop-Energiemessung sind ergänzende Untersuchungen. Sie sind nicht der Hauptzweck des Projekts.

Der nächste reale Pilot braucht einen zahlenden Kunden, einen geeigneten Wärmestandort und gemessene Serverdaten. Vertrauliche Pharma-Daten brauchen zusätzlich eine passende Sicherheitsarchitektur.

## Auf diesem Rechner

```sh
python3 demo_start.py --open
```

Oder `Gesamtdemo_starten.command` doppelklicken. Oberfläche: `http://127.0.0.1:18200`. Dort startet die Schaltfläche „Live-Demo starten“ den echten CPU-Auftrag. Es läuft höchstens eine Live-Demo gleichzeitig. Wiederholungen bekommen jeweils einen neuen Arbeitsordner; vorhandene Messungen werden nicht gelöscht.

Die vorhandene FastEmbed-Umgebung des Desktop-Projekts wird automatisch verwendet. Der Hauptdienst selbst benötigt nur Python. Der Worker braucht FastEmbed und den bereits vorhandenen Modellcache.

## Neue Einrichtung

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-live.txt
.venv/bin/python -c 'from fastembed import TextEmbedding; TextEmbedding("BAAI/bge-small-en-v1.5")'
python3 demo_start.py --open
```

Die einmalige Einrichtung lädt das öffentliche Modell. Die Live-Demo selbst verwendet `--offline` und den CPU-Provider. Alternativ lässt sich eine vorhandene passende Python-Umgebung mit `DIGITALHEAT_PYTHON` auswählen.

## Ablauf

1. `build_case()` führt `Haus(8, "spot", "rechnen")` für alle 8'760 Stunden aus.
2. Die neu berechnete Bilanz wird im Browser angezeigt. Sie stimmt mit `bilanz_8_spot.json` überein.
3. Tagesausschnitte vom 15. Januar, 15. Juli und 7. März werden direkt aus diesem Lauf übernommen.
4. Je Tag wird mit der vorhandenen Funktion `waehle_server()` ein repräsentativer Serverplatz ausgewählt. Dessen zeitlicher Anteil stammt aus `anteil()` und der tatsächlichen Scheduler-Ausgabe.
5. Der echte vorhandene Embedding-Worker initialisiert das Modell, meldet Bereitschaft und hält sich zunächst mit SIGSTOP an. Der Hauptdienst bestätigt den gestoppten Zustand, bevor die Demo beginnt.
6. Je Modellstunde läuft der Prozess für seinen freigegebenen Anteil der beschleunigten Echtzeit. SIGSTOP/SIGCONT steuern tatsächliche Pausen und Weiterlauf.
7. Während bestätigter Pausen wird geprüft, dass die Checkpoint-Zahl unverändert bleibt.
8. Zum Abschluss oder bei Abbruch wird der Worker fortgesetzt, mit SIGTERM um einen Checkpoint gebeten und beendet. Ein Zeitlimit verhindert unbegrenzt laufende Worker.

Standard sind 1,2 Sekunden pro Modellstunde: 72 Stunden entsprechen etwa 86 Sekunden, zuzüglich Initialisierung und letztem Checkpoint. `--seconds` erlaubt eine andere Geschwindigkeit. Die Live-Zeit ist keine Benchmark-Laufzeit und keine Energiemessung.

## Fachliche Abgrenzung

- Echter Auftrag: BGE-small-Embeddings aus öffentlichen AG-News-Texten, keine proprietären Pharma-Daten.
- Simuliert: Haus, Heizsystem, acht Referenzserver, Stundenverlauf und Wärme.
- Der Worker repräsentiert einen Serverplatz, nicht alle simulierten Aufträge der Jahreswarteschlange.
- Kein physischer Ortswechsel, kein Verteilen auf mehrere echte Geräte in dieser Gesamtdemo. Der vorhandene Flottenrouter ist ein eigener weiterführender Ablauf.
- Kein ML nötig, um diesen Kernnachweis zu führen. Die ML-Untersuchung bleibt separat verfügbar.
- Der niedrigere Case-Break-even berücksichtigt nur Strom abzüglich Wärmewert. Der höhere Preis stammt aus dem Unternehmensmodell inklusive Investition und weiterer Kosten.
- Die wirtschaftlichen Werte bleiben Annahmenrechnungen und keine Bestätigung tatsächlicher Nachfrage oder Pharma-Sicherheit.

## Ergebnisse

Je Lauf liegt unter `messungen/gesamtdemo/<Zeitstempel>/`:

- `demo.json`: Ablauf, Prozess-ID, Modellstunden, tatsächliche Checkpoint-Zähler, bestätigte Pausen und Abschlussstatus.
- `stand.json`: Checkpoint des echten Embedding-Jobs.
- `vektoren_*.npy`: tatsächlich berechnete Textvektoren.
- `prozess.log`: Ausgabe des Workers.

Die Betriebsoberflächen für Pharma und Serverhalter bleiben getrennt. Der neue Port 18200 ist ausschliesslich der geführte Nachweis für den Case.

## Prüfen

```sh
python3 -m unittest discover -s tests -v
```

38 Tests bestehen: die bisherigen 34 Prüfungen und vier neue Tests für Referenzgleichheit, Winter-/Sommer-/Pausenverlauf, Herkunfts-/Sitzungsschutz sowie die explizit freigegebenen Dateien und Befehle. Der lokale Dienst ist kein öffentlicher Produktionsserver.

Ein kompakter abgeschlossener Prüflauf ist unter `messungen/gesamtdemo_nachweis/` versioniert. Neue Live-Läufe und ihre Vektoren bleiben lokal. Die ausführbare Mehrstandort-Simulation mit Abschalten aus `serverbetrieb.py` bleibt unverändert verfügbar.
