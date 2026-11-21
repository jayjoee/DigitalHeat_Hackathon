# Sicht des Kunden: Pharmafirma (Stand 21.11.2026)

**Aktualisierte Angebotsentscheidung:** Wir behalten L4 und verarbeiten nur öffentliche/synthetische oder bereits beim Kunden ausreichend anonymisierte und freigegebene Aufgaben. Vertrauliche Forschungsdaten sind ausgeschlossen. Die nachstehenden Marktgrössen und Preise sind Hintergrundszenarien; sie belegen keine zulässige oder zahlende öffentliche Nachfrage. Massgeblich ist [L4_ANGEBOT.md](L4_ANGEBOT.md).

**Alle Preise in CHF** (0,84 CHF/$). Da die Gruppe Pharma keine eigenen Ergebnisse hat, ist hier ihre Arbeit übernommen: Wer ist der Kunde, welche Aufträge hat er, wie viel zahlt er heute, welche Verträge sind üblich und welche Sicherheitsnachweise verlangt er? Am Ende stehen die Werte, die ins Modell gehören.

Grundlage: 8 Server pro Haus (64 L4-Karten), Jahressimulation Referenzhaus 2025, Kosten aus `KOSTEN_DH.md` (mittlerer Fall).

---

## 1. Wer der Kunde realistisch ist

| Kundentyp | Lage | Passt zu DH? |
|---|---|---|
| **Grosse Pharma** (z. B. Roche in Basel, Lilly) | Bauen eigene KI-Rechenzentren: Roche hat über 3'500 GPUs in einer hybriden Cloud (März 2026), Lilly 1'016 Blackwell-Ultra-GPUs | Nur für **Lastspitzen im Winter** und als **Nachhaltigkeitsprojekt**. Die Grundlast rechnen sie selbst |
| **Mittelgrosse Pharma und Biotech** ohne eigenes Rechenzentrum | Mieten Rechenzeit in der Cloud | **Hauptkunde.** Sie zahlen heute Cloud-Preise und würden für einen tieferen, planbaren Preis wechseln |
| **Hochschulen und Forschungsinstitute** (Life Sciences) | Eigene Cluster, oft ausgelastet | Ergänzung, vor allem für Batch-Rechnungen |

**Folge:** Pharma ist ein möglicher Ankerkunde für ausdrücklich zulässige Workflows. Wie viel ihrer Nachfrage unter die öffentliche Freigabe fällt, ist noch unbekannt; die gesamte Pharma-Nachfrage darf nicht als L4-Hausnachfrage angesetzt werden.

## 2. Wann DH liefern kann

| Monat | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L4-Stunden pro Haus | 46'100 | 41'300 | 40'200 | 22'200 | 10'700 | 3'600 | 3'700 | 3'700 | 9'400 | 25'200 | 38'500 | 45'700 |
| Anteil am Jahr | 15,9 % | 14,2 % | 13,8 % | 7,6 % | 3,7 % | 1,2 % | 1,3 % | 1,3 % | 3,2 % | 8,7 % | 13,3 % | 15,7 % |

**82 % der Rechenzeit fallen von Oktober bis März an.** Das Angebot an Pharma heisst deshalb **Winterkontingent**: Aufträge, die bis zum Frühling fertig sein müssen.

## 3. Welche Aufträge Pharma hat

| Auftrag | Passt? | Grössenordnung |
|---|---|---|
| **Virtuelles Screening (Docking)** | ✓ sehr gut | Uni-Dock: 38,2 Mio. Moleküle in 12 h auf 100 V100-GPUs ≈ 32'000 Moleküle pro GPU-Stunde (Yu et al. 2023). Molekül-Bibliotheken sind riesig (Enamine REAL: 48 Mrd.). Neuere KI-Verfahren docken aber nur einen Bruchteil davon (Deep Docking Ultra: 10,1 Mrd. Moleküle in 10 Tagen, bis 45-mal weniger Rechenaufwand) |
| **Mikroskopbilder** (High-Content-Screening, Cell Painting) | ✓ gut | Labore erzeugen Terabytes pro Jahr; öffentliche Sammlung: 656 TB (Cell Painting Gallery, 2024). Auswertung als nächtlicher Batch |
| **Molekül-Simulationen** (GROMACS) | ~ bedingt | Läuft auf L4, rechnet meist in einfacher Genauigkeit. L4 reagiert stark auf Leistungsdrosselung (NHR@FAU 2025) |
| **Proteinstrukturen** (AlphaFold) | ~ bedingt | 24 GB Speicher der L4 können bei grossen Proteinen knapp werden (eigene Einschätzung) |
| **Klinische Daten, Produktion** | ✗ nein | GxP-Regeln (GCP, GMP) mit Validierungspflicht und Patientendaten. Nicht für Privatkeller |

