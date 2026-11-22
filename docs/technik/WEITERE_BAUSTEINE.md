# Weitere Bausteine

Ausführlichere Beschreibungen, die bisher in der README standen (ausgelagert am 21.11.2026). Befehle laufen aus dem Hauptordner des Repos.

## Gewähltes Angebot: öffentliche L4-Aufträge

Das Team behält L4 und verarbeitet öffentliche/synthetische sowie beim Kunden bereits
ausreichend anonymisierte und freigegebene Aufgaben. Die lokale Demo ist ausdrücklich
auf öffentliche Verarbeitung begrenzt. Die geprüfte Hybridvariante wurde verworfen.
[Angebot, Freigabemechanismus und Grenzen](../kunden/L4_ANGEBOT.md).

## Confidential-Computing-Rechercheoption – nicht das gewählte Angebot

`start/confidential_start.py` verschlüsselt Testaufträge auf dem Kundengerät, plant Kata/CoCo-Jobs
und berechnet angenommene Mehrkosten. Ein separater Worker-Endpunkt nimmt nur verschlüsselte
Pakete an; Schlüssel kommen ausschliesslich vom externen Trustee nach dessen Attestierung.
Die Softwareintegration ist getestet, eine echte TDX-/Confidential-GPU-Umgebung ist noch
nicht eingerichtet. **L4 ist für diesen GPU-Schutzpfad nicht unterstützt.**
[Architektur, Quellen, Annahmen und reale Bereitstellung](CONFIDENTIAL_COMPUTING.md).

## Ressourcenbasierte Auftragsvergabe

Die getrennte Pharma-/Host-Demo (`python3 prototyp/digitalheat.py demo --open`)
verwendet jetzt eine Warteschlange mit GPU-/VRAM-, RAM-, CPU-, Standort- und Freigabeprüfung,
Kundenpriorität, Kontingenten, Backfill und Wartungssperren. CPU-Demoaufträge laufen;
GPU-Aufträge warten auf einen echten GPU-Worker. Nur öffentliche/synthetische Inhalte sind zugelassen.
`python3 start/queue_start.py` vergleicht die Vergabestrategien und simuliertes Schlafenlegen.
[Recherche, Annahmen, Grenzen und Betreiberkonfiguration](RESSOURCEN_SCHEDULER.md).

## ML-Serviceplanung

`python3 start/service_start.py --demo --case --open` trainiert ein ML-Risikomodell und berechnet
Serviceintervalle, erwartete geplante/ungeplante Eingriffe und Kosten pro physischem
Server. Voraussetzung: `requirements/ml.txt`. HTML, CSV und JSON entstehen unter
`daten/ergebnisse/service_ml/`. Eigene CSV-Dateien sind über `--history` und `--fleet`
anschliessbar. Der Case-Modus übernimmt getrennte Betriebsstunden, Rechenstunden und
Starts je Server aus dem bestehenden Jahres-Scheduler. Die gemeinsame Kühlung hat
einen unabhängigen Wartungskalender. **Die Demo nutzt künstliche Trainingsdaten und angenommene Servicewirkungen;
sie ist kein realer L4-Wartungsnachweis.** [Methode und Datenschema](SERVICE_ML.md)

## Kontrollierter Vergleich der Betriebsstrategien

`python3 start/vergleich_start.py --days 184` berechnet vier Varianten mit identischen
endlichen Aufträgen, Fristen und aktiven Leistungs-/Geschwindigkeitsprofilen.
Voraussetzung: `requirements/ml.txt`. Bericht, Kennzahlen-CSV und vollständiges JSON
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
