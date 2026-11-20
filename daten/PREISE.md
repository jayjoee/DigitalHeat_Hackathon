# Rechenpreise (Recherche 20.11.2026)

Alle Preise in USD, Region US East, wenn nicht anders vermerkt. Quellen sind zum Teil Vergleichsseiten und widersprechen sich. Vor der Präsentation die Werte für die Kennzahlen an der offiziellen Preisseite prüfen.

## GPU-Stunde

| Angebot | On-Demand | Spot / unterbrechbar | Quelle |
|---|---|---|---|
| AWS g6.xlarge (1× L4) | 0.80 $/h | 0.35–0.45 $/h (US), Unterbruchrate 10–20 % | doit.com, holori.com |
| AWS p5.4xlarge (1× H100) | 6.88 $/h | – | thundercompute.com |
| AWS p5.48xlarge (8× H100) | 55.04 $/h (6.88 $/GPU-h) | – | thundercompute.com, wring.co |
| Azure ND H100 v5 | ≈ 12.29 $/GPU-h | – | intuitionlabs.ai |
| Google a3-highgpu-8g | ≈ 11.06 $/GPU-h | 1.57–3.69 $/GPU-h (preemptible) | intuitionlabs.ai, spheron.network |
| Spezialanbieter H100 (Runpod, Lambda, Jarvislabs, Nebius …) | 2.00–4.50 $/GPU-h | 0.79–2.50 $/GPU-h | spheron.network, jarvislabs.ai |
| Marktmedian H100 | 3.61 $/GPU-h (Mai 2026), 4.20 $/GPU-h (Okt. 2026) | – | Vergleichsseiten, s. unten |

Spot gilt als 40–65 % günstiger als On-Demand und passt zu unterbrechbaren Batch-Jobs. Unser Modell verkauft im Kern Spot-Kapazität: Rechnen nur, wenn Wärme gebraucht wird.

## Preise pro Job (Dienste mit Abrechnung pro Einheit)

| Dienst | Preis | Quelle |
|---|---|---|
| Bilderkennung, AWS Rekognition DetectLabels | 1.00 $ pro 1'000 Bilder (erste 1 Mio.), danach 0.80, 0.60 … | aws.amazon.com/rekognition/pricing |
| Transkription, Amazon Transcribe | Batch 0.006 $/min, Streaming 0.01 $/min (Rechenbeispiel auf der AWS-Seite, Stufentabelle nicht gelesen) | aws.amazon.com/transcribe/pricing |
| Embeddings, OpenAI text-embedding-3-small | 0.02 $ pro 1 Mio. Tokens, Batch ≈ 0.01 $ | developers.openai.com, openrouter.ai |

Diese Preise enthalten Plattform, Marge und Mengenrabatte. Sie gelten pro Ergebnis, nicht pro Rechenstunde, und eignen sich nicht als Erlös pro Serverstunde. Beispiel: RetinaNet schafft auf 8× H100 NVL rund 11'100 Bilder/s bei 4,85 kW (MLPerf v5.0). Zum Rekognition-Preis wären das Tausende Dollar pro kWh, was kein Markt zahlt. Für die Bilanz deshalb mit dem GPU-Stundenpreis rechnen und die Jobpreise nur als Obergrenze nennen.

## Umrechnung auf den 1-kW-Referenzserver (Annahme, prüfen)

- MLPerf v5.0: 8× H100 NVL ziehen gemessen rund 4,85 kW, also ≈ 0,6 kW pro GPU samt Host → **1 kW ≈ 1,6 H100-GPU**
- MLPerf v5.1: 8× B200 ziehen 7,6–10,4 kW, also ≈ 1,0–1,3 kW pro GPU → 1 kW ≈ 0,8–1 B200
- Erlösspanne pro Serverstunde mit 1,6 H100-Äquivalenten:
  - Spot 0,79–2,50 $/GPU-h → **≈ 1,3–4,0 $/Server-h**
  - On-Demand Spezialanbieter 2,00–4,50 $/GPU-h → ≈ 3,2–7,2 $/Server-h
  - On-Demand AWS 6,88 $/GPU-h → ≈ 11 $/Server-h