**Grössenordnung pro Haus:** 290'000 L4-Stunden pro Jahr. Mit dem Uni-Dock-Tempo wären das grob 9 Mrd. gedockte Moleküle, *falls* eine L4 ähnlich schnell ist wie eine V100 (nicht geprüft).

### Wie viele Aufträge pro Jahr? (Aufträge in GPU-Stunden)

Keine Firma veröffentlicht, wie viele GPU-Stunden sie pro Jahr braucht. Die Menge lässt sich aber aus belegten Werten pro Auftrag abschätzen:

| Auftrag | GPU-Stunden pro Auftrag | Quelle | Ein Haus schafft pro Jahr |
|---|---|---|---|
| Docking: 1 Mio. Moleküle | ≈ 31 GPU-h (V100) | Uni-Dock: 38,2 Mio. Moleküle = 1'200 GPU-h | ≈ 9'000 solche Aufträge (= 9 Mrd. Moleküle) |
| Bindungsenergie (FEP), 1 Molekülvergleich | ≈ 3,8 GPU-h | Flare FEP: 28 Vergleiche = 106 GPU-h | ≈ 76'000 Vergleiche |
| FEP-Kampagne einer grossen Firma | 20'000 Rechnungen in 3 Tagen auf 3'500 GPU-Instanzen | AWS-Fallstudie, 16 $ ≈ 13 CHF pro Ergebnis (Spot) | – |

**Zum Vergleich der Grössen:**
- Roche betreibt über 3'500 GPUs. Voll ausgelastet wären das rund 30 Mio. GPU-Stunden pro Jahr, also so viel wie gut 100 DH-Häuser liefern.
- In der Region Basel gibt es 700–800 Life-Sciences-Firmen (Kanton Basel-Stadt, Basel Area). Die meisten haben kein eigenes Rechenzentrum.
- **Beispielrechnung (Annahme):** Eine mittelgrosse Firma, die in der Cloud dauerhaft 100 GPUs zur Hälfte auslastet, braucht rund 440'000 GPU-Stunden pro Jahr. Das sind **1,5 DH-Häuser**. Für 100 Häuser bräuchte DH also rund 65 solche Kunden, oder einige grosse plus viele kleine.

Diese Beispielmenge zeigt nur eine rechnerische Grössenordnung. Sie beweist weder die Eignung der Daten noch ein Kontingent für 5–10 Häuser. Für einen Pilot braucht es einen bezahlten, zulässigen Workflow; für den Ausbau weitere bestätigte Nachfrage.

## 4. Was Pharma heute für eine L4-Stunde zahlt

| Angebot | Preis pro L4-Stunde | Quelle |
|---|---|---|
| AWS g6.xlarge, auf Abruf | ≈ 0,67 CHF (0,80 $) | doit.com (us-east-1) |
| Google Cloud g2-standard-4, auf Abruf | ≈ 0,60 CHF (0,71 $) | cloud.google.com, holori.com |
| Google Cloud, 1 Jahr fest | ≈ 0,55 CHF (−8 %) | holori.com |
| Google Cloud, 3 Jahre fest | ≈ 0,53 CHF (−11 %) | holori.com |
| Spot (unterbrechbar, ohne Garantie) | 0,29–0,38 CHF (0,35–0,45 $) | AWS Spot g6, Joëls Preisliste |

**Wichtig:** Bei GPU-Maschinen sind die Rabatte für feste Verträge klein (8–11 %). Die hohen Rabatte von 66–72 %, die man oft liest, gelten für normale Server, nicht für GPUs.

Historischer Preisvergleich mit Schweizer GPU-Clouds: Ein Schweizer Standort allein begründet weder den Schutz vertraulicher Forschungsdaten noch einen Preisaufschlag für unser gewähltes öffentliches Angebot. Die Vergleichskonfigurationen müssen auch CPU, RAM und weitere Leistungen berücksichtigen:

| Schweizer Anbieter | Preis pro L4-Stunde |
|---|---|
| Hikube (Rechenzentren in der Schweiz) | ≈ 0,68 CHF (0,81 $) |
| Everyware (Sovereign Cloud) | 2,13 CHF |
| Infomaniak | L4 im Angebot, Preis nicht öffentlich gefunden |

