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
| Wärmebedarf gedeckt | **93 %** | Die restlichen 7 % liefert der Holzofen, den viele ältere Häuser schon haben, nur an den kältesten Tagen. Öl braucht es keines mehr. |
| Abgeführte Wärme | **5 kWh im Jahr im Case-Idealmodell** | Das Modell setzt 0 W bei pausierten Servern an |
| Auslastung | **52 %** | Die Server rechnen gut die Hälfte der Zeit |
| Verpasste Fristen | **0 %** | Jeder Auftrag mit Frist wird rechtzeitig fertig |
| Break-even-Preis | **0,23 CHF pro Server-Stunde** | Ab diesem Preis decken die Rechenerlöse den Strom (abzüglich Wert der Wärme) |

**Jobs pausieren oder Server abschalten?** Bei angenommenen 230 W Leerlauf fallen beim Pausieren im Modell rund 4’200 kWh ungenutzte Wärme an. Gezieltes Abschalten spart im Vergleich rund 5’200 kWh Strom pro Jahr. Die Wärmedeckung sinkt dabei von 91,3 % auf 90,5 %. Die Verbrauchswerte der L4-Server müssen im Pilot gemessen werden. [Rechnung und Bandbreite](ERGEBNISSE.md#leerlauf-und-abschalten-im-referenzhaus)

## Warum genau 8 Server?
- Mehr Server = mehr Wärme, aber jeder Server rechnet seltener.
- Bis 8 Server bringt jeder weitere Server viel zusätzliche Wärme. Ab dem 9. kaum noch.
- 12–13 Server würden 100 % decken, wären aber nur zu 35 % ausgelastet. Das lohnt sich nicht.

## Das Problem: der Sommer
- Im Winter laufen die Server fast pausenlos (96 % Auslastung).
- Im Sommer braucht das Haus nur Warmwasser, die Server laufen dann nur zu **8 %**.
- **Lösung:** Im Sommer gehen die Aufträge an Orte, die dann Wärme brauchen. In Basel ist das das **Sportbad St. Jakob**: ein beheiztes 50-m-Becken, offen von Ende April bis Anfang Oktober, also genau dann, wenn die Häuser keine Wärme brauchen. Ein Hallenbad passt nicht, denn das Rialto macht im Sommer Pause.

## Der Wärme-Router: 20 Häuser und ein Sportbad
- Alle Aufträge kommen in einen gemeinsamen Topf. Jede Stunde verteilt der **Wärme-Router** sie dorthin, wo die Wärme gebraucht wird.
- **Die Häuser haben immer Vorrang.** Das Bad bekommt nur Arbeit, deren Wärme gerade kein Haus brauchen kann.
- An beiden Standorttypen simuliert der Router das Ein- und Ausschalten. Ausserhalb der Saison bleiben die Bad-Server im Standby.
- Bei knapper Nachfrage gehen ohne Bad rund **195’000 Serverstunden** an andere Clouds. Mit 50 Servern im Bad sind es rund **30’000**. Das verbessert das Jahresergebnis um rund **66’600 CHF**.
- Die 50 Bad-Server stammen aus dem Vergleich im Case-Idealmodell. Bei ausreichenden Aufträgen könnte das Bad mehr Rechenlast aufnehmen. [Ergebnisse des Abschaltmodells](ERGEBNISSE.md#flotte-mit-bedarfsgerechtem-abschalten)
- **Ehrlich:** Wenn es nur Aufträge mit Frist gibt, macht die Flotte trotzdem Verlust, weil Aufträge fehlen und nicht Wärme. Der Router verteilt die Arbeit besser, er schafft aber keine neue. Entscheidend bleibt der feste Vertrag mit Pharma, Banken und Spitälern.

## Planbar: die Zusage am Vortag
- Pharma zahlt 0,60 CHF nur für Stunden, die DigitalHeat **am Vortag um 12 Uhr verbindlich zusagt**.
- Die Zusage stützt sich auf die Wetterprognose vom Vortag (ECMWF). Im Test zählen nur Prognosen, die um 12 Uhr schon veröffentlicht waren.
- Ergebnis Referenzhaus: **93 % der Stunden lassen sich zusagen**, verkauft werden 60 %. An rund 2 % der Tage fehlt etwas. Dafür gibt es eine Gutschrift, die rund 270 CHF pro Jahr kostet.
- Damit bleibt das Ergebnis bei **34'300 CHF pro Haus und Jahr**. Der Preis ist also nicht nur angenommen, sondern abgesichert.

## Lohnt es sich?
- **Der Strom ist nicht das Problem.** Nur für Strom (abzüglich Wärmewert) reichen schon 0,23 CHF pro Server-Stunde.
- **Entscheidend sind die Computer.** DigitalHeat kauft pro Haus 8 Server mit je 8 Grafikkarten (NVIDIA L4) und investiert dafür mit Einbau rund **290'000 CHF**.
- Die Kunden sind Firmen, deren Daten in der Schweiz bleiben müssen: Pharma, Banken, Spitäler. Sie zahlen DigitalHeat **0,60 CHF pro Grafikkarte und Stunde**, rund 12 % weniger als bei anderen Schweizer Clouds (ab 0,68 CHF).
- Damit bleiben DigitalHeat nach allen Kosten, Steuern und Zinsen rund **34'500 CHF pro Haus und Jahr**. Das Geld für die Computer ist nach **3 Jahren** zurück, die Rendite liegt bei rund **21 %**. Mit 100 Häusern rund 3,5 Mio. CHF pro Jahr.
- Vorsichtig gerechnet mit 0,50 CHF sind es noch rund 20'300 CHF pro Haus und Jahr.
- Der Haushalt bekommt die **Wärme gratis**.
- **Es lohnt sich NICHT, wenn:**
  - der Preis unter **0,36 CHF pro Grafikkarte und Stunde** fällt, oder
  - weniger als rund 40 % der Stunden fest verkauft werden, oder
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
  - **7. März:** Am Nachmittag ist der Speicher voll. Der Auftrag pausiert 7 Stunden lang und rechnet am Abend weiter, sobald das Haus wieder Wärme braucht.
- Nach einem Stopp macht der Auftrag genau dort weiter, wo er aufgehört hat. Das Ergebnis ist identisch.

- **Der Job wandert echt.** Am 25. Mai rechnet der echte Auftrag bis 10 Uhr im Haus. Dann ist der Wassertank voll, und der Router schickt ihn ins Sportbad. Der Auftrag speichert seinen Stand, ein neuer Prozess macht dort weiter. Ein Vergleich mit einem Lauf ohne Unterbruch ergibt exakt dieselben Ergebnisse.

## Wichtigste Annahmen
- Es gibt genug Rechenaufträge: Eine Pharmafirma bucht 60 % der Stunden fest, der Rest wird günstiger verkauft. Ohne genug Aufträge sinkt die Deckung auf 52 %.
- Strompreis 33,25 Rp./kWh (IWB Basel 2026). Die Wärme ist 13,3 Rp./kWh wert, weil sie eine Wärmepumpe ersetzt (Case-Regel).
- Ein Server mit 8 Grafikkarten kostet 32'245 CHF und hält 5 Jahre. Alle Beträge in CHF, Herleitung in `KOSTEN_DH.md`.
- Der Wärmebedarf des Sportbads ist geschätzt: rund 650'000 kWh im Jahr, auf ±30 % genau (Kennwert des Verbands Hallen- und Freibäder, `daten/HALLENBAD.md`).

## In einem Satz
**8 Server pro Haus decken 93 % der Wärme, und der Haushalt bekommt sie gratis. Im Sommer schickt der Wärme-Router die Arbeit ins Sportbad, statt sie zu verschenken. Als Schweizer Cloud mit verbindlicher Zusage am Vortag verdient DigitalHeat rund 34'300 CHF pro Haus und Jahr und hat die Investition nach 3 Jahren zurück.**
