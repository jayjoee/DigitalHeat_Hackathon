# Ressourcen-Scheduler: Recherche, Umsetzung und Annahmen

Stand: 21. November 2026. Der Scheduler ist in die getrennte Pharma-/Host-Demo eingebunden. Er ergänzt den bisherigen Wärme-Jahres-Scheduler und die ML-Serviceplanung.

## Welche Verfahren wir übernehmen

Wir übernehmen öffentlich dokumentierte Ideen als eigene kleine Python-Implementierung. Wir installieren weder Run:ai noch Kubernetes und kopieren keinen proprietären Programmcode. Slurm und Kueue sind Vergleichssysteme für die Auftragsvergabe, keine Wärmeanbieter. Aus deren Dokumentation lässt sich keine garantierte Einsparung für DigitalHeat ableiten.

| Vergleich | Öffentlich dokumentiertes Verfahren | Unsere Umsetzung | Grenze |
|---|---|---|---|
| [NVIDIA Run:ai](https://run-ai-docs.nvidia.com/self-hosted/platform-management/runai-scheduler/scheduling/how-the-scheduler-works) | Ressourcen, Quoten und organisatorische Regeln bestimmen die Platzierung; Bin Packing bündelt Arbeit. | Erst passende Server filtern, dann geschätzte zusätzliche Stromkosten minimieren und bereits belegte Server bevorzugen. | Lineares Strommodell; ganze GPUs, keine GPU-Fraktionen oder tatsächliche Speicherisolation. |
| [Kueue Admission Fair Sharing](https://kueue.sigs.k8s.io/docs/concepts/admission_fair_sharing/) | Frühere reservierte Nutzung und eine Belastung bei Zulassung verhindern, dass ein Kunde alles belegt. | Gewichtete, exponentiell abklingende Nutzungszählung; Belastung sofort bei Zuteilung, parallele Aufträge und GPUs je Kunde begrenzen. | Eigene Formel, keine vollständige Kueue-Implementierung. |
| [Kueue ClusterQueue](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/) | Ressourcenvarianten und Kontingente regeln die Zulassung. | GPU-Modell, VRAM je Karte, Host-RAM, CPU, Region, Datenklasse und Kundenzulassung müssen passen. | Keine geliehenen Kontingente, Cohorts oder Verdrängung laufender Aufträge. |
| [Slurm Backfill](https://slurm.schedmd.com/sched_config.html) | Ein kleiner Auftrag darf vorziehen, wenn er den erwarteten Start höher gereihter Arbeit nicht verschiebt. Dafür braucht es brauchbare Laufzeitgrenzen. | Konservative Reservierung erwarteter Ressourcenfreigaben je Server; kurze passende Aufträge nutzen die Lücke. | Laufzeiten sind Schätzungen; keine clusterweite optimale Planung oder garantierte Startzeit. |
| [Slurm Power Saving](https://slurm.schedmd.com/power_save.html) | Ungenutzte Rechner schlafen; benötigte Rechner werden geweckt und müssen ihre Bereitschaft bestätigen. | Scheduler liefert Schlaf-/Weckempfehlungen. Im Vergleichslauf simuliert ein Controller Start und Bereitschaft, jeweils einen Server gleichzeitig. | Auf echter Hardware werden keine Ausschaltbefehle gesendet. Ein realer Controller und Bereitschaftsmeldungen fehlen. |

Für eine spätere Kubernetes-Installation ist [NVIDIAs offener KAI-Scheduler](https://github.com/kai-scheduler/KAI-Scheduler) ein möglicher Ersatz für unseren kleinen Kern. Er ist hier nicht installiert; sein Funktionsumfang und seine Isolation gelten deshalb nicht automatisch für unsere Demo.

Als direkten Wärmerechen-Konkurrenten haben wir [Heatas öffentliche technische Dokumentation](https://cdn.heata.co/) geprüft: Sie beschreibt eine ständig verfügbare Steuerung und austauschbare Worker; bei Ausfall wird Arbeit auf andere Worker verteilt. Eine genaue Queue-Kostenfunktion veröffentlicht diese Seite nicht. Wir behaupten deshalb keine Kopie des internen Heata-Algorithmus. Dauerhafte Steuerung und Wiederaufnahme nach Ausfällen bleiben eine spätere Ausbaustufe unserer Lösung.

## Ablauf eines Auftrags

1. Der Zugangsschlüssel bestimmt den Kunden. Priorität, Quoten und Freigaben kommen ausschliesslich aus der Betreiberkonfiguration. Vom Kunden mitgesendete Prioritäts-/Freigabefelder werden abgelehnt.
2. Datenklasse, Standort und Einzelkontingent werden geprüft. Der ausführende CPU-Prototyp nimmt nur öffentliche bzw. synthetische Inhalte an. Vertrauliche Pharma-Daten werden abgewiesen.
3. Vor Zuteilung werden Serverfreigabe und deren Ablaufdatum, GPU-Modell, Anzahl ganzer GPUs, VRAM **je Karte**, freier Host-RAM, freie CPU-Kerne und Ausführungsplätze geprüft. VRAM verschiedener Karten wird nicht addiert.
4. Fehlende/veraltete Gesundheitsmeldungen (wenn konfiguriert), kritische Zustände, Wartungsfälligkeit und fehlende Wärmefreigabe verhindern Zuteilungen. Der Auftrag muss vor dem nächsten Wartungstermin fertig werden können.
5. Reihenfolge: durch Wartezeit verbesserte Vertragspriorität, danach gewichtete Nutzung, dann Frist und Eingangszeit. Das ist keine reine Fristenreihenfolge und keine SLA-Garantie. Backfill darf freie Zeitfenster nutzen.
6. Die Zuteilung reserviert alle Ressourcen zusammen unter einer Sperre. Auch bei überschrittener Laufzeit werden Ressourcen erst nach bestätigtem Ende der Ausführung freigegeben. Ein überfälliger Prozess kann somit keine Doppelbelegung auslösen.
7. Die CPU-Ausführung prüft laufend Pause, Frist, Laufzeitlimit und Sperren. Bei kritischer Meldung pausiert sie, behält ihre Reservierung und endet spätestens am Laufzeitlimit. Ein realer Not-Aus des Servers wird dadurch nicht ersetzt.

`drain` lässt bereits laufende Aufträge fertig werden und nimmt keine neuen an. `isolated` blockiert auch die laufende Verarbeitung. Kritische Sperren bleiben bestehen, bis der Betreiber sie ausdrücklich aufhebt. Normale erfolgreiche Aufträge setzen keinen Wartungskalender zurück.

## Verbindung zum bestehenden ML-Tool

`--service-plan` liest das Ergebnis-JSON unserer [Serviceplanung](SERVICE_ML.md). Ohne zusätzliche Freigabe erscheinen die Ergebnisse nur als Hinweise. `--approve-service-dates` übernimmt separat den individuellen Servertermin und den gemeinsamen Kühlungstermin; der frühere Termin begrenzt die Vergabe. Ein individueller Service verschiebt den Kühlungstermin nicht.

Das bisherige Modell wurde mit synthetischen Daten trainiert. Sein Risikowert sperrt deshalb **keinen** Server automatisch. Eine risikobasierte Zulassungssperre setzt ausdrücklich als echt und validiert deklarierte Daten voraus. Diese Kennzeichnung ist eine Betreiberangabe, keine technische Beglaubigung. Kritische reale Meldungen und fällige freigegebene Termine blockieren unabhängig davon. ML unterstützt die Wartungsentscheidung; verbindliche Ressourcen- und Sicherheitsprüfungen bleiben deterministisch.

## Eigene Annahmen und Herkunft

Die genannten Fremdsysteme begründen die Verfahren, nicht unsere Zahlenwerte. Für alle folgenden Standardwerte gilt: Sie sind konfigurierbare Teamannahmen, sofern keine andere Herkunft angegeben ist.

| Annahme | Wert / Bedeutung | Herkunft und Prüfbedarf |
|---|---|---|
| Vertragspriorität | 0 dringend bis 3 Batch; pro Kunde festgelegt | Eigene Produktregel, keine bereits abgeschlossenen Kundenverträge. |
| Wartezeitausgleich | Alle 900 s eine Prioritätsstufe besser, maximal Stufe 0 | Eigener Startwert; an echten Wartezeiten prüfen. |
| Fairness | Zähler = Laufzeit × max(GPU-Anzahl, CPU/8, RAM/64); Abklingzeit 3’600 s; durch Kundengewicht geteilt | Eigene vereinfachte Heuristik nach Kueue-Idee; keine gemessene Kostenäquivalenz. |
| Kontingente | Standard maximal 4 gleichzeitige Aufträge und 64 GPUs je Kunde | Generische Obergrenzen des Kerns, keine zugesagte Hardwarekapazität. CPU-Demo begrenzt zusätzlich durch ihre Worker-Anzahl. |
| CPU-Demo | 4 GB reservierbares Host-RAM; keine GPU | Gewähltes Demobudget, keine automatische Hardwaremessung oder RAM-Begrenzung durch das Betriebssystem. |
| Ganze GPUs | Eine reservierte GPU gehört genau einem Auftrag | Bewusst einfaches Ressourcenmodell; kein MIG, MPS oder GPU-Sharing. |
| Laufzeitgrenze CPU-Demo | 2 × gewünschte aktive Demolaufzeit + 2 s | Eigene Sicherheitsreserve inklusive Pausen; Hardwareläufe brauchen Profiling und durchsetzbare Limits. |
| Gesundheitsalter | Maximal 120 s, wenn Gesundheitsdatei aktiviert | Eigener Startwert; fehlende/ungültige Daten sperren. Ohne diese Option behaupten wir keine laufende Sensorüberwachung. |
| Abfragehäufigkeit | Vergabe ungefähr alle 50 ms, Gesundheitsdatei alle 500 ms | Eigene Demowerte; keine Echtzeit-/Ausfallgarantie. |
| Risiko-Schwelle | 20 % für die nächsten 30 Tage, nur für explizit validierte Risikodaten | Unkalibrierter Platzhalter, keine Herstellerangabe; synthetische Werte bleiben Hinweise. |
| Kühlungsnotfall | Gemeldeter Durchfluss 0 bei eingeschaltetem Server löst Sperre aus | Eigene vorsichtige Regel für den Kühlplattenkreislauf. Kein Wasser vorausgesetzt; Kühlflüssigkeit und Sensoren müssen zur realen Anlage passen. |
| Temperaturgrenze | Kein universeller Standardwert | Muss als `max_gpu_temp_c` für die konkrete Hardware freigegeben werden. |
| Leerlauf vor Schlaf | 300 s ohne passende Arbeit | Eigener Testwert, nach Slurm-Verfahrensidee; Starts, Serviceverschleiss und Wärmebedarf später mitoptimieren. |
| Serverleistung | 1 kW aktiv, 230 W Leerlauf, 10 W Standby; Start 300 s | Übernahme der **Annahmen** des vorhandenen Serverbetriebsmodells, keine Messung eines 8-L4-Servers. Siehe `src/scheduler/serverbetrieb.py` und Service-Annahmen. |
| Preis | 0,3325 CHF/kWh | Vorhandener Projektwert, kein aktuelles verbindliches Stromangebot. |
| Leistungsmodell | Leerlauf + (Aktiv−Leerlauf) × Belegungsanteil | Eigene lineare Näherung; keine gemessene GPU-/Host-Kennlinie. |
| Vergleichsflotte | 3 Hosts mit je 8 L4, 24 GB pro Karte, 192 GB RAM und 16 CPU-Kernen | Simuliertes Inventar. Daraus folgt weder ein validiertes Serverdesign noch, dass diese Hardware vorhanden ist. |
| Testnachfrage | 48 künstliche Aufträge über 6 Ankunftsstunden, 8 h Bilanz; Laufzeiten 180–600 s, Frist 1 h nach Eingang | Frei erzeugte Funktionsdaten mit festem Zufallsstartwert 2026; keine beobachtete Pharma-Nachfrage. |
| Wärme | Wärmebedarf nur als nachrangiges Platzierungskriterium; bestehende Wärmefreigabe bleibt verbindlich | Noch keine gemeinsame Optimierung von Pufferspeicher, Pumpen, Ersatzheizung und diesen GPU-Aufträgen. |

## Starten und betreiben

Ohne Zusatzpakete den kontrollierten Vergleich rechnen:

```sh
python3 start/queue_start.py
```

Der Kern `src/scheduler/resource_queue.py` benötigt keine Oberfläche. Die Einbindung erfolgt direkt im Worker `prototyp/digitalheat.py`: Jeder eingehende Auftrag durchläuft die neue Vergabe vor der Ausführung. Die vorhandene Oberfläche ist lediglich ein optionaler Zugang und wurde für diesen Stand nicht erweitert.

Optional lässt sich der bestehende Zugang starten:

```sh
python3 prototyp/digitalheat.py demo --open
```

CPU-Aufträge laufen tatsächlich. GPU-Aufträge bleiben mit sichtbarer Begründung in der Warteschlange: Es ist noch kein NVIDIA-Ausführungsagent angeschlossen. Eine konfigurierte GPU-Kapazität allein bewirkt keine GPU-Ausführung.

Das Auftragsschema der Worker-API `/v1/jobs` enthält beispielsweise:

```json
{"title":"Synthetischer GPU-Auftrag","task_type":"virtual_screening","sample_count":1000,"target":"Demo","duration":5,"deadline_seconds":3600,"requirements":{"gpu_count":1,"gpu_memory_gb":24,"ram_gb":16,"cpu_cores":1,"classification":"public"}}
```

Der Aufruf benötigt TLS und den Bearer-Schlüssel des Kunden. Priorität und Freigaben sind keine Eingabefelder dieser API. Antworten enthalten `waiting_reason`, `assigned_server`, `gpu_devices` und `resource_lease_active`. Ohne GPU-Executor wartet dieser Beispielauftrag; er wird nicht als CPU-Auftrag ausgeführt.

Für Betreiber gibt es `daten/beispiele/scheduler_cpu.json`. Diese Datei enthält keine Schlüssel. `token_env` bezeichnet eine Umgebungsvariable mit einem zufälligen Zugangsschlüssel von mindestens 40 Zeichen; unterschiedliche Kunden brauchen unterschiedliche Schlüssel. Die vorhandenen TLS-Zugangsdaten werden wie bisher initialisiert. Die Kundenseite nutzt den jeweils zugehörigen Schlüssel in ihrem lokalen Zugangsdatenverzeichnis. Beispiel für den Worker nach Einrichtung der Schlüssel:

```sh
python3 prototyp/digitalheat.py worker --credentials credentials/worker --scheduler-config daten/beispiele/scheduler_cpu.json
```

Optional `--health-file /absoluter/pfad/health.json` verwenden. Die vertrauenswürdige Betreiberdatei hat das Format:

```json
{"observed_at": 1795250000, "nodes": [{"id": "local-cpu-demo", "powered": true, "flow_lpm": 2.5, "critical": false}]}
```

Der Zeitstempel ist nur ein Formatbeispiel und absichtlich nicht frisch. Reales Monitoring muss die Datei atomar mit dem tatsächlichen Unix-Beobachtungszeitpunkt aktualisieren. Nach einem Dateifehler wird eine neue gültige Beobachtung benötigt. Die Datei darf nicht vom Kunden beschreibbar sein. Sie ist eine Schnittstelle, kein bereits installierter Sensoragent. `clear: true` hebt eine gespeicherte Sperre ausdrücklich auf; das gehört in den kontrollierten Betreiberprozess.

## Was die Energieauswertung aussagt

`start/queue_start.py` schreibt identische Eingangsaufträge samt Hash sowie JSON, CSV und Bericht. Verglichen werden FIFO/Verteilung, Priorität/Bündelung und zusätzlich simuliertes Schlafenlegen. Alle Varianten verwenden dieselben Ressourcen-/Freigabeprüfungen. Der Referenzlauf erledigt überall dieselben 48 Aufträge ohne Fristverletzung. Das reine Bündeln senkt bei ständig eingeschalteten Hosts die modellierte IT-Energie nicht; der Vorteil entsteht durch weniger Leerlauf im Schlafmodus.

Die Rechnung ist ein Funktionsvergleich bei geringer Auslastung. Pumpen, Datenübertragung, Steuerungsenergie, Speicherung, reale Wärmeabnahme, Ersatzheizung und Wartungskosten fehlen. Sie belegt weder Gesamtsystem-Einsparung noch Unternehmensrentabilität und darf nicht mit den 18’121,5 kWh des früheren Halbjahresmodells gleichgesetzt werden. Für eine belastbare Entscheidung müssen reale Leistungsprofile, Laufzeiten, Fristen, Startkosten und eine vollständige Wärmebilanz hinein.

## Grenzen vor produktiver Pharma-Nutzung

Die Queue liegt im Arbeitsspeicher; Neustarts verlieren Aufträge. Keine dauerhafte Datenbank, automatische Wiederaufnahme, Checkpoints oder verteilte Ausfallsicherung. Der Ressourcen-Kern verwaltet Metadaten; RAM-/GPU-Reservierungen sind keine Betriebssystemgrenzen. TLS schützt den Transport, die Host-Anwendung kann im CPU-Demobetrieb Klartext sehen. Eine Sicherheitsklasse in der Konfiguration beweist weder Verschlüsselung während der Verarbeitung noch eine geprüfte Pharma-Umgebung. Es werden daher nur öffentliche/synthetische Inhalte angenommen.

Als nächste reale Ausbaustufe braucht es einen NVIDIA-Worker mit geprüfter Geräteerkennung und Ressourcenlimits, authentisierte Sensormeldungen und einen dauerhaften Auftragsbestand. Danach lassen sich dieselben Tests mit gemessenen Energie- und Laufzeitdaten wiederholen.