- Wechselkurs USD → CHF: noch festlegen (Quelle und Stichtag angeben)

## Erster Vergleich mit den Energiekosten (nur Strom, ohne Hardware)

- Strom pro Serverstunde: 1 kWh × 0,3325 CHF = **0,33 CHF**
- Wärmewert, wenn alles genutzt wird: 0,8 kWh × 0,133 CHF = **0,11 CHF**
- Energetischer Break-even: ≈ **0,23 CHF pro Serverstunde**, wenn die Wärme vollständig genutzt wird. Wird die Wärme abgeführt, steigt er auf 0,33 CHF.
- Folgerung: Der Strom ist nicht der Engpass, die Spot-Preise liegen etwa 5- bis 15-mal darüber. Entscheidend sind Hardwarekosten, Abschreibung und Auslastung. Ein H100-Server kostet ein Vielfaches seines Stroms. Diese Zahl steht deshalb jetzt in der Bilanz (nächster Abschnitt).

## Hardware (Recherche 20.11.2026)

| Grösse | Wert | Quelle |
|---|---|---|
| H100 NVL 94 GB, PNY-Karte | 32'382.99 $, Stand 21.09.2026, als «Discontinued» markiert | CDW-Listing, zitiert auf gpuperhour.com |
| H100 NVL 94 GB | ab 24'500 $ pro GPU (2026, ohne Datum) | fluence.network |
| H100 PCIe 80 GB | 25'000–30'000 $, Marktpreise oft 30'000–38'000 $ | fluence.network, jarvislabs.ai |
| Abschreibung Server | Amazon 5 Jahre, Microsoft und Alphabet 6 Jahre, Meta 5,5 Jahre | Geschäftsberichte, zitiert bei fortune.com (15.04.2026) und siliconangle.com (22.11.2025) |

NVIDIA veröffentlicht keine Listenpreise, die Händlerpreise streuen. **Im Modell:** 25'000 $ pro GPU (untere Spanne), 1,6 GPU pro 1-kW-Server, 0,84 CHF/$, 5 Jahre. Das ergibt

**25'000 × 1,6 × 0,84 ÷ 5 = 6'720 CHF pro Server und Jahr.**

Nicht eingerechnet sind Host (CPU, RAM, Netzteil), Flüssigkühlung und Wärmetauscher, Wartung, Internetanschluss und Kapitalkosten. Die echte Zahl liegt also eher höher. 5 statt 6 Jahre, weil eine GPU-Generation heute nach 2–3 Jahren überholt ist (siehe die Debatte bei fortune.com).

Folge für 8 Server (Spot, 36'290 Server-h): Nötig sind **(Strom − Wärmewert + Hardware) ÷ Server-h = (12'066 − 3'861 + 8 × 6'720) ÷ 36'290 = 1,71 CHF pro Server-h**, also 1,27 $ pro H100-Stunde. Das liegt in der Spot-Spanne (0,79–2,50 $), aber über dem günstigsten Preis, mit dem bisher gerechnet wurde (0,79 $).

Quellen:
- https://gpuperhour.com/blog/nvidia-h100-price
- https://www.fluence.network/blog/nvidia-h100-deep-dive/
- https://jarvislabs.ai/blog/h100-price
- https://fortune.com/2026/04/15/data-centers-hyperscalers-spending-billions-on-hardware-thats-worthless-in-3-years/
- https://siliconangle.com/2025/11/22/resetting-gpu-depreciation-ai-factories-bend-dont-break-useful-life-assumptions/

## Quellen
- https://www.thundercompute.com/blog/ec2-gpu-instances
- https://wring.co/blog/aws-gpu-instance-pricing-guide
- https://www.doit.com/compute/spot/us-east-1/g6.xlarge
- https://calculator.holori.com/aws/ec2/g6.xlarge/us-east-1
- https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison
- https://www.spheron.network/blog/gpu-cloud-pricing-comparison-2026/
- https://jarvislabs.ai/blog/h100-price
- https://aws.amazon.com/rekognition/pricing/
- https://aws.amazon.com/transcribe/pricing/
- https://developers.openai.com/api/docs/models/text-embedding-3-small
- https://openrouter.ai/openai/text-embedding-3-small%3Abatch
