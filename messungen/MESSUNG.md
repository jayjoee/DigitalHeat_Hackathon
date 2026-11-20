# Messung Jobtyp A: Archiv-Embedding (20.11.2026)

## Aufbau
- Gerät: MacBook Pro (MacBookPro18,3), Apple M1 Pro, 8 Kerne (6 Leistung, 2 Effizienz), 16 GB, am Netz
- Software: Python 3.13, fastembed 0.9.1, ONNX Runtime 1.32.0, CPU, 6 Threads, Batch 16 (`requirements.txt`)
- Modell: BAAI/bge-small-en-v1.5 (384 Dimensionen)
- Daten: AG News Testset, 7'600 Nachrichtentexte, Median 231 Zeichen (Hugging Face `fancyzhx/ag_news`)
- Job: `src/jobs/embedding_job.py`, Checkpoint alle 128 Texte (Vektoren + `stand.json`, atomar geschrieben)
- Leistung: `powermetrics --samplers cpu_power -i 1000` (Apple, Summe CPU + GPU + ANE, jede Sekunde)

## Massgebliche Messung (21:31:07–21:32:37)
Lauf `embedding_powermetrics`, Leistungslog `powermetrics_2026-11-20_2131.txt` (150 Proben ab 21:31:00).

| Grösse | Wert |
|---|---|
| Texte | 7'600 |
| Rechenzeit (Summe der Blöcke) | **89,0 s** |
| Durchsatz | **85,4 Texte/s** |
| Leistung während des Jobs (89 s) | **28,9 W** |
| Leerlauf vor und nach dem Job (61 s) | 1,4 W |
| Mehrleistung durch den Job | 27,5 W |
| **Energie** | **0,094 Wh pro 1'000 Texte** = 10,6 Mio. Texte pro kWh |
| Systemlast beim Start | 8,3 (macOS-Update lief noch) |

Gerechnet wird mit der vollen Leistung (28,9 W) und nicht nur mit der Mehrleistung. Das ist vorsichtig, weil der Job damit etwas mehr Energie braucht.

Gemessen ist nur der Chip (CPU, GPU, ANE). Bildschirm, Speicher, Netzteilverluste und Lüfter fehlen. Für die Wärme spielt das keine Rolle (siehe Skalierung), für die Texte pro kWh ist es eine leichte Überschätzung.

Erste Messung (21:20, Lauf `embedding_2026-11-20_2120`): 102,0 s, 74,5 Texte/s, Systemlast 17 wegen eines macOS-Updates, Leistung damals nur angenommen (30 W). Sie bleibt als Vergleich liegen.

Wiederholen:
```
bash src/leistung_messen.sh        # im macOS-Terminal, fragt nach dem Mac-Passwort
```

## Unterbrechbarkeit (gemessen, Test 21:23)
- `SIGSTOP`: Prozessstatus T, während 5 s kein neuer Block → Pause wirkt sofort, Speicher bleibt belegt
- `SIGCONT`: Status R, rechnet weiter
- `SIGTERM`: rechnet den laufenden Block fertig, schreibt den Checkpoint bei 768/2048, beendet sich mit «Checkpoint bei 768, beendet» (vorgesehen ist Exit-Code 3, die Shell meldete nach der vorherigen Pause 145, beim Scheduler prüfen)
- Neustart mit demselben Ordner: macht bei 768 weiter und wird fertig
- **Vektoren nach Unterbruch und Neustart bit-genau gleich wie im ununterbrochenen Lauf** (max. Abweichung 0,0)
- Verlust bei Stopp am Checkpoint: höchstens ein Block (128 Texte ≈ 1,5 s)

## Skalierung auf den 1-kW-Referenzserver
- **Energieproportional:** Der Server schafft gleich viele Texte pro kWh wie der Laptop, bei 1 kW also ≈ 2'950 Texte/s.
- Konservativ: Ein GPU-Server rechnet Embeddings meist effizienter als eine Laptop-CPU, die echte Zahl dürfte höher liegen. Wir unterschätzen damit den Rechenertrag pro kWh, nicht die Wärme.
- Wärme hängt nur an der Leistung: 1 kW Strom → 0,8 kW nutzbare Wärme, unabhängig vom Durchsatz.

## Definition Jobtyp A (für den Scheduler)
| Merkmal | Wert | Herkunft |
|---|---|---|
| Inhalt | 10 Mio. Texte einbetten (z. B. Dokumentenarchiv für Suche) | eigene Definition |
| Energie | 0,941 kWh | gemessen (Laufzeit × powermetrics) |
| Laufzeit auf 1-kW-Server | 56,5 min | skaliert |
| Unterbrechbar | ja, Checkpoint alle 128 Texte | gemessen |
| Frist | 24 h (Batch, nächtliche Neuberechnung) | Annahme, passt zu wiederkehrenden Jobs im Alibaba-Trace (74 %) |

## Offen
- Messung auf ruhigem Rechner wiederholen (Systemlast lag noch bei 8)
- Jobtyp B (Transkription oder Bilderkennung) aus MLPerf ableiten
