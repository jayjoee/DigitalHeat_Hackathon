# Alibaba PAI GPU Trace 2020 – Auswertung für DigitalHeat

Reproduzierbar mit `python3 src/alibaba_analyse.py` (Rohdaten in `daten/roh/alibaba/`, Zahlen in `daten/alibaba_auswertung.json`). Quelle: Weng et al., «MLaaS in the Wild», NSDI ’22. Tabellen: job, task, group_tag, machine_spec, sensor (SHA-256 geprüft).

## Was der Trace ist
- Produktivcluster von Alibaba PAI, Juli–August 2020, **68,9 Tage**
- **1'897 Maschinen, 6'742 GPUs**: ältere Typen (K40/K80/M60 als MISC 2'240, P100 1'596, V100 1'912, T4 994)
- Gemischt Training und Inferenz, nur 12 % der Jobs haben ein Workload-Tag
- Status: 732'355 erfolgreich (69 %), 256'555 fehlgeschlagen (24 %), Rest laufend oder wartend

## Kernzahlen (erfolgreiche Jobs mit GPU)

**Ankünfte**
- **≈ 15'300 Jobs pro Tag** (Tag p10 8'050, Median 15'270, p90 20'660)
- Über den Tag fast flach: höchste Stunde 7 % (00 Uhr UTC+8), tiefste 3 %. Wochentage 13–16 %, kein Wochenendloch
- → **2,3 Jobs pro GPU und Tag**, auf den 1-kW-Server (≈ 1,6 GPU) **≈ 3,6 Jobs pro Server und Tag**

**Laufzeit** (Minuten): p10 0,7 · p25 2,4 · **Median 10,8** · p75 65 · p90 216 · p99 1'157

| Laufzeit | Anteil Jobs | Anteil GPU-Stunden |
|---|---|---|
| < 1 min | 14,6 % | 0,0 % |
| 1–10 min | 34,2 % | 0,7 % |
| 10–60 min | 25,0 % | 5,5 % |
| 1–4 h | 17,2 % | 16,6 % |
| 4–24 h | 8,3 % | 46,9 % |
| > 24 h | 0,7 % | 30,2 % |

- **74 % der Jobs laufen unter einer Stunde, tragen aber nur 6 % der GPU-Stunden.**
- **77 % der GPU-Stunden stecken in Jobs über 4 h.** Die Wärme kommt also aus den langen Jobs. Sie müssen pausierbar sein (Checkpoint), sonst lassen sie sich nicht nach dem Wärmebedarf steuern.

**GPU-Bedarf pro Job**: Median 1 GPU, p90 5, p99 30. 37 % fordern nur einen Bruchteil einer GPU an.

**Nachfrage gegen Kapazität**: 68'083 GPU-Stunden pro Tag angefordert = **42 % der Kapazität**. Selbst im Rechenzentrum steht mehr als die Hälfte der GPU-Zeit leer.

**Tatsächliche Nutzung** (Sensor, 2,0 Mio. Instanzen): GPU-Auslastung Median **4 %**, p75 14 %, p90 38 %. Gewichtet nach GPU-Stunden werden **32 % der angeforderten GPU** wirklich genutzt.

**Wiederkehrende Last**: 74 % der Instanzen gehören zu Gruppen mit wiederholten Läufen (gleiches Skript, gleiche Daten).

**Wartezeit**: im Trace nicht messbar (Job-Start und erster Task-Start fallen praktisch zusammen, p99 = 0).

## Workloads mit Tag

| Workload | Jobs | Laufzeit Median | Laufzeit p90 | GPU Median | GPU-h total |
|---|---|---|---|---|---|
| BERT (Sprache) | 45'550 | 15 min | 263 min | 1 | 280'144 |
| CTR (Empfehlung) | 25'270 | 21 min | 156 min | 2 | 134'765 |
| NMT (Übersetzung) | 8'732 | 151 min | 265 min | 1 | 80'597 |
| Inception (Bild) | 5'220 | 6 min | 35 min | 25 | 39'271 |
| GraphLearn | 1'534 | 64 min | 524 min | 8 | 67'078 |
| XLNet | 335 | 220 min | 617 min | 2 | 4'134 |
| ResNet (Bild) | 296 | 20 min | 482 min | 2,25 | 7'033 |

## Folgerungen für den Case

1. **Jobankünfte begründen (Muss-Kriterium 1):** Als belegte Ausgangszahl dienen 2,3 Jobs pro GPU und Tag bzw. ≈ 3,6 pro 1-kW-Server, mit Median 11 min und langem Schwanz. Für unsere eigenen Inferenz-Jobtypen wird daraus eine Ankunftsrate mit Verteilung, statt «unbegrenzt viele Jobs».
2. **Wärme kommt aus langen, pausierbaren Jobs.** Kurze Jobs füllen Lücken, lange Batch-Jobs mit Checkpoints tragen die Grundlast. Das spricht für Batch-Inferenz (Embeddings eines Archivs, Transkription von Archiven, Bild-Tagging) mit Fristen von Stunden bis Tagen.
3. **Wärme ≠ Nennleistung.** Bei 4 % GPU-Auslastung im Median gibt ein Server nur einen Bruchteil seiner Nennleistung als Wärme ab. Der Scheduler muss Jobs **verdichten** (mehrere pro Server, grosse Batches), damit 1 kW Strom wirklich zu 0,8 kW Wärme wird. Das zeigt auch: Wärme muss aus der gemessenen Leistung gerechnet werden, nicht aus «Server an».
4. **Spielraum ist vorhanden.** Die Nachfrage liegt bei 42 % der Kapazität, und die Ankünfte sind über Tag und Woche gleichmässig. Die Flexibilität kommt also nicht aus Lastspitzen, sondern aus den Fristen: Jobs mit Frist > 12 h lassen sich in die Stunden mit Wärmebedarf schieben.
5. **Wiederkehrende Jobs sind planbar.** Bei 74 % Wiederholungen lässt sich die Last mit der Wetterprognose vorausplanen (z. B. nächtliche Neuberechnung von Embeddings).
6. **Risiko Fehlschläge:** 24 % der Jobs schlagen fehl. Für den Erlös zählt nur verkaufte, erfolgreiche Rechenzeit, die Bilanz muss das berücksichtigen.

## Grenzen
- Trace von 2020 mit älteren GPUs, Training und Inferenz gemischt. Laufzeiten heutiger Inferenz auf H100/L4 sind kürzer.
- Ein Cluster bei einem Anbieter in China, Ankunftszeiten in UTC+8. Für Basel nicht 1:1 übertragbar, nur als Form der Verteilung verwendet.
- Sensorwerte sind Mittelwerte über die Lebensdauer einer Instanz, keine Zeitreihe.
- Zuordnung GPU → 1-kW-Server (≈ 1,6 GPU) ist eine Annahme aus MLPerf (siehe `PREISE.md`).
- Nicht geladen: instance (663 MB) und machine_metric (198 MB). Sie bräuchte man nur für die Maschinenauslastung pro Zeit.
