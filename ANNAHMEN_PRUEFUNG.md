# Kritische Prüfung aller Annahmen (Stand 21.11.2026)

Joëls Modell war als schnelle Übersicht gedacht. Hier wird jede Annahme einzeln geprüft: Woher kommt sie, hält sie, und was ändert sich, wenn nicht?

**Legende:** ✓ hält · ⚠ schwach, Folgen benennen · ✗ falsch oder fehlt, ändert das Ergebnis
**Herkunft:** *Case* = vom Case vorgegeben (für die Pflichtzahlen nicht ändern, aber Grenzen nennen) · *Team* = selbst gesetzt

## Die sechs wichtigsten Befunde

1. **✗ Pausierte Server verbrauchen im Modell keinen Strom.** Gemessen braucht ein 8-GPU-H100-Server im Leerlauf 1,86 kW, unter Last 7,92 kW (Median), also rund 23 % (Latif et al. 2024, Tabelle 1). Mit 23 % Leerlauf bei 8 Servern: **+4'650 kWh Strom (+1'550 CHF) pro Jahr und 3'720 kWh abgeführte Wärme statt 5 kWh**, davon 2'150 kWh im Sommer. Die Leerlaufwärme der 8 Server (1,5 kW) ist allein schon dreimal so gross wie der Warmwasserbedarf im Sommer (0,5 kW). **Folge:** Der Scheduler muss Server ganz ausschalten, nicht nur den Prozess pausieren. Sonst stimmt «fast keine Abwärme» nicht.
2. **✗ Unbegrenzte Spot-Nachfrage (Szenario Spot) ist die stärkste Annahme.** Ohne sie sinkt die Deckung bei 8 Servern auf 52 %. Dazu kommt: Der Rechenpreis ist ein Preis, den *Kunden* bei Cloud-Anbietern zahlen. DigitalHeat als Lieferant erhält weniger, denn Marktplatz-Gebühren, Netz und Leerzeiten zwischen Aufträgen fehlen im Modell.
3. **⚠ Die Hardware passt nicht zum Betrieb.** Neue H100 sind für 24/7-Rechenzentren gebaut. Bei DH laufen die Server nur rund 4'500 von 8'760 Stunden. Mit dieser Laufzeit sind gebrauchte oder kleine Inferenz-GPUs deutlich wirtschaftlicher (siehe Serververgleich unten).
4. **⚠ 2025 war für den Winter ein mildes Jahr.** Die kälteste Stunde lag bei −5,6 °C. In den Jahren 2010–2025 lag sie zwischen −4,6 und −17,5 °C. Mit derselben Case-Formel schwankt die Deckung der 8 Server zwischen **84,5 % und 95,9 %**, die Spitzenlast bis **14,6 kW** statt 10 kW (Tabelle unten). Die Backup-Heizung muss also deutlich grösser sein, als das Referenzjahr vermuten lässt.
5. **✗ Wichtige Kosten fehlen ganz:** Host (CPU, RAM, Netzteil), Einbau mit Wärmetauscher, Wartung, Versicherung, Internet, Kapitalkosten. Alle machen DH teurer, als das Modell zeigt.
6. **⚠ Der Wärmewert ist niemandem zugeordnet.** Das Modell schreibt DH den vollen Wärmewert gut (13,3 Rp./kWh). Wenn DH die Wärme so teuer verkauft, spart der Hausbesitzer aber nichts gegenüber einer Wärmepumpe. Den Wärmepreis müssen die Gruppen DH und Hausbesitzer gemeinsam festlegen.

## Alle Annahmen einzeln

### Haus und Wetter

| Annahme | Wert | Herkunft | Prüfung | Urteil |
|---|---|---|---|---|
| Wetter Basel 2025, Open-Meteo | 8'760 h | Case | Unabhängig nachgeladen, Stunde für Stunde identisch. 206 Heiztage, 26'851 kWh | ✓ |
| Heizformel max(0, 10 × (20 − T) ÷ 25,6) | linear, ohne Sonne, ohne Gebäudemasse | Case | Bewusst einfach. Sonnengewinne und träge Wände fehlen | ✓ für die Pflichtzahlen, Grenze nennen |
| Nur ein Wetterjahr | 2025 | Case | 2010–2025 nachgerechnet: Deckung 84,5–95,9 %, Spitze 9,6–14,6 kW | ⚠ zusätzlich zeigen |
| Warmwasser 12 kWh/Tag, gleichmässig 0,5 kW | | Case / Team | In Wirklichkeit Spitzen morgens und abends. Der Speicher gleicht das aus, kleiner Effekt | ✓ |
| Speicher 35 kWh, verlustfrei | | Case | Echte Speicher verlieren Wärme. Gerechnet: 8-facher Speicher bringt nur +2 Prozentpunkte | ✓, Speicher ist nicht der Engpass |

