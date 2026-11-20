# Rechnen, das heizt – die Resultate einfach erklärt

## Die Idee
Ein Server braucht Strom und macht daraus fast vollständig Wärme. Normalerweise wird diese Wärme weggekühlt. Wir stellen die Server in den Keller eines Hauses: Sie rechnen KI-Aufträge und heizen dabei das Haus und das Warmwasser.

## Das Testhaus
- Einfamilienhaus in Basel, Wetter des ganzen Jahres 2025
- Braucht im Jahr **31'231 kWh Wärme** (Heizung 26'851 + Warmwasser 4'380)
- An den kältesten Tagen bis 10 kW Heizleistung
- Ein Wassertank speichert 35 kWh Wärme
- Ein Server: 1 kW Strom → 0,8 kW nutzbare Wärme

## Das Ergebnis: 8 Server pro Haus

| Kennzahl | Ergebnis | Was das heisst |
|---|---|---|
| Server pro Haus | **8** | |
| Wärmebedarf gedeckt | **93 %** | Nur 7 % muss die normale Heizung liefern, an den kältesten Tagen |
| Verschwendete Wärme | **5 kWh im Jahr** | Praktisch nichts wird weggekühlt |
| Auslastung | **52 %** | Die Server rechnen gut die Hälfte der Zeit |
| Verpasste Fristen | **0 %** | Jeder Auftrag mit Frist wird rechtzeitig fertig |
| Break-even-Preis | **0,23 CHF pro Server-Stunde** | Ab diesem Preis decken die Rechenerlöse den Strom (abzüglich Wert der Wärme) |

## Warum genau 8 Server?
- Mehr Server = mehr Wärme, aber jeder Server rechnet seltener.
- Bis 8 Server bringt jeder weitere Server viel zusätzliche Wärme. Ab dem 9. kaum noch.
- 12–13 Server würden 100 % decken, wären aber nur zu 35 % ausgelastet. Das lohnt sich nicht.

## Das Problem: der Sommer
- Im Winter laufen die Server fast pausenlos (96 % Auslastung).
- Im Sommer braucht das Haus nur Warmwasser, die Server laufen dann nur zu **8 %**.
- **Lösung:** Im Sommer gehen die Aufträge an Orte, die dann Wärme brauchen, etwa ein Hotel mit Spa oder eine Trocknungsanlage in der Landwirtschaft.

## Lohnt es sich?
- **Der Strom ist nicht das Problem.** Schon ab 0,23 CHF pro Server-Stunde rechnet es sich. Rechenzeit wird heute für etwa 1–4 CHF pro Stunde verkauft.
- **Entscheidend sind die Kosten der Hardware.** Bei einem Rechenpreis von 1,06 CHF pro Stunde darf ein Server höchstens rund **3'800 CHF pro Jahr** kosten.
- **Es lohnt sich NICHT, wenn:**
  - der Rechenpreis unter 0,23 CHF pro Stunde fällt, oder
  - die Hardware teurer ist, als die Erlöse hergeben, oder
  - es nicht genug flexible Aufträge gibt. Dann deckt das System nur 52 % und muss im Sommer Wärme wegkühlen.

## Welche Aufträge passen?
| Auftrag | Dauer | Unterbrechbar | Frist | Herkunft der Zahlen |
|---|---|---|---|---|
| Texte für eine Suche aufbereiten (Embeddings) | ca. 1 h | ja | 24 h | **selbst gemessen** auf dem Laptop |
| Bilder auf Objekte prüfen | ca. 7 min | nein | 2 h | MLPerf-Messungen eines Servers |

- Gut passen Aufträge, die **warten können** und sich **pausieren lassen**. Sie werden dann gerechnet, wenn das Haus Wärme braucht.
- Eilige Aufträge laufen sofort. Wird ihre Wärme nicht gebraucht, landet sie im Speicher oder der Auftrag geht an einen anderen Standort.

## Echt getestet
- Ein echter KI-Auftrag läuft auf dem Laptop: 85 Texte pro Sekunde bei 28,9 Watt (gemessen).
- Der Scheduler pausiert und startet ihn je nach Wärmebedarf:
  - **Januar:** Das Haus braucht viel Wärme, der Auftrag läuft durchgehend.
  - **Juli:** Der Speicher ist voll, der Auftrag läuft nur 62 % jeder Stunde und ist sonst pausiert.
- Nach einem Stopp macht der Auftrag genau dort weiter, wo er aufgehört hat. Das Ergebnis ist identisch.

## Wichtigste Annahmen
- Es gibt immer genug Rechenaufträge zu kaufen (Spot-Markt). Ohne diese Annahme sinkt die Deckung auf 52 %.
- Strompreis 33,25 Rp./kWh (IWB Basel 2026). Die Wärme ist 13,3 Rp./kWh wert, weil sie eine Wärmepumpe ersetzt.
- Rechenpreis rund 1,06 CHF pro Server-Stunde (günstigster Marktpreis, 1 $ = 0,84 CHF).
- Hardwarekosten sind nicht eingerechnet, sondern als Grenze angegeben.

## In einem Satz
**8 Server pro Haus decken 93 % der Wärme und verschwenden fast nichts. Es lohnt sich, wenn ein Server weniger als rund 3'800 CHF pro Jahr kostet und es im Sommer einen zweiten Wärmeabnehmer gibt.**
