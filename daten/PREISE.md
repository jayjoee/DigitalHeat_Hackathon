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
- Folgerung: Der Strom ist nicht der Engpass, die Spot-Preise liegen etwa 5- bis 15-mal darüber. Entscheidend sind Hardwarekosten, Abschreibung und Auslastung. Ein H100-Server kostet ein Vielfaches seines Stroms. Diese Zahl fehlt noch und gehört in die Bilanz, sonst ist die Aussage «rechnet sich» nicht belastbar.

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
