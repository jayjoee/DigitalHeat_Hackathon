# DigitalHeat Projektübersicht

Stand der Zusammenführung: 21. November 2026. Das gemeinsame Ziel ist: **Bezahlte Rechenaufträge erledigen und die entstehende Wärme zum Heizen verwenden.**

Die bisher getrennten lokalen Ergänzungen sind nun im selben Repository enthalten. Sie haben weiterhin verschiedene Zwecke; die Veröffentlichung macht daraus noch keinen durchgehend verbundenen Produktivbetrieb.

## Das Grundsystem

| Baustein | Zweck | Ort |
|---|---|---|
| Jahresmodell | Wärmebedarf, Speicher, Rechenlast, Fristen und Kosten über 8'760 Stunden berechnen | `src/scheduler/jahr.py`, `kern.py` |
| Wärme-Router | Aufträge zwischen Häusern und einem Sportbad als Sommer-Wärmeabnehmer verteilen | `src/scheduler/router.py`, `flotte.py` |
| Zusage am Vortag | Rechenkapazität anhand der Wetterprognose mit Reserve zusagen | `src/scheduler/zusage.py` |
| Serverbetrieb | Leerlauf, Startzeit, Standby und Abschalten in Häusern und Sportbad simulieren | `src/scheduler/serverbetrieb.py` |
| Unternehmensrechnung | Investition, Erlöse, laufende Kosten, Steuern und Restwert abbilden | `src/wirtschaft.py` |
| Echter KI-Auftrag | Öffentliche Nachrichtentexte auf der CPU in Suchvektoren umwandeln | `src/jobs/embedding_job.py` |
| Ursprüngliche Live-Steuerung | Prozesspause, Weiterlauf und Checkpoint-Neustart aus dem Wärme-Router steuern | `src/scheduler/live.py`, `live_flotte.py` |
| Analyse-Dashboard | Jahresresultate, Tagesverläufe, Flotte und Serverbetrieb untersuchen | `dashboard/` |

Das Case-Idealmodell ergibt für acht Referenzserver rund 93 % Wärmedeckung und 5 kWh weggekühlte Wärme, wenn genügend flexible Aufträge vorhanden sind. Die neue Rechnung mit Abschalten und angenommenem Leerlauf ergibt rund 90,5 % Wärmedeckung. Häuser, Wärme und NVIDIA-Leistung sind weiterhin simuliert.

## Die Demonstratoren

| Demonstrator | Was tatsächlich passiert | Grenze |
|---|---|---|
| Geführte Gesamtdemo | Die Jahresbilanz und drei Tagesausschnitte steuern einen echten Embedding-Prozess; Pausen werden anhand stabiler Checkpoints geprüft | Laptop repräsentiert einen modellierten Serverplatz; keine echte Heizung |
| Pharma- und Serverhalter-Oberflächen | Aufträge und Ergebnisse sind von der einfachen Betriebsansicht getrennt; Übertragung mit TLS | Gemeinsamer Demo-Kundenzugang, keine vollständige Mandanten-/Pharma-Sicherheit |
| Blisterprüfung | Helligkeitsprüfung auf 30 synthetischen Bildern; manueller Wechsel mit verschlüsselter Checkpoint-Übergabe zwischen Sender und Empfänger | Kein trainiertes/validiertes Pharma-Modell; noch nicht automatisch an den Wärme-Router angeschlossen |

Die allgemeine Pharma-Oberfläche enthält Screening-, Cell-Painting- und Literaturvorlagen. Screening und Cell Painting erzeugen dort synthetische Ergebnisse; Literatur liefert echte Textstatistik. Die Blisterprüfung ist eine zusätzliche, separate bildhafte Demo.

## Die ergänzenden Untersuchungen

**ML-Energievergleich:** Ein echtes Gradient-Boosting-Modell prognostiziert den berechneten Case-Wärmebedarf. Es wird mit Januar–Mai trainiert, mit Juni kalibriert und ab Juli ausgewertet. Gegenüber derselben sparsamen Steuerung ohne ML beträgt die zusätzliche Stromersparnis im Referenzversuch rund 0,77 kWh oder 0,0045 %. Das ist kein belastbarer zusätzlicher Effizienznachweis. Der ML-Vergleich verwendet sein eigenes transparentes Energieprofil; seine Werte nicht direkt mit dem anderen Serverbetriebsmodell gleichsetzen.

**Laptop-Messung:** Neun Durchläufe mit je 2'048 Texten auf dem M1 Pro verglichen Standard, weniger Threads und grössere Pakete. Standard hatte den niedrigsten Median: rund 22,8 Sekunden und 0,178 Wh geschätzte Chip-Energie für die Rechenphase. Weniger Threads und grössere Pakete zeigten keine Einsparung. Alle Ergebnisse waren numerisch ähnlich. Die Werte sind macOS-Chipschätzungen, keine Steckdosenmessungen und kein L4-Nachweis.

## Wo anfangen?

1. **Projekt verstehen und zeigen:** `Gesamtdemo_starten.command` oder `python3 demo_start.py --open`, Port 18200. [Kurze Orientierung](START_HIER.md)
2. **Pharma mit zwei Leinwänden zeigen:** [Blister-Anleitung](../prototyp/blister/README.md).
3. **Produktrollen zeigen:** [Prototyp-Anleitung](../prototyp/README.md).
4. **Zahlen vertiefen:** bestehendes Dashboard auf Port 8765.
5. **ML oder Energie untersuchen:** [ML-Methode](ML_SYSTEM.md) und [Messwerkzeug](../messwerkzeug/README.md).

## Was noch offen ist

- Echte NVIDIA-Server messen: Leistung, Tempo, Leerlauf, Start, nutzbare Heiztemperatur und Gesamtverbrauch.
- Einen zahlenden Kunden mit konkreter Arbeitsmenge, Frist und Vergütung finden.
- Einen realen Wärmestandort erproben.
- Schutz vertraulicher Pharma-Daten gegen Netzwerkangreifer, andere Kunden und den Besitzer des Rechners nachweisen.
- Produktaufträge, Blister-Übergabe, Wärme-Router und echte Hardware durchgehend verbinden.

Die dokumentierten Wirtschaftsergebnisse beruhen auf Annahmen. Die jährliche Unternehmenskennzahl ist ein Kapitalwertäquivalent, kein bereits erzielter Jahresgewinn. Der Wärmewert, die Deckungsquote und die niedrige Case-Preisgrenze belegen alleine kein tragfähiges Geschäft.

Die nächste gemeinsame Arbeit ist ein vollständig nachvollziehbarer Demo-Ablauf und danach ein Pilot mit Kunde, Servermessung und Wärmestandort. Alte ZIPs und lokale Kopien sind Zwischenstände; dieser Repository-Stand bündelt die weitergeführten Teile.

Eine kurze aktuelle Aufgabenliste steht in [TODO_KURZ.md](TODO_KURZ.md). Der frühere zusätzliche Pharma-Arbeitsentwurf ist unter [archiv/PharmaView_Joel.md](archiv/PharmaView_Joel.md) zur Nachvollziehbarkeit abgelegt.
