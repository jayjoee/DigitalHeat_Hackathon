# Messlauf auf dem vorhandenen Rechner

Modell: BAAI/bge-small-en-v1.5. Gleiche 2048 Texte pro Durchlauf. Wiederholungen: 3.

| Variante | Median Rechenzeit | Texte/s | Numerisch ähnlich | Chip-Energie (Rechnen) | Steckdose (Gesamtprozess) |
|---|---:|---:|---|---|---|
| Standard | 22.765 s | 90.0 | Ja | 0.17762 Wh (Chip-Schätzung) | Nicht gemessen |
| Weniger CPU-Threads | 57.330 s | 35.7 | Ja | 0.18434 Wh (Chip-Schätzung) | Nicht gemessen |
| Grössere Verarbeitungspakete | 33.393 s | 61.3 | Ja | 0.26206 Wh (Chip-Schätzung) | Nicht gemessen |

Die Messung zeigt Laufzeit und numerische Vergleichbarkeit. Ohne Leistungsdaten lässt sich daraus keine Energieeinsparung ableiten.
Der erste Lauf ist Referenz. Die Variantenreihenfolge wird pro Wiederholung mit fester Zufallssaat gemischt; Standard wird anfangs zuerst ausgeführt.
Kurze Durchläufe sind Funktionsprüfungen. Für eine Energieauswertung längere ruhige Messläufe und idealerweise ein externes Messgerät verwenden.

## Grenzen

- CPU-Test auf diesem Rechner, keine NVIDIA-L4-Messung.
- Weniger Threads ist kein GPU-Power-Cap und kein aktivierter macOS-Stromsparmodus.
- Grössere Batches lassen keinen Schluss auf ausgeschaltete Server zu. Kein automatisches Abschalten.
- powermetrics sind geschätzte Chip-Leistungswerte; Display, Netzteil und weitere Verbraucher fehlen.
- Ohne Leistungsmessung wird keine Energieersparnis berechnet.
- Numerischer Vektorvergleich ist keine Pharma- oder Retrieval-Qualitätsvalidierung.
- Andere laufende Programme und Temperatur beeinflussen die Ergebnisse.