**Wetterjahre im Vergleich (8 Server, gleiche Case-Formel):**

| Jahr | Heiztage | Gesamtbedarf kWh | Kälteste Stunde | Deckung | Auslastung | Spitze kW |
|---|---|---|---|---|---|---|
| 2010 | 213 | 36'748 | −16,4 °C | 84,5 % | 55,4 % | 14,2 |
| 2012 | 197 | 33'009 | −17,5 °C | 88,5 % | 52,0 % | 14,6 |
| 2014 | 187 | 28'560 | −8,3 °C | 95,9 % | 48,9 % | 11,1 |
| 2021 | 221 | 34'593 | −14,7 °C | 91,7 % | 56,7 % | 13,6 |
| 2024 | 190 | 29'005 | −7,1 °C | 94,5 % | 48,8 % | 10,6 |
| **2025** | **206** | **31'231** | **−5,6 °C** | **92,9 %** | **51,8 %** | **10,0** |

Alle 16 Jahre mit Open-Meteo-Archivdaten gerechnet. Die Tabelle zeigt eine Auswahl.

### Strom und Wärme

| Annahme | Wert | Herkunft | Prüfung | Urteil |
|---|---|---|---|---|
| Strompreis IWB H4 2026 | 33,25 Rp./kWh | Case | ElCom-API bestätigt. H4 = Haushalt mit 4'500 kWh/Jahr. Die Server brauchen 36'000 kWh, das liegt näher am Kleingewerbe (C2, rund 30'000 kWh): **32,745 Rp.**, fast gleich | ✓ |
| Wärmewert = Strompreis ÷ 2,5 | 13,3 Rp./kWh | Case | Ein Einfamilienhaus mit Wärmepumpe fällt vermutlich in die ElCom-Kategorie H7 (Definition noch prüfen): bei IWB **28,5 Rp./kWh** → Wärmewert 11,4 Rp. (−14 %) | ⚠ Case-Wert behalten, Grenze nennen |
| MwSt. im Strompreis | unklar | – | Nicht geklärt, ob die ElCom-Werte die MwSt. enthalten. Für DH als Firma wäre sie abziehbar | ⚠ offen |
| 80 % der Wärme nutzbar | | Case | DH nennt keine Zahl (Website) | ✓ Case |
| Pausierter Server braucht 0 kW | | Team | **Gemessen rund 23 % der Last** (Latif et al. 2024) | ✗ siehe Befund 1 |
| «Läuft ein Server, läuft er voll» | 1 kW | Team | Alibaba-Trace: GPUs im Median nur 4 % ausgelastet, gewichtet 32 % der angeforderten Leistung genutzt | ⚠ nur mit dicht gepackten Aufträgen |

### Server und Hardware

| Annahme | Wert | Herkunft | Prüfung | Urteil |
|---|---|---|---|---|
| 1 kW ≈ 1,6 H100 | MLPerf, 8× H100 NVL = 4,85 kW | Team | Gilt für PCIe-Karten bei Inferenz. Ein H100-SXM-Server braucht beim Training 7,9 kW für 8 GPUs, also ≈ **1 GPU pro kW** | ⚠ hängt vom Servertyp ab |
| H100 NVL 25'000 $ pro GPU | untere Spanne | Team (Jin) | Quellen 24'500–32'383 $ (Karte gilt als auslaufend) | ⚠ ohne Host, eher zu tief |
| Abschreibung 5 Jahre | | Team (Jin) | Hyperscaler 5–6 Jahre. Für GPUs wird kürzer diskutiert | ⚠ |
| Wechselkurs 0,84 CHF/$ | «Angabe Joël» | Team | Mitte November 2026 ≈ 0,839 (mehrere Kursquellen) | ✓, Quelle ersetzen |

### Aufträge und Messung

| Annahme | Wert | Herkunft | Prüfung | Urteil |
|---|---|---|---|---|
| Job A gemessen: 85,4 Texte/s bei 28,9 W | | Team | Aus dem Messlog reproduziert. Nur Chip-Leistung (CPU+GPU+ANE), ohne RAM und Netzteil | ✓ |
| Skalierung auf 1 kW: gleich viele Texte pro kWh wie der Laptop | | Team | Passt nicht zum H100-Server, mit dem der Preis gerechnet wird. Ändert nur die Zahl der Texte, nicht Wärme und Geld | ⚠ harmlos, aber erklären |
| Job B: MLPerf RetinaNet, 1 Mio. Bilder = 0,121 kWh | | Team | Nachgerechnet. MLPerf ist ein optimierter Bestwert (TensorRT), im Alltag eher mehr Energie | ✓ mit Hinweis |
| Fristen 24 h (A), 2 h (B) | | Team | Frei gesetzt, so gekennzeichnet. Mit Pharma-Kunde aus dessen Bedarf ableiten | ⚠ |
| Typ B = Anteil kurzer Jobs (6 % der GPU-Stunden) | | Team | Zuordnung «kurz = Bilderkennung» ist willkürlich | ⚠ |

### Nachfrage (Alibaba-Trace)

| Annahme | Wert | Herkunft | Prüfung | Urteil |
|---|---|---|---|---|
| 10,1 Server-h pro Server und Tag | 42 % der Kapazität | Team | Das sind **angeforderte** Stunden in einem Cluster von 2020 mit alten GPUs (K80, P100, V100). Auf heutigen GPUs dauert dieselbe Arbeit viel kürzer, und genutzt werden nur 32 % des Angeforderten. Es ist eine Auslastung, keine Marktnachfrage für DH | ⚠ als Vergleich, nicht als Nachfrage |
| Ankünfte nach Tagesform in UTC+8 | | Team | Nicht auf Basel umgerechnet (von Joël selbst vermerkt). Ankünfte fast flach, kleiner Effekt | ✓ |

### Preise

| Annahme | Wert | Herkunft | Prüfung | Urteil |
|---|---|---|---|---|
| Spot H100 0,79 $/GPU-h | tiefster Wert | Team | 0,79 $ ist ein Ausreisser («ab», preemptible). Andere Quellen nennen als tiefsten Spot-Preis 1,25–1,50 $. Gleichzeitig erhält DH als Anbieter weniger als den Kundenpreis | ⚠ beide Fehler gehen in entgegengesetzte Richtungen |
| Alle Server-Stunden werden voll verkauft | | Team | Keine Gebühren, keine Lücken zwischen Aufträgen, keine Ausfälle (Alibaba: 24 % der Jobs schlagen fehl) | ⚠ zu optimistisch |

### Wirtschaftlichkeit aus Sicht DigitalHeat

| Posten | Im Modell? | Stand |
|---|---|---|
| Strom | ja | ✓ |
| Hardware (Abschreibung) | ja, seit PR #1 | ⚠ ohne Host |
| Wärmeerlös | als «Wärmewert» | ⚠ Preis für den Hausbesitzer festlegen |
| Einbau, Wärmetauscher, Anschluss | nein | ✗ keine Quelle gefunden |
| Wartung, Versicherung, Internet | nein | ✗ keine Quelle gefunden |
| Leerlaufstrom | nein | ✗ siehe Befund 1 |
| Vorteil gegenüber Rechenzentrum | nein | Rechenzentren brauchen pro kWh Rechnen im Schnitt 0,54 kWh zusätzlich für Kühlung und Gebäude (PUE 1,54, Uptime Institute 2025). DH spart das. Gutes Argument, noch nicht in CHF gerechnet |

## Welcher Server passt zu DigitalHeat?

Rechnung pro 1 kW Server, 4'536 Laufstunden pro Jahr (Mittel der 8 Server), 5 Jahre Abschreibung, Strom minus Wärmewert 0,226 CHF/h.
*Pessimistisch* = hoher Kaufpreis, tiefer Mietpreis; *optimistisch* = umgekehrt. **Ohne Host, Einbau und Wartung, mit Kundenpreisen.** Die absoluten Zahlen sind deshalb zu gut, der Vergleich zwischen den Typen ist das Aussagekräftige.

| Typ | Karten pro kW | Kaufpreis pro Karte | Mietpreis pro Karte | Gewinn pro kW und Jahr | Break-even pro Karte |
|---|---|---|---|---|---|
| H100 NVL, neu | 1,6 (MLPerf) | 24'500–32'383 $ | 0,79–1,50 $/h | **−4'900 bis +1'400 CHF** | 1,27–1,60 $/h |
| A100 80 GB, gebraucht | ≈ 2,2 (Annahme: 300 W pro Karte plus Host-Anteil) | 4'000–9'000 $ | 0,68–1,29 $/h | **+1'300 bis +8'300 CHF** | 0,30–0,52 $/h |
| L4, neu | ≈ 8 (Annahme: 72 W pro Karte plus Host) | 2'000–3'000 $ | 0,35–0,87 $/h | **+5'600 bis +22'800 CHF** | 0,12–0,17 $/h |
| CPU-Server (2× EPYC) | ≈ 1 | keine belastbare Quelle gefunden | AWS c7a.48xlarge Spot 1,56–4,80 $/h | nicht gerechnet | – |

**Was man daraus lernt, auch wenn die Zahlen grob sind:**
- Bei halber Laufzeit zählen zwei Grössen: **wenig Kaufpreis pro kW** und **viel Erlös pro kWh**. Neue Top-GPUs schneiden bei beidem am schlechtesten ab.
- Kleine Inferenz-GPUs (L4) und gebrauchte A100 kommen viel früher in die Gewinnzone. Der Mietmarkt für sie ist aber kleiner, und gebrauchte Karten halten weniger lang.
- **GeForce-Karten (z. B. RTX 4090) sind keine Option:** NVIDIAs Treiberlizenz verbietet den Einsatz im Rechenzentrum, ausser für Blockchain. Ob ein Keller-Server-Netz als Rechenzentrum gilt, ist ungeklärt, das Risiko ist zu gross.
- Für den Pharma-Docking-Job reichen CPU-Server. Dafür braucht es noch einen belegten Serverpreis.

## Was jetzt zu tun ist

| # | Was | Wer | Aufwand |
|---|---|---|---|
| 1 | Leerlaufstrom ins Modell, Server ganz ausschalten statt nur pausieren | Modell | 30 min |
| 2 | Wärmepreis für den Hausbesitzer festlegen | Gruppen DH und Hausbesitzer | Entscheid |
| 3 | Vertragspreis und Aufträge des Pharma-Kunden statt Spot | Gruppe Pharma | Recherche |
| 4 | Servertyp wählen, Host- und Einbaukosten mit Quelle ergänzen | DH (Jin) | 1–2 h |
| 5 | Mehrere Wetterjahre im Dashboard zeigen (Referenzjahr bleibt 2025) | Modell | 30 min |
| 6 | Quelle für Wechselkurs statt «Angabe Joël» | Modell | 5 min |

Die Pflichtzahlen für das Referenzhaus bleiben bei den Case-Annahmen. Alles hier kommt zusätzlich dazu und gehört in «Wo die Annahmen nicht mehr gelten».

## Quellen

- Latif et al. (2024): Empirical Measurements of AI Training Power Demand on a GPU-Accelerated Node, https://arxiv.org/html/2412.08602v2 (Leerlauf 1,86 kW, Training 7,92 kW Median, Nennleistung 10,2 kW)
- ElCom Strompreis-API, IWB Basel 2026, Kategorien H4, H7, C2 (abgefragt 21.11.2026)
- Open-Meteo Archive API, Basel 47.56 N / 7.59 E, 2010–2025; Previous-Runs-API für Vortagsprognosen
- Uptime Institute Global Data Center Survey 2025 (PUE 1,54): https://intelligence.uptimeinstitute.com/resource/uptime-institute-global-data-center-survey-2025
- H100-Preise: https://gpuperhour.com/blog/nvidia-h100-price, https://www.fluence.network/blog/nvidia-h100-deep-dive/
- H100-Mietpreise: https://www.spheron.network/blog/h100-price-per-hour-2026/, https://tech-insider.org/what-renting-an-nvidia-h100-costs-per-hour-in-2026-and-when-renting-beats-buying/
- A100: https://jarvislabs.ai/blog/a100-price, https://www.amcompute.com/gpu-cloud-prices/a100-80gb, https://gpuperhour.com/rent/a100
- L4: https://jarvislabs.ai/blog/l4-gpu-price, https://getdeploying.com/gpus/nvidia-l4
- CPU-Server: https://instances.vantage.sh/aws/ec2/c7a.48xlarge, https://aws-pricing.com/c7a.48xlarge.html
- GeForce-Lizenz: https://www.nvidia.com/en-us/drivers/geforce-license, https://deeptalk.lambdalabs.com/t/nvidia-geforce-datacenter-ban-january-eula-change/138
- Wechselkurs: https://tradingeconomics.com/switzerland/currency/news/601255, https://therighttrader.com/convert/usd-to-chf
- Abschreibung: https://fortune.com/2026/04/15/data-centers-hyperscalers-spending-billions-on-hardware-thats-worthless-in-3-years/
