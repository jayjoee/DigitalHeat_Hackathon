# Jobtypen (Muss-Kriterium 1)

Erzeugt mit `python3 src/jobtypen.py` → `daten/jobtypen.json` (liest der Scheduler).

| | **A Archiv-Embedding** | **B Bildanalyse-Batch** |
|---|---|---|
| Inhalt | 10 Mio. Texte einbetten (Suchindex eines Dokumentenarchivs) | 1 Mio. Bilder auf Objekte prüfen (z. B. Inspektions- oder Kamerabilder eines Tages) |
| Modell | bge-small-en-v1.5 (Text-Embedding) | RetinaNet (Objekterkennung, OpenImages, mAP 37,3) |
| Arbeit pro kWh | 10,6 Mio. Texte | 8,2 Mio. Bilder |
| **Energie pro Job** | **0,941 kWh** | **0,121 kWh** |
| **Laufzeit auf 1-kW-Server** | **56,5 min** | **7,3 min** |
| **Unterbrechbar** | **ja**: Pause jederzeit, Stopp am Checkpoint alle 128 Texte | **nein** innerhalb des Jobs (kurz, ohne Checkpoint), nur zwischen Jobs |
| **Frist** | **24 h** | **2 h** |
| Herkunft Energie | **eigene Messung** auf M1 Pro: 85,4 Texte/s bei 28,9 W (powermetrics), `messungen/MESSUNG.md` | **MLPerf Inference v5.0**, ID 5.0-0023, Fujitsu PRIMERGY CDI mit 8× H100 NVL, Offline: 11'106 Bilder/s bei 4'849 W |
| Herkunft Frist | Annahme: nächtliche Neuberechnung, passt zu 74 % wiederkehrenden Jobs im Alibaba-Trace | Annahme: Ergebnisse werden am selben Morgen gebraucht |
| Läuft echt auf dem Laptop | ja, unter Kontrolle des Schedulers | nein, nur im Jahresmodell |

## Rolle im Scheduler
- **A trägt die Wärme**: lang, flexibel, pausierbar. Der Scheduler verschiebt A in die Stunden mit Wärmebedarf und pausiert A, wenn der Speicher voll ist.
- **B ist die harte Last**: kurz, mit enger Frist und nicht unterbrechbar. B muss laufen, auch wenn gerade keine Wärme gebraucht wird. Dann landet die Wärme im Speicher, geht an einen anderen Standort oder wird abgeführt. Daran zeigt sich der Zielkonflikt zwischen Rechenerlös und abgeführter Wärme.

## Skalierung auf den 1-kW-Referenzserver
- Beide Typen gleich: **energieproportional**, also gleiche Arbeit pro kWh wie gemessen.
- A ist dabei konservativ, weil ein GPU-Server Embeddings effizienter rechnet als eine Laptop-CPU.
- B kommt bereits von einem GPU-Server. 1 kW entspricht ≈ 1/4,85 dieses Systems, also etwa 1,6 H100 NVL.
- Wärme: 1 kW Strom → 0,8 kW nutzbar, unabhängig vom Jobtyp.

## Grenzen
- MLPerf-Werte sind Bestwerte des Herstellers unter optimalen Bedingungen (TensorRT, Offline). Im Betrieb ist der Durchsatz eher tiefer, die Energie pro Bild also höher.
- Arbeit pro kWh von A und B ist nicht vergleichbar (CPU gegen GPU, verschiedene Aufgaben). Die Bilanz rechnet ohnehin in Serverstunden.
- **Ankünfte pro Tag sind noch nicht festgelegt.** Sie folgen im Scheduler aus dem Alibaba-Trace (≈ 3,6 Jobs pro Server und Tag, Median 11 min) oder werden als «unbegrenzte Nachfrage» ausdrücklich so benannt.
- Whisper (Transkription, MLPerf v5.1) ist als möglicher Typ C vorgemerkt. Offen ist, wie lang ein «Sample» Audio dauert, das ist vor einer Verwendung zu klären.

## Echter Pharma-Auftrag: virtuelles Screening (Docking)

Neben dem Embedding läuft auch ein **echtes Docking** auf dem Laptop: `src/jobs/docking_job.py` testet 28 Moleküle (Schlüssel) gegen die Bindetasche der Abl-Kinase (Schloss, PDB 1IEP) mit AutoDock Vina. Details, Quellen und Ergebnis: [docking/README.md](docking/README.md).

| | Virtuelles Screening (Docking) |
|---|---|
| Inhalt | Moleküle an ein Zielprotein docken und nach Bindungsenergie ordnen |
| Laufzeit (gemessen) | im Median 5,5 s pro Molekül, 0,4–74 s je nach Grösse; alle 28 Moleküle 384 s (Linux-Testrechner, 4 Kerne) |
| Unterbrechbar | **ja**: Pause jederzeit (ganze Prozessgruppe), Checkpoint nach jedem Molekül |
| Frist | **Wochen bis Monate** (Screening-Kampagne, `docs/kunden/PHARMA_SICHT.md`) |
| Rolle im Modell | verhält sich wie Typ A mit langer Frist; was eine lange Frist bringt, zeigt `src/scheduler/frist_szenario.py` |
| Läuft echt | ja, unter Kontrolle des Schedulers: `python3 src/scheduler/live.py --tag 2025-03-07 --job docking` |

Die Energie pro Molekül ist noch nicht gemessen; auf dem Mac lässt sie sich wie beim Embedding mit powermetrics bestimmen (`messungen/MESSUNG.md`). Für die Jahresbilanz ändert das nichts: Das Modell rechnet in Server-Stunden, die Wärme hängt nicht am Auftragstyp.