**Zielpreis als Annahme: 0,60 CHF**, Sensitivität 0,50 CHF. Für öffentliche bzw. freigegebene anonymisierte Aufgaben müssen Zahlungsbereitschaft und Wettbewerbspreis neu bestätigt werden. Das Angebot verspricht keinen Schutz der laufenden L4-Verarbeitung vor dem Hostadministrator und keine pauschale rechtliche Sonderstellung.

## 5. Welche Verträge im GPU-Markt üblich sind

- Grosse GPU-Anbieter verkaufen fast nur **mehrjährige Verträge mit Abnahmepflicht** («take or pay»): Der Kunde zahlt die reservierte Kapazität, auch wenn er sie nicht nutzt. Laufzeit meist **2–5 Jahre**; bei CoreWeave stammen 96–98 % des Umsatzes daraus (Analyse electroneconomics, OpenAI-Vertrag 5 Jahre).
- Ältere GPUs werden für **1–3 Jahre** neu vermietet.

**Vorschlag für DH:** Vertrag über **3 Jahre**, fester Preis, ein fest gebuchtes **Winterkontingent** (z. B. 80 % der Oktober-bis-März-Stunden). Der Kunde bekommt Planbarkeit, DH ist vor dem Preisverfall geschützt.

## 6. Welche Sicherheitsnachweise Pharma verlangt

| Nachweis | Wofür | Für DH |
|---|---|---|
| **ISO 27001** und/oder **SOC 2 Type II** | Standard-Nachweis für Informationssicherheit bei Lieferanten (ISPE, ISACA) | Pflicht. ISO 27001 kostet 25'000–60'000 € im ersten Jahr (siehe `KOSTEN_DH.md`) |
| Penetrationstests, Schwachstellen-Scans | gehören zur Lieferantenprüfung | jährlich einplanen |
| Vertragsklauseln | Meldefristen bei Datenpannen, Haftung | im Vertrag regeln |
| Regulierter Verwendungszweck | Anforderungen hängen am konkreten Workflow | Keine pauschale Freistellung durch das Wort Forschung; validierungspflichtige Anwendungen sind im aktuellen Angebot nicht zugesagt |
| Physischer Schutz | Server stehen in Privatkellern | abgeschlossener Schrank, Lecksensor, keine Daten dauerhaft auf den Geräten |
| Schutz während der Verarbeitung | L4 bietet im gewählten Betrieb keinen attestierten TEE-Schutz | Nur ausdrücklich zur nicht vertraulichen Verarbeitung freigegebene Inhalte; CC-Recherche ist nicht Teil dieses Angebots |

## 7. Was das für DH bedeutet

Mittlerer Kostenfall, 8 Server, 5 Jahre, nach Steuern. Direktvertrag mit festem Preis, 5 % eigene Plattformkosten statt Marktplatzgebühr. Der Rest der Stunden läuft als Füllauftrag zum Spot-Preis (sinkt 10 % pro Jahr).

| Vertragspreis pro L4-Stunde | 60 % fest gebucht | 80 % fest gebucht |
|---|---|---|
| 0,42 CHF | +8'800 CHF/Jahr | +17'300 CHF/Jahr |
| **0,50 CHF (vorsichtig)** | **+20'300** | +32'500 |
| 0,55 CHF | +27'400 | +42'000 |
| **0,60 CHF (Zielannahme)** | **+34'500** | +51'500 |

**Break-even mit Direktvertrag: 0,36 CHF pro L4-Stunde** bei 60 % fest gebucht, 0,33 CHF bei 80 %. Über einen Marktplatz (20 % Gebühr, Preisverfall auf dem ganzen Preis) bräuchte es rund 0,50 CHF.

Gerechnet mit dem finalen Modell (`src/wirtschaft.py`, `KOSTEN_DH.md`): Referenzhaus, 8 Server, alle Kosten, Steuern, Zins und Restwert, Gratiswärme.

## 8. Antworten auf die offenen Fragen

| Frage | Antwort |
|---|---|
| Welche Aufträge, wie viele Stunden? | Screening (Docking) als grosser Winterauftrag, Mikroskopbilder als nächtlicher Batch. Die Menge hängt am Kunden; ein Haus liefert 290'000 L4-Stunden pro Jahr, davon 82 % im Winterhalbjahr |
| Was zahlt Pharma heute? | US-Clouds: 0,60–0,67 CHF auf Abruf, 0,53–0,55 CHF mit festem Vertrag, 0,29–0,38 CHF Spot. Schweizer Clouds (Datenstandort Schweiz): ab ≈ 0,68 CHF bis 2,13 CHF |
| Fester Preis über mehrere Jahre? | Im GPU-Markt Standard (2–5 Jahre, mit Abnahmepflicht). Für Pharma attraktiv, wenn DH unter dem Preis Schweizer Clouds liegt |
| Welche Sicherheitsnachweise? | Zulässigkeit und Anforderungen je Workflow prüfen; keine pauschale GxP-Freistellung. Schutz vor Einsicht des Hostadministrators ist nicht zugesagt |

