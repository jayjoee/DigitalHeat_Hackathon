# Worum geht es bei DigitalHeat?

**Bezahlte Rechenaufträge erzeugen Wärme. Können wir damit Häuser sinnvoll mitheizen?**

Dafür müssen drei Dinge zusammenpassen:

1. Die Wärme wird im Haus tatsächlich gebraucht.
2. Die Rechenaufträge werden sinnvoll und rechtzeitig erledigt.
3. Die Einnahmen decken Hardware und Betrieb.

## Die Gesamtdemo starten

Auf diesem Rechner: **`Gesamtdemo_starten.command` doppelklicken.** Die Seite öffnet sich unter `http://127.0.0.1:18200`.

Falls sie bereits läuft, direkt diese Adresse öffnen. Für die Live-Demo den Knopf **„Live-Demo starten“** drücken. Sie dauert ungefähr 90 Sekunden und kann über **„Beenden“** angehalten werden.

## Was zeigen wir?

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

- rund CHF 0,23 pro Serverstunde für Strom nach Gutschrift der verwendeten Wärme;
- rund CHF 2,87 pro Serverstunde im umfassenderen Unternehmensmodell. Das ist der Wert des Case-Modells ohne Leerlauf; mit abschaltenden Servern und 230 W Leerlauf sind es CHF 3,07 (`KOSTEN_DH.md`).

Diese Grenzen nicht verwechseln. Die Rechnung enthält Preis- und Absatzannahmen; tatsächliche Abnahmezusagen und Messungen der vorgesehenen NVIDIA-Hardware fehlen noch.

## Was ist jetzt wichtig?

**Zuerst diese Gesamtdemo verstehen und zeigen.** ML und die Laptop-Energiemessung sind ergänzende Untersuchungen. Sie sind nicht der Hauptzweck des Projekts.

Der nächste reale Pilot braucht einen zahlenden Kunden, einen geeigneten Wärmestandort und gemessene Serverdaten. Vertrauliche Pharma-Daten brauchen zusätzlich eine passende Sicherheitsarchitektur.