## 9. Werte für das Modell

| Variable | Bisher | Neu (Pharma-Sicht) |
|---|---|---|
| Jobtyp A | Nachrichtentexte einbetten, Frist 24 h | **Screening-Kampagne** (Docking), unterbrechbar, Frist bis Ende März |
| Jobtyp B | Bilderkennung, Frist 2 h | **Mikroskopbilder** auswerten, Frist 12 h |
| Rechenpreis | 0,29–0,73 CHF (Marktplatz) | **0,60 CHF Vertragspreis** (vorsichtig 0,50 CHF) |
| Marktplatzgebühr | 15–30 % | **5 %** (eigene Plattform) |
| Preisverfall | −10 % pro Jahr | **0 %** im Vertrag, −10 % nur für Füllaufträge |
| Verkaufsquote | 85 % | **60 %** fest gebucht (42–80 %, Herleitung in `KOSTEN_DH.md` Abschnitt 2b) |
| Vertragsdauer | – | **3 Jahre** |
| Sicherheitskosten | ISO 27001 im Firmenanteil | zusätzlich jährliche Penetrationstests (ohne Quelle) |

Den echten Job auf Joëls Laptop umzustellen (Docking statt Texte), ist optional. Das Modell rechnet in Server-Stunden, die Wärme hängt nicht am Jobtyp. Für die Geschichte im Pitch wäre ein Docking-Job aber stärker.

## Quellen

- Monatswerte: Jahressimulation `dashboard/daten.js` (8 Server, Spot, Referenzhaus 2025)
- FEP: https://www.massbio.org/news/member-news/flare-fep-competitively-combining-speed-and-accuracy-with-ease-of-use/, https://aws.amazon.com/blogs/hpc/running-20k-simulations-in-3-days-with-aws-batch
- Region Basel: https://www.bs.ch/en/schwerpunkte/portrait/heart-europe/basel-figures, https://baselarea.swiss//wp-content/uploads/2023/01/Fakten-uber-die-Life-Sciences-DE_2025-1.pdf
- Roche: https://www.roche.com/media/releases/med-cor-2026-03-16, https://www.rdworldonline.com/roche-claims-pharmas-largest-gpu-footprint-at-nvidias-flagship-gtc-event/
- Lilly: https://blogs.nvidia.com/blog/2026/02/26/lilly-ai-factory-live/
- Uni-Dock: https://cdn.dp.tech/home/paper/yu-et-al-2023-uni-dock-gpu-accelerated-docking-enables-ultralarge-virtual-screening.pdf, https://github.com/dptech-corp/Uni-Dock
- Deep Docking Ultra: https://pubs.rsc.org/en/content/articlepdf/2026/sc/d5sc09599a
- Enamine REAL: https://enamine.net/public/press-release/Enamine-Pharmacelera-PR-May-7th-2024.pdf
- Cell Painting Gallery: https://web3.arxiv.org/pdf/2405.02767
- GROMACS auf L4: https://arxiv.org/html/2510.06902v1
- L4-Preise Cloud: https://www.doit.com/compute/spot/us-east-1/g6.xlarge, https://calculator.holori.com/gcp/vm/g2-standard-4, https://cloud.google.com/products/compute/pricing/accelerator-optimized
- Verträge: https://electroneconomics.substack.com/p/coreweaves-contract-machine-how-a, https://thenextweb.com/news/coreweave-has-agreed-a-multi-year-gpu-cloud-deal-with-anthropic-to-power-claude-at-production-scale-its-second-major-ai-infrastructure-announcement-in-48-hours
- Sicherheit: https://www.ispeboston.org/download/educational_presentations/2024/Vendor-Qualification-and-Quality-Agreements-for-Cloud-XaaS-suppliers-June06.pdf, https://www.isaca.org/resources/news-and-trends/industry-news/2024/cloud-security-challenges-in-the-pharmaceutical-industry, https://www.freyrsolutions.com/blog/cyber-risk-considerations-in-pharma-vendor-assessments
- GxP und Cloud: https://azure.microsoft.com/en-us/blog/new-azure-gxp-guidelines-help-pharmaceutical-and-biotech-customers-build-gxp-solutions/
- Confidential Computing Pharma: https://blogs.nvidia.com/blog/mitsui-xeureka-drug-discovery/
