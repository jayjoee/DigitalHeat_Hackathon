# Vollständiger Bericht zur Serverheizung von DigitalHeat

Kundenperspektive Nordwestschweiz und technische Ergebnisse des Hackathons  
Stand der Ausgangsunterlagen 20 und 21 November 2026

Die Unterlagen beschreiben eine Serverheizung, deren Abwärme für Heizung und Warmwasser genutzt wird. Im vorgeschlagenen Pilot stellt DigitalHeat die Anlage neben eine bestehende Ölheizung und übernimmt nach der Arbeitsannahme Anlage, Einbau, Serverstrom und Unterhalt. Der Haushalt erhält kostenlose oder vergünstigte Wärme; die bestehende Heizung bleibt als Backup.

Das untersuchte Referenzhaus hat einen jährlichen Wärmebedarf von 31'231 kWh. Die Unterlagen weisen für acht Server im Szenario mit ausreichend flexiblen Rechenaufträgen rund 93 Prozent Wärmedeckung aus. Für ein angenommenes Durchschnitts-Einfamilienhaus mit 17'000 kWh und einer kleineren Einheit werden 99,6 Prozent genannt. Die hohe Deckung hängt entscheidend von der Verfügbarkeit flexibler Aufträge ab. Kostenübernahme, Wärmepreis, Vertrag und Sicherheitsanforderungen sind mit den Säulen Firma und Pharma abzustimmen; die kantonale Anerkennung und die Zulässigkeit des vorgesehenen Backups sind offene Punkte der Unterlagen.

## Umfang und Lesefolge

Alle acht ausgewählten Dateien sind nachfolgend vollständig enthalten. Tabellen, Quellenlinks, Formeln, Befehle, Annahmen, offene Fragen und Wiederholungen bleiben erhalten. Lediglich die Markdown-Überschriften werden um eine Ebene eingerückt. Die frühere Zusammenführung in KUNDENVIEW ersetzt deshalb hier keine der ursprünglichen Dateien. Die Befehle sind Dokumentationsinhalt und wurden für diesen Bericht nicht ausgeführt.

1. KUNDENVIEW als zusammenhängende Darstellung der Kundenperspektive
2. ERGEBNISSE mit Simulation, Wirtschaftlichkeit und Reproduzierbarkeit
3. RESULTATE EINFACH mit der verständlichen Ergebnisdarstellung
4. KUNDENPERSPEKTIVE als vollständiger früherer Arbeitsstand
5. KUNDE NORDWESTSCHWEIZ mit regionalen Details
6. ANNAHMEN KUNDE mit Annahmen und Quellen
7. NOTIZEN mit zusätzlichen Ideen und Recherchefragen
8. requirements mit sämtlichen aufgeführten Softwareabhängigkeiten
9. Prüfung der zusätzlich referenzierten Dateien

## Einordnung abweichender Aussagen

Die Unterlagen nennen die Deckung des Referenzhauses teils mit 92,9 Prozent, teils mit 93,0 Prozent. Diese Angaben werden in ihren jeweiligen Arbeitsständen beibehalten. Die Herkunft der Differenz wurde nicht neu berechnet. Auch die Angabe von 29'027 kWh Serverwärme und 2'203 kWh Backup ergibt gerundet 31'230 kWh statt der ausgewiesenen 31'231 kWh Gesamtbedarf.

Der Wert von 0,226 CHF je Serverstunde ist in ERGEBNISSE als Stromkosten abzüglich des rechnerischen Wärmewerts je Serverstunde definiert. Er enthält keine vollständigen Anlagen-, Installations-, Unterhalts- oder Finanzierungskosten. Bei kostenloser Wärme für den Haushalt ist der rechnerische Wärmewert zudem kein Wärmekassenerlös von DigitalHeat. Die im Bericht wiedergegebenen Schwellen ersetzen daher keine vollständige Firmenrechnung.

Die mit 0,0 Tonnen angegebenen verbleibenden CO2-Werte sind gerundete Werte aus dem Vergleich der bisherigen Brennstoffnutzung. Sie belegen keine emissionsfreie Gesamtanlage einschliesslich Serverstrom und Hardware. Die Aussagen zur Förderung, zu Energiepreisen und zum Recht behalten den in den Ausgangsdateien angegebenen Stand und Prüfstatus; eine neue externe Prüfung ist nicht Bestandteil dieses Berichts.

Die genannten Partner, Haftungszusagen und Bedingungen für den Pilot sind Bestandteile des vorgeschlagenen Angebots. Sie sind hier nicht als bereits abgeschlossene Verträge oder bestätigte Partnerschaften ausgewiesen.

<!-- Beginn Quelldatei KUNDENVIEW.md -->

## Kundenview: Serverheizung für Hauseigentümer in der Nordwestschweiz

Stand 21.11.2026 · Säule «Kunde» des DigitalHeat-Case (Hackathon) · Die Säulen «Firma» und «Pharma» werden separat erarbeitet.

---

### 0. Kurzfassung

**Das Angebot:** DigitalHeat stellt eine Serverheizung kostenlos neben die bestehende Öl- oder Gasheizung. DigitalHeat zahlt Anlage, Einbau, Server-Strom und Unterhalt. Der Haushalt bekommt 93–100 % seiner Wärme von den Servern und braucht kaum noch Heizöl oder Gas.

**Was der Haushalt gewinnt (Gratiswärme, Durchschnitts-Einfamilienhaus mit 17'000 kWh Wärme pro Jahr):**

| Heute heizt der Haushalt mit | Ersparnis pro Jahr | CO2 pro Jahr |
|---|---|---|
| **Öl** | **3'317 CHF** (Referenzhaus: 5'686 CHF) | 5,3 t → 0,0 t |
| **Gas** | **2'636 CHF** (Referenzhaus: 4'520 CHF) | 3,7 t → 0,0 t |
| Wärmepumpe | 2'252 CHF (Referenzhaus: 3'861 CHF) | – |

Eigene Investition: **0 CHF**. Keine Sanierung nötig, weil die Serverheizung 50–70 °C liefert und zu alten Radiatoren passt.

**Strategie:** Einstieg mit **Ölheizungen in Basel-Stadt** (Pilot mit 5–10 Häusern), danach Öl in **Basel-Landschaft und Aargau** (rund 19'300 Öl-Wohngebäude allein in BL), dann **Gas** (Basler Gasnetz wird bis 2037 stillgelegt), zuletzt alle Haushalte.

**Bedingungen, damit es für den Kunden aufgeht:**
1. Die Wärme kostet den Haushalt höchstens rund **7 Rp./kWh** (Gratiswärme ist am stärksten). Gegenüber Öl lohnt sich der Wechsel bis 19,6 Rp., gegenüber Gas bis 15,6 Rp., gegenüber einer Wärmepumpe bis 13,3 Rp.
2. Es gibt das ganze Jahr **genug flexible Rechenaufträge**. Sonst sinkt die Deckung auf 52–63 % und die Ersparnis fast auf die Hälfte.
3. Die Kantone akzeptieren die Lösung (erneuerbarer Heizungsersatz, Heizstab als Notheizung). Das ist noch offen.

---

### 1. Ausgangslage und Auftrag

Der Case wird in drei Säulen bearbeitet:

| Säule | Frage | Wer |
|---|---|---|
| **Kunde** (dieses Dokument) | Warum stellt sich ein Hauseigentümer eine Serverheizung in den Keller, und was gewinnt er? | Joël |
| Firma | Wie verdient DigitalHeat Geld, und ist das Modell nachhaltig profitabel? | Kollegen |
| Pharma | Warum kaufen Pharmakonzerne diese Rechenleistung (Sicherheit, Preis)? | Kollegen |

Ziel ist eine Win-Win-Win-Situation. Dieses Dokument behandelt nur den Kunden. Wo das Kundenangebot von den anderen Säulen abhängt, steht das in Abschnitt 11 als Schnittstelle.

**Vorgehen:**
1. Zielkunde festlegen
2. Heutige Heizkosten kennen
3. Angebot und Bezahlmodell festlegen
4. Ersparnis rechnen, auch für schlechtere Fälle
5. Markt und Regeln in der Region prüfen
6. Einwände beantworten
7. Kunden-Dashboard ableiten
8. Schnittstellen mit den Kollegen klären

---

### 2. Zielkunde und Einstiegsstrategie

**Zielkunde im Pilot:** Eigentümer eines Einfamilienhauses mit **Ölheizung**, der aus dem Öl aussteigen will, ohne gleich eine teure Wärmepumpe samt Sanierung zu finanzieren.

**Warum Öl zuerst:**
- Höchste Heizkosten: 19,6 Rp. pro kWh Wärme (Gas 15,6, Wärmepumpe 13,3)
- Politischer Druck: Basel-Stadt will bis 2037 fossilfrei heizen, neue Öl- und Gasheizungen sind seit 2017 verboten
- Oft alte Häuser mit Radiatoren, in denen eine Wärmepumpe schlecht arbeitet
- Der Öltank im Keller macht die Wirkung sichtbar: Er leert sich kaum noch.

Öl ist der Einstieg, nicht das Ziel. Diese Kunden wechseln am schnellsten und werden zu Referenzen. Danach folgen die anderen:

| Phase | Wo und wer | Argument |
|---|---|---|
| **1 Pilot** | Ölheizungen in Basel-Stadt ausserhalb der Fernwärme (Bruderholz, Riehen, Bettingen), 5–10 Einfamilienhäuser | −93 bis −100 % Heizöl, 0 CHF Investition, Referenzen schaffen |
| **2 Öl ausrollen** | Basel-Landschaft (≈ 19'300 Öl-Wohngebäude), dann Aargau (135'574 Öl-Wohnungen) | gleiche Ersparnis, über zehnmal grösserer Markt |
| **3 Gas** | Basel-Stadt (Netz geht bis 2037 zu), dann Basel-Landschaft (≈ 20'500 Gas-Wohngebäude) | Ausstieg aus Gas ohne eigene Investition, Termindruck in BS |
| **4 Alle Haushalte** | Häuser mit Wärmepumpe, Neubauten, Mehrfamilienhäuser | Gratiswärme statt Strom für die Wärmepumpe |

---

### 3. Das Angebot

#### 3.1 Wer zahlt was?
**DigitalHeat zahlt und besitzt alles:** Server, Einbau, Server-Strom (eigener Zähler) und Unterhalt. So beschreibt es auch DigitalHeat selbst («kein Hardwarekauf durch den Wärmeabnehmer»), und so arbeiten Heata und Deep Green in Grossbritannien.

Warum der Haushalt die Anlage nicht selbst kauft: Eine 8-kW-Einheit kostet rund 290'000 CHF (Hardware ≈ 258'000, Kühlung, Einbau, Speicher und Netzwerk ≈ 32'000; belegter Komplettpreis eines L4-Servers, siehe KOSTEN_DH.md). Eine Wärmepumpe kostet in Basel 31'500–63'000 CHF. Die Serverheizung ist vor allem ein Rechenzentrum, das sich über verkaufte Rechenzeit bezahlt, nicht über die Wärme. Wie sich das für DigitalHeat rechnet, klärt die Säule Firma.

| Modell | Haushalt zahlt | Bewertung aus Kundensicht |
|---|---|---|
| **A Gratiswärme** (empfohlen für den Pilot) | nichts, stellt Platz und Anschluss | stärkstes Verkaufsargument |
| **B Wärmeabo** | Preis pro kWh, legt die Säule Firma fest | lohnt sich bis zur Schwelle in Abschnitt 4.3 |
| C Kunde kauft die Anlage | ≈ 290'000 CHF | nicht sinnvoll: zu teuer, zu riskant |

**Wohin der Ertrag der Rechenleistung fliesst:** Der Pharmakunde zahlt DigitalHeat für die Rechenzeit. DigitalHeat zahlt davon Strom, Hardware, Einbau und Unterhalt. Der Haushalt bekommt keinen Anteil am Rechenerlös, sondern die Wärme gratis und trägt kein Risiko. Ob er zusätzlich einen Bonus oder eine Platzmiete erhält, entscheidet die Säule Firma (Abschnitt 11).

#### 3.2 Die bestehende Heizung bleibt als Backup
Die Serverheizung kommt **neben** die bestehende Heizung. Für die kältesten Stunden und bei Ausfällen springt das Backup ein.

| Heute | Backup | Bemerkung |
|---|---|---|
| Öl | bestehender Ölkessel | kostet nichts, Tank bleibt; in BS spätestens 2037 durch erneuerbares Backup ersetzen |
| Gas (ausserhalb BS) | bestehender Gaskessel | Grundgebühr ≈ 195 CHF/Jahr bleibt |
| Gas (Basel-Stadt) | **Heizstab im Speicher** (≈ 2'000 CHF, Annahme) | nötig, weil das Gasnetz bis 2037 abgestellt wird; Erlaubnis als Notheizung offen |

#### 3.3 Pilot-Aufbau (Vorschlag)
| | |
|---|---|
| Teilnehmende | 5–10 Einfamilienhäuser mit Ölheizung in Basel-Stadt, ausserhalb des Fernwärmegebiets |
| Voraussetzungen | Platz im Keller oder Heizraum (der Raum des Öltanks wird oft frei), Wasser-Heizsystem, Starkstromanschluss, Glasfaser |
| Dauer | 1 Jahr, damit Winter und Sommer drin sind |
| Kosten für den Haushalt | keine, auch nicht für den Rückbau |
| Was gemessen wird | Heizöl in Litern vorher und nachher, Wärme vom Server, Raumtemperatur und Komfort, Lärm, Ausfälle, Zufriedenheit |
| Nach dem Pilot | Gratiswärme weiter, Wärmeabo oder Rückbau ohne Kosten |

---

### 4. Was der Haushalt spart

Zwei Häuser:
- **Referenzhaus** des Case: 31'231 kWh Wärme pro Jahr, 8-kW-Einheit
- **Durchschnitts-EFH:** 17'000 kWh Wärme pro Jahr, 5-kW-Einheit (die kleinste DigitalHeat-Einheit)

Die Deckung kommt aus der Jahressimulation mit dem Wetter Basel 2025: **92,9 % bzw. 99,6 %**, wenn genug flexible Rechenaufträge da sind.

#### 4.1 Was kostet heute 1 kWh Wärme?
| Heizung | Rp. pro kWh Wärme | Grundlage |
|---|---|---|
| Öl | **19,6** | 1,665 CHF/l, 10 kWh/l, Kessel 85 % |
| Gas | **15,6** + ≈ 195 CHF/Jahr Grundgebühr | IWB 2026, Stufe M, inkl. MwSt., Kessel 90 % |
| Wärmepumpe | **13,3** (BS) / 12,1 (BL, AG) | Strompreis ÷ Jahresarbeitszahl 2,5 |
| **Serverheizung, Gratiswärme** | **0** | DigitalHeat zahlt Strom und Anlage |

#### 4.2 Ersparnis pro Jahr (Gratiswärme, Basel-Stadt)
| | Referenzhaus | Durchschnitts-EFH |
|---|---|---|
| **Öl:** heute → nachher | 6'118 → 432 CHF, **spart 5'686** | 3'330 → 13 CHF, **spart 3'317** |
| Heizöl in Litern | 3'674 → 259 l (−93 %) | 2'000 → 8 l (−100 %) |
| **Gas mit Gas-Backup:** heute → nachher | 5'057 → 538 CHF, **spart 4'520** | 2'841 → 205 CHF, **spart 2'636** |
| **Gas mit Heizstab-Backup** (kein Gasanschluss mehr) | **spart 4'325** | **spart 2'819** |
| **Wärmepumpe:** heute → nachher | 4'154 → 293 CHF, **spart 3'861** | 2'261 → 9 CHF, **spart 2'252** |
| CO2 Öl | 9,7 → 0,7 t | 5,3 → 0,0 t |
| CO2 Gas | 6,9 → 0,5 t | 3,7 → 0,0 t |

Muss ein Öl-Haushalt ohnehin ersetzen und entfällt dank der Serverheizung die neue Wärmepumpe (45'000 CHF − 10'500 CHF Förderung, über 18 Jahre), kommen **rund 1'900 CHF pro Jahr** dazu. Das gilt nur, wenn der Kanton die Serverheizung als Heizungsersatz akzeptiert (offen).

#### 4.3 Ersparnis je nach Wärmepreis (Modell B)
Ersparnis pro Jahr, Referenzhaus / Durchschnitts-EFH:

| Wärmepreis | vs. Öl | vs. Gas | vs. Wärmepumpe |
|---|---|---|---|
| 0 Rp./kWh (gratis) | 5'686 / 3'317 | 4'520 / 2'636 | 3'861 / 2'252 |
| 3 Rp./kWh | 4'815 / 2'809 | 3'649 / 2'128 | 2'990 / 1'744 |
| 5 Rp./kWh | 4'235 / 2'470 | 3'069 / 1'789 | 2'410 / 1'405 |
| 8 Rp./kWh | 3'364 / 1'962 | 2'198 / 1'281 | 1'539 / 897 |
| 10 Rp./kWh | 2'783 / 1'624 | 1'617 / 943 | 958 / 559 |
| 13,3 Rp./kWh | 1'825 / 1'065 | 659 / 384 | 0 / 0 |

**Schwellen:** Öl 19,6 Rp., Gas 15,6 Rp., Wärmepumpe 13,3 Rp. pro kWh Wärme. Damit der Wechsel für einen Öl-Haushalt deutlich attraktiv bleibt (über 2'000 CHF im Durchschnitts-EFH), sollte die Wärme **höchstens rund 7 Rp./kWh** kosten.

#### 4.4 Schlechterer Fall: zu wenig flexible Aufträge
Kommen nur Aufträge mit Frist (Nachfrage wie im Alibaba-Rechenzentrum), deckt die Serverheizung nur 52 % (Referenzhaus) bzw. 63 % (Durchschnitt).

| Gratiswärme | Referenzhaus | Durchschnitts-EFH |
|---|---|---|
| spart vs. Öl | 3'164 CHF | 2'104 CHF |
| spart vs. Gas (Gas-Backup) | 2'515 CHF | 1'673 CHF |
| spart vs. Gas (Heizstab) | 44 CHF | 761 CHF |
| spart vs. Wärmepumpe | 2'148 CHF | 1'429 CHF |

Der Heizstab-Backup lohnt sich also nur, wenn genug Aufträge da sind. Diese Frage geht an die Säule Pharma.

---

### 5. Warum es technisch passt

- **Temperatur:** DigitalHeat nennt 50–70 °C Vorlauf. Das reicht für alte Radiatoren und Warmwasser ohne Wärmepumpe. Eine Wärmepumpe braucht in solchen Häusern oft zuerst Dämmung und neue Heizkörper.
- **Sicher getrennt:** Direkte Flüssigkeitskühlung an den Prozessoren, eigener Kühlkreis, Wärmetauscher zum Heizwasser. Das Heizwasser kommt nie an die Server.
- **Speicher:** Ein Wassertank (im Modell 35 kWh) gleicht aus, wann die Server rechnen und wann das Haus Wärme braucht.
- **Grösse:** DigitalHeat baut Einheiten mit 5–20 kW. Unsere 8 kW (Referenzhaus) und 5 kW (Durchschnitt) liegen darin.
- **Jahresverlauf:** Im Winter laufen die Server fast pausenlos. Im Sommer liefern sie nur Warmwasser, und der Haushalt merkt keinen Unterschied.

---

### 6. Markt Nordwestschweiz

Nordwestschweiz = Grossregion des BFS: Basel-Stadt, Basel-Landschaft, Aargau.

| Kanton | Öl | Gas | Bezug |
|---|---|---|---|
| **Basel-Stadt** | 1'677 Ölfeuerungen (Juni 2026), 8 % der Wohngebäude | knapp 11'000 Gas-Liegenschaften (2024) | Anlagen bzw. Liegenschaften |
| **Basel-Landschaft** | ≈ 19'300 Wohngebäude (28,9 % von 66'780) | ≈ 20'500 Wohngebäude (30,7 %) | Wohngebäude 2024 |
| **Aargau** | 135'574 Wohnungen (39 %) | 58'620 Wohnungen (17 %) | Wohnungen 2024, nicht Gebäude |

**Ersparnis Durchschnitts-EFH pro Kanton (Gratiswärme):**

| | Basel-Stadt | Basel-Landschaft | Aargau |
|---|---|---|---|
| Strompreis 2026 | 33,25 Rp. (IWB) | 30,20 Rp. (EBL) | 30,15 Rp. (AEW) |
| spart vs. Öl | 3'317 CHF | 3'317 CHF | 3'317 CHF |
| spart vs. Gas | 2'636 CHF | ≈ 2'636 CHF | ≈ 2'636 CHF (Gaspreis angenommen) |
| spart vs. Wärmepumpe | 2'252 CHF | 2'045 CHF | 2'042 CHF |

**Basel-Stadt im Detail:**
- **Ölheizungen** nehmen schnell ab: 2'631 (2018) → 1'847 (2024) → 1'677 (Juni 2026).
- **Gasnetz:** Der Grosse Rat hat 2023 die Stilllegung bis 2037 beschlossen. Ab 2028 nimmt IWB rund 1'000 Anschlüsse pro Jahr vom Netz. Gas-Haushalte müssen also wechseln.
- **Fernwärme:** Wo Fernwärme kommt, ist sie die naheliegende Lösung, und die kantonale Förderung für dezentrale Heizungen ist dort halbiert. Die Serverheizung zielt deshalb auf die **Gebiete ohne Fernwärme**: laut Energierichtplan rund **5,3 km²**, vor allem **Bruderholz, Riehen, Bettingen** und Teile am Westrand von Basel. Karte: `dashboard/karte_fernwaerme.html`.

**Grössenordnung:** Wechseln 1 % der Öl-Wohngebäude in Basel-Landschaft (≈ 190 Häuser), sparen diese Haushalte zusammen rund **0,6 Mio. CHF und 1'000 t CO2 pro Jahr**.

---

### 7. Förderung und Regeln

| | Basel-Stadt | Basel-Landschaft | Aargau |
|---|---|---|---|
| Förderung Wärmepumpe (zum Vergleich) | 8'000 + 250 CHF/kWth, max. 40 %, halbiert im Fernwärmegebiet | Energiepaket BL, Beträge für Ölersatz 2026 nicht gefunden | Programm ab 1.5.2026; ältere Broschüre 6'000 + 180 CHF/kWth; keine Förderung im Verbundgebiet |
| Bund | Impulsprogramm (2025–2034, 200 Mio. CHF/Jahr): Ersatz von Elektroheizungen, Einbau einer Wärmeverteilung | gleich | gleich |
| Druck zum Wechsel | sehr hoch (Gasnetz zu bis 2037, fossile Neuanlagen verboten) | nicht im Detail geprüft | nicht im Detail geprüft |

- Für die Serverheizung gibt es **in keinem Kanton eine eigene Förderkategorie**.
- Ob sie als **erneuerbarer Heizungsersatz** zählt und ob ein **Heizstab als Notheizung** erlaubt ist, muss jeder Kanton beantworten. In Basel-Stadt ist das Amt für Umwelt und Energie, Abteilung Energie, zuständig.
- Im Pilot wird der Ölkessel nicht ersetzt, sondern ergänzt. Die Ersatzpflicht greift deshalb vermutlich noch nicht (Annahme).

---

### 8. Partner aus Kundensicht

| Partner | Was der Kunde davon hat |
|---|---|
| **IWB** bzw. **EBL / AEW** | bekannter regionaler Absender, Strom und Glasfaser aus einer Hand, Vertrauen |
| **Lokaler Heizungsinstallateur** | Einbau, Service und Backup aus der Region |
| **Smart-Home-Anbieter** (Loxone, Home Assistant, Homey, Matter) | Steuerung in der App, die er schon hat |
| **Versicherung** (z. B. Baloise) | Schäden an der Anlage sind nicht sein Risiko |
| **Bank** (grüne Hypothek, z. B. BKB) | günstigere Hypothek für ein Haus mit erneuerbarer Wärme |

---

### 9. Einwände und Antworten

| Einwand | Antwort |
|---|---|
| «Was, wenn der Server ausfällt?» | Das Backup springt automatisch ein, der Speicher überbrückt Stunden. |
| «Ist das laut?» | Flüssigkeitskühlung ohne grosse Lüfter, im Keller hinter einer Tür (Annahme, im Pilot messen). |
| «Wer haftet bei Schäden?» | DigitalHeat, über eine Versicherung. |
| «Kommt jemand an meine Daten oder ich an fremde?» | Getrennte Netze, verplombtes Gehäuse, der Haushalt hat keinen Zugang. |
| «Was, wenn ich umziehe?» | Der Vertrag geht auf den neuen Eigentümer über, oder die Anlage wird kostenlos zurückgebaut. |
| «Brauche ich trotzdem eine neue Wärmepumpe?» | Offen, hängt vom Kanton ab. Im Pilot bleibt die bestehende Heizung. |
| «Was, wenn DigitalHeat Konkurs geht?» | Die bisherige Heizung bleibt immer funktionsfähig. |

---

### 10. Kunden-Dashboard

**In der Smart-Home-App (nur das Wichtigste):**
- **Ersparnis in CHF** diesen Monat und seit Start
- Wärme vom Server heute und diesen Monat (kWh, Anteil am Bedarf)
- Heizöl bzw. Gas gespart (Liter bzw. kWh) und CO2 gespart
- Speicher-Füllstand in %
- Status: läuft / pausiert / Störung
- Knöpfe «Komfort» (wärmer) und «Abwesend» (Ferien)

**Im eigenen Dashboard (Details):**
- Verlauf Wärme, Backup und abgeführte Wärme pro Tag und Monat
- Vergleich mit der alten Heizung (CHF, CO2), auch für die ganze Vertragsdauer
- Rechenleistung: Stunden und Bereich (z. B. «Medikamentenforschung»), ohne Kundennamen
- Prognose der nächsten Tage (Wetter, erwartete Wärme)
- Wartung, Vertrag, Förderung, Kontakte

---

### 11. Schnittstellen zu den anderen Säulen

| Was die Kundenperspektive braucht | Von wem | Warum | Arbeitsannahme |
|---|---|---|---|
| Wer zahlt Hardware, Einbau und Server-Strom? | Firma | Gratiswärme nur möglich, wenn DigitalHeat zahlt | DigitalHeat zahlt alles |
| Gratiswärme oder Wärmeabo, zu welchem Preis? | Firma | bestimmt die Ersparnis (Abschnitt 4.3) | Gratiswärme im Pilot, sonst ≤ 7 Rp./kWh |
| Gibt es das ganze Jahr genug flexible Aufträge? | Pharma | Deckung 93–100 % statt 52–63 % | ja |
| Einheitengrösse pro Haus | Firma | Platz, Lärm, Anschluss | 8 kW / 5 kW |
| Sicherheitsauflagen im Haus | Pharma | was der Haushalt dulden muss | kein Zugang, verplombt |
| Vertrag, Kündigung, Konkurs | Firma | Vertrauen | Backup bleibt immer |
| Bekommt der Haushalt einen Anteil am Rechenerlös (Bonus, Platzmiete)? | Firma | Der Rechenerlös fliesst heute ganz an DigitalHeat; ein Anteil macht das Angebot stärker, besonders für Wärmepumpen-Haushalte | kein Anteil, nur Gratiswärme |

---

### 12. Risiken und offene Punkte
- **Zu wenig flexible Aufträge:** grösstes Risiko für die Ersparnis (Abschnitt 4.4)
- **Regeln der Kantone:** Serverheizung als Heizungsersatz? Heizstab als Notheizung?
- **Gas in Basel-Stadt:** Backup muss ersetzt werden, Fernwärme ist starke Konkurrenz
- **Lärm und Platz** von 5–8 kW Servern im Keller (im Pilot messen)
- **Preise:** Gaspreise in BL und AG ausserhalb des IWB-Gebiets, Förderbeträge BL 2026, MwSt. beim EBL-Strompreis
- **Wetter:** Gerechnet mit Basel 2025, im Aargau etwas kühler

---

### 13. Methode und Reproduzierbarkeit

| Was | Wo |
|---|---|
| Jahressimulation (Deckung, Backup, Speicher) | `src/scheduler/jahr.py`, `src/scheduler/kern.py` |
| Kundenrechnung (Öl, Gas, Wärmepumpe, Heizstab, Wärmepreise) | `src/kunde/wirtschaftlichkeit.py` → `daten/ergebnisse/win_win_win.json` |
| Karte Gebiete ohne Fernwärme | `src/kunde/karte_fernwaerme.py` → `dashboard/karte_fernwaerme.html` |
| Wetter | offizielles Case-CSV, identisch mit Open-Meteo Basel 2025 |
| Rohdaten | `daten/roh/` (ElCom, Geoportal BS, EBL) |

Neu rechnen:
```
python3 src/kunde/wirtschaftlichkeit.py
python3 src/kunde/karte_fernwaerme.py
```

---

### 14. Alle Annahmen mit Quellen

Status:
- **Case** = Vorgabe von DigitalHeat im Hackathon
- **Belegt** = aus einer öffentlichen Quelle übernommen
- **Abgeleitet** = aus belegten Werten gerechnet
- **Annahme** = selbst gesetzt, ohne Quelle. Vor einer Entscheidung prüfen.

Rechnung: `src/kunde/wirtschaftlichkeit.py` (alle Werte stehen dort in `P` mit Quelle), Physik aus `src/scheduler/jahr.py`.

#### 14.1 Haus und Wärmebedarf
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Wetter Basel 2025, stündlich | Open-Meteo, 47.56 N 7.55 E | Case, Belegt | offizielles Case-CSV, identisch mit [Open-Meteo Archiv](https://open-meteo.com/en/docs/historical-weather-api) |
| Heizbedarf Referenzhaus | max(0, 10 kW × (20 − T) ÷ 25,6) an Heiztagen = 26'851 kWh | Case | Case-Formel |
| Warmwasser | 12 kWh/Tag = 4'380 kWh/Jahr, gleichmässig über den Tag | Case | Case; Verteilung über den Tag = Annahme |
| Durchschnitts-EFH | 17'000 kWh/Jahr Wärme | Annahme | abgeleitet aus [Raiffeisen](https://www.raiffeisen.ch/rch/de/wissen/wohnen/energiesparen-erneuerbare-heizung.html): EFH mit 2'000 l Heizöl/Jahr × 10 kWh/l × 85 % |
| Speicher | 35 kWh, verlustfrei | Case | Case |

#### 14.2 Serverheizung
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Wärme pro Server | 1 kW Strom → 0,8 kW nutzbare Wärme | Case | Case |
| Einheitengrösse | 8 kW Referenzhaus, 5 kW Durchschnitts-EFH | Abgeleitet | Jahressimulation; DigitalHeat nennt 5–20 kW pro Einheit ([digitalheat.ch](https://digitalheat.ch)) |
| Vorlauftemperatur | 50–70 °C, passt zu alten Radiatoren | Belegt | [digitalheat.ch](https://digitalheat.ch) |
| Kühlung | direkte Flüssigkeitskühlung, Wärmetauscher trennt Kühlkreis und Heizwasser | Belegt | [digitalheat.ch](https://digitalheat.ch) |
| Deckungsgrad | 93 % (Referenz) / 99,6 % (Durchschnitt) | Abgeleitet | Jahressimulation, **setzt genug flexible Rechenaufträge voraus** (Säule Pharma) |
| Deckung ohne genug Aufträge | 52 % / 63 % | Abgeleitet | Jahressimulation mit Nachfrage aus dem Alibaba-Trace |
| Server-Strom zahlt nicht der Haushalt | eigener Zähler | Annahme | so bei [Heata](https://www.techradar.com/news/this-company-will-pay-for-your-heating-if-you-let-it-install-a-server-in-your-house) und [Deep Green](https://techradar.com/news/this-startup-is-recycling-energy-to-heat-swimming-pools-for-free); von Säule Firma zu bestätigen |
| Haushalt kauft keine Hardware | 0 CHF | Belegt (Absicht) | [digitalheat.ch](https://digitalheat.ch): «kein Hardwarekauf durch den Wärmeabnehmer» |
| Wärmepreis für den Haushalt | 0–13,3 Rp./kWh (Varianten) | offen | legt Säule Firma fest; Kundenperspektive empfiehlt ≤ 7 Rp./kWh |

#### 14.3 Energiepreise
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Strom | 33,25 Rp./kWh (Total, IWB, H4, 2026) | Belegt | [ElCom](https://www.strompreis.elcom.admin.ch) (API-Abruf, `daten/roh/elcom/`) |
| Heizöl | 1,665 CHF/l (3'000 l, Anfang Nov. 2026) | Belegt | [weekend.at](https://www.weekend.at/chronik/heizoelpreise-fallen-gruende-marktuebersicht-und-kaufempfehlung); Preis schwankt stark |
| Heizwert Heizöl | 10 kWh/l | Annahme | Standardwert Heizöl EL |
| Gas Arbeitspreis | 11,57 Rp./kWh (Stufe M, inkl. MwSt.) | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| CO2-Abgabe Gas | 2,333 Rp./kWh (inkl. MwSt.) | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| Konzessionsabgabe Gas BS | 0,11 Rp./kWh | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| Gas Leistungspreis | 12,43 CHF/kW/Jahr, min. 194,58 CHF | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| Tarifstufe M für das Referenzhaus | ≈ 35'000 kWh Gas | Abgeleitet | IWB-Beispiel EFH 20'000 kWh = Stufe M; Grenze der Stufen nicht publiziert |
| Gas-Anschlussleistung | 15 kW Referenz / 12 kW Durchschnitt | Annahme / Belegt | 12 kW aus IWB-Beispiel Typ II; 15 kW Annahme |

#### 14.4 Heute verwendete Heizung
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Wärmepumpe Jahresarbeitszahl | 2,5 | Case | Case («Wärme ersetzt Wärmepumpe, JAZ 2,5») |
| Ölkessel Wirkungsgrad | 85 % | Annahme | älterer Kessel |
| Gaskessel Wirkungsgrad | 90 % | Annahme | |
| CO2 Heizöl | 2,65 kg/l | Annahme | gängiger Emissionsfaktor Heizöl EL |
| CO2 Erdgas | 0,198 kg/kWh | Annahme | gängiger Emissionsfaktor Erdgas |
| Wärme kostet heute | Öl 19,6 / Gas 15,6 / WP 13,3 Rp. pro kWh Wärme | Abgeleitet | aus den Zeilen oben |

#### 14.5 Investitionen und Förderung beim Haushalt
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Neue Wärmepumpe in Basel | 31'500–63'000 CHF, gerechnet 45'000 | Belegt (Spanne) | [handwerker-kosten.ch](https://www.handwerker-kosten.ch/waermepumpe/basel/) |
| Förderung Wärmepumpe BS 2026 | 8'000 + 250 CHF/kWth (Luft/Wasser, ausserhalb Fernwärme), max. 40 %; Beispiel 8 kW = 10'500 | Belegt (nicht amtlich) | [ion-e.ch](https://www.ion-e.ch/de/waermepumpe-basel), [Stiebel Eltron](https://www.stiebel-eltron.ch/de/home/ratgeber/uebersicht/foerderung/basel-stadt.html); amtliche Broschüre 2026 war nicht abrufbar |
| Förderung halbiert im Fernwärmegebiet | ja | Belegt | [bs.ch](https://www.bs.ch/medienmitteilungen/2025-teilrevision-energieverordnung-mehr-foerderbeitraege-fuer-gesamtsanierungen-und-anpassung-beim-heizungsersatz) |
| Lebensdauer Wärmepumpe | 18 Jahre | Annahme | übliche 15–20 Jahre |
| Heizstab im Speicher (Backup ohne Gas) | 2'000 CHF einmalig | Annahme | grobe Schätzung, keine Offerte |
| Heizstab erlaubt? | als Notheizung | **offen** | Elektro-Widerstandsheizungen sind in der Schweiz eingeschränkt; beim AUE BS klären |
| Serverheizung gilt als erneuerbarer Heizungsersatz? | — | **offen** | beim AUE BS klären |
| Impulsprogramm Bund | 2025–2034, 200 Mio. CHF/Jahr, Elektroheizungen, Wärmeverteilung | Belegt | [admin.ch](https://www.admin.ch/de/newnsb/qGTPQ1ZqqKag), [BAFU](https://www.bafu.admin.ch/de/foerderungen-im-gebaeudebereich) |

#### 14.6 Markt Basel-Stadt
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Ölfeuerungen | 1'677 (Juni 2026), alle Gebäudetypen | Belegt | [bs.ch, Open Data AUE](https://www.bs.ch/wsu/aue/abteilung-energie/meldung-fossilbefeuerte-heizungen) |
| Ölanteil Wohngebäude | 8 % BS, 25–40 % in den meisten Kantonen | Belegt | [BFS](https://www.bfs.admin.ch/bfs/de/home/statistiken/bau-wohnungswesen/gebaeude/energiebereich.html) |
| Gas-Liegenschaften | knapp 11'000 (2024) | Belegt | Presse über IWB, siehe [bz Basel](https://www.bzbasel.ch/basel/basel-stadt/netto-null-bis-2037-trotz-fernwaerme-ausbau-stilllegung-des-gasnetzes-wird-zum-mammutprojekt-ld.2531385) |
| Gasnetz stillgelegt | bis 2037, ab 2028 ≈ 1'000 Anschlüsse/Jahr | Belegt | [IWB](https://www.iwb.ch/klimadreh/ratgeber/heizung-ersetzen/gasstilllegung-basel-stadt), [bs.ch](https://www.bs.ch/medienmitteilungen/wsu/2023-die-waermeversorgung-basel-stadt-wird-bis-2037-erneuerbar) |
| Neue Öl-/Gasheizungen verboten | seit 2017 | Belegt | [BKB](https://www.bkb.ch/de/privatkunden/magazin/2024/heizsysteme-basel-stadt-verzicht-auf-gas-und-oel-bis-2037-lohnt-sich-auch-finanziell) |
| Gebiete ohne Fernwärme | 5,3 km² mit dezentraler Lösung vorgesehen (Fernwärme 12,2 km²) | Belegt + Abgeleitet | Geoportal BS, Teilrichtplan Energie (WFS `ms:EP_Energierichtplan_*`), Flächen eigene Berechnung, `dashboard/karte_fernwaerme.html` |

#### 14.7 Nordwestschweiz (siehe KUNDE_NORDWESTSCHWEIZ.md)
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Region | BS, BL, AG (BFS-Grossregion) | Belegt | BFS |
| Strom BL | 30,20 Rp./kWh (EBL, N-Basis, 2026; MwSt. nicht angegeben) | Belegt | [EBL Mitteilung 2026](https://www.ebl.ch/hubfs/EBL/_EBL%20Website/Preisbl%C3%A4tter%202026/Mitteilung%20zu%20den%20Tarif%C3%A4nderungen%202026.pdf), Kopie in `daten/roh/elcom/` |
| Strom AG | 30,15 Rp./kWh (AEW, H4, 2026, inkl. MwSt.) | Belegt | [AEW info August 2025](https://www.aew.ch/sites/default/files/2025-11/AEW_info_August_2025_Mitteilungen_zu_Tarifaenderungen_im_Jahr_2026_neu3.pdf) |
| Gas BL/AG | wie IWB 2026 | Annahme | für AG ohne Quelle |
| Öl- und Gas-Wohngebäude BL | 28,9 % / 30,7 % von 66'780 (2024) | Belegt | [Energiestatistik BL 2024](https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/daten-statistik/abteilung-statistik/publikationen-und-statistiken/energie/webartikel-vom-07-07-2026-energiestatistik-2024) |
| Öl- und Gas-Wohnungen AG | 135'574 / 58'620 von 348'656 (2024) | Belegt | [Statistisches Jahrbuch AG 2025](https://www.ag.ch/app/staag/statistisches_jahrbuch/chapters/09_bau.html) |
| Wetter | Basel 2025 für die ganze Region | Annahme | Aargau etwas kühler |

#### 14.8 Was die Kundenperspektive nicht annimmt
- Gewinn und Preise von DigitalHeat: Säule Firma (anderer Chat)
- Rechenpreise, Aufträge und Sicherheit: Säule Pharma
- Hardwarekosten: nur als Begründung, warum der Haushalt nicht selbst kauft


<!-- Ende Quelldatei KUNDENVIEW.md -->

<!-- Beginn Quelldatei ERGEBNISSE.md -->

## Ergebnisse Referenzhaus Basel 2025 (Stand 20.11.2026)

Reproduzieren:
```
python3 src/referenzprofil.py                     # Stundenprofil aus Open-Meteo
python3 src/jobtypen.py                           # Jobtypen A und B
python3 src/scheduler/jahr.py                     # 1–13 Server, alle Szenarien → daten/ergebnisse/serverzahl.json
python3 src/scheduler/jahr.py --server 8 --stunden daten/ergebnisse/stunden_8_spot.csv
.venv/bin/python src/scheduler/live.py --tag 2025-01-15 --server 8   # echter Job, Januar
.venv/bin/python src/scheduler/live.py --tag 2025-07-15 --server 8   # echter Job, Juli
python3 src/dashboard_daten.py                    # Zahlen fürs Dashboard → dashboard/daten.js
bash dashboard/starten.sh                         # Dashboard auf http://localhost:8765
```

Das Dashboard zeigt alle Kennzahlen für 1–13 Server und beide Nachfrageszenarien. Strompreis, Rechenpreis und Hardwarekosten lassen sich verschieben, das Urteil «rechnet sich / rechnet sich nicht» folgt sofort. Läuft `live.py`, zeigt es den echten Prozess (rechnet oder pausiert) jede Sekunde.

### Kennzahlen für 8 Server pro Haus (Vorschlag)

Szenario **Spot**: Typ A wird jederzeit vom Spot-Markt abgenommen (Annahme: unbegrenzte Nachfrage, ohne Frist). Typ B kommt begrenzt nach Alibaba-Trace (40 Jobs pro Tag, Frist 2 h).

| Kennzahl | Wert |
|---|---|
| Server pro Haus | **8** |
| Deckung des Wärmebedarfs (Heizung + Warmwasser, 31'231 kWh) | **93,0 %** (29'027 kWh, Rest 2'203 kWh vom Backup) |
| Abgeführte Wärme | **5 kWh** (0,02 % der Serverwärme) |
| Auslastung | **51,8 %** (36'290 Server-h ÷ 8 × 8'760) |
| Verpasste Fristen | **0,0 %** von 14'390 Jobs mit Frist |
| Stromkosten | 12'066 CHF (36'290 kWh × 0,3325) |
| Wert der genutzten Wärme | 3'861 CHF (29'027 kWh × 0,133) |
| Rechenerlös bei 1,06 CHF/Server-h | 38'409 CHF |
| **Break-even-Rechenpreis** | **0,226 CHF pro Server-h** = (12'066 − 3'861) ÷ 36'290 |
| Höchstens tragbare Hardwarekosten | 3'775 CHF pro Server und Jahr (beim Rechenpreis 1,06 CHF/Server-h) |

### Warum 8 Server
| Server | 4 | 6 | **8** | 10 | 12 |
|---|---|---|---|---|---|
| Deckung | 58,1 % | 79,6 % | **93,0 %** | 99,3 % | 100 % |
| Auslastung | 64,7 % | 59,1 % | **51,8 %** | 44,2 % | 37,2 % |
| Abgeführt | 0 | 0 | **5 kWh** | 12 kWh | 28 kWh |
| Max. Hardware/Server/Jahr | 4'715 | 4'310 | **3'775** | 3'226 | 2'712 CHF |

- Bis 8 Server bringt jeder weitere Server 6–13 Prozentpunkte Deckung, der 9. nur noch 3,9.
- Die Kosten tragen die Winterstunden: Ab Server 9 laufen die zusätzlichen Server nur in wenigen kalten Stunden, die Auslastung fällt unter 50 %.
- 12,5 Server für die kälteste Stunde wären 100 % Deckung bei 37 % Auslastung.

### Jahresverlauf (8 Server, Spot)
| Monat | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Deckung | 86 % | 90 % | 98 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 92 % | 89 % |
| Auslastung | 97 % | 96 % | 84 % | 48 % | 22 % | 8 % | 8 % | 8 % | 20 % | 53 % | 84 % | 96 % |

Von Juni bis August laufen die Server nur noch für das Warmwasser (0,6 Server). **Das Sommerloch ist das Problem der Wirtschaftlichkeit, nicht die Deckung.**

### Wann es sich nicht lohnt
1. **Rechenpreis unter 0,226 CHF pro Server-h:** Dann deckt der Erlös nicht einmal den Strom abzüglich Wärmewert. Das gilt unabhängig von der Serverzahl, solange keine Wärme abgeführt wird.
2. **Hardware:** Mit Hardware gilt: nötiger Rechenpreis = Hardware pro Server und Jahr ÷ 4'538 Server-h + 0,226 CHF.
   Beispiel (nur zur Illustration, Hardwarepreis nicht recherchiert): Kostet ein 1-kW-GPU-Server über 5 Jahre 9'000 CHF pro Jahr, braucht es **2,21 CHF pro Server-h** (≈ 1,64 $ pro H100-GPU-h). Das liegt im Bereich heutiger Spot-Preise (0,79–2,50 $), aber nicht am unteren Rand.
   **Bei 1,06 CHF/Server-h (unterster Spot-Preis) lohnt es sich nur, wenn ein Server weniger als 3'775 CHF pro Jahr kostet.**
3. **Ohne flexible Nachfrage (Szenario Alibaba):** Kommen alle Jobs mit Frist nach Alibaba-Trace, sinkt die Deckung bei 8 Servern auf 51,7 %. Im Sommer müssen 7'506 kWh Wärme abgeführt werden, weil die Jobs vor ihrer Frist laufen müssen. Der Break-even steigt auf 0,260 CHF.
   Mit der Regel «abgeben» gehen 9'608 Jobs (8'990 Server-h) an andere Standorte. Abgeführt werden nur noch 316 kWh. **Genau diese 9'000 Server-h im Sommer bräuchten einen Abnehmer mit Sommerwärmebedarf** (Hotel mit Spa, Maistrockner).

### Scheduler (Muss-Kriterium 2)
- Kern: `src/scheduler/kern.py`, Funktion `entscheide`. Pro Stunde: Pflichtjobs (Frist in Gefahr, 2 h Puffer) zuerst, dann nach frühester Frist so viel Arbeit, bis Wärmebedarf plus freier Speicher gedeckt sind. Pausierbare Jobs halten mitten in der Arbeit an.
- Speicher: 35 kWh, verlustfrei. Überschuss füllt den Speicher, erst dann wird abgeführt.
- Wärme nicht gebraucht und Frist drängt: Regel `rechnen` (Wärme abführen) oder `abgeben` (Job geht an einen anderen Standort, kein Erlös hier).
- Derselbe Kern steuert den echten Prozess (`src/scheduler/live.py`) über `Haus.schritt`:
  - Januar: alle 8 Server laufen durchgehend, der echte Job rechnet die ganze Stunde.
  - Juli: Speicher voll, nur Warmwasser. Der Scheduler fährt 0,62 Server, der echte Job läuft 62 % jeder Stunde und ist sonst mit SIGSTOP pausiert.
  - Am Ende SIGTERM → Checkpoint. Der nächste Lauf macht dort weiter (getestet: 2'688 → 4'864 → 6'528 Texte).

### Annahmen und Grenzen
Alle Annahmen mit Quelle stehen in `src/scheduler/annahmen.py` und in jeder Ergebnisdatei (`daten/ergebnisse/serverzahl.json`, Feld `annahmen`). Die wichtigsten:
- **Unbegrenzte Spot-Nachfrage für Typ A** (Szenario Spot). Das ist die stärkste Annahme. Das Szenario Alibaba zeigt, was ohne sie passiert.
- Rechenpreis 1,26 $/Server-h (unterster Spot-Preis × 1,6 GPU/kW), Wechselkurs 0,84 CHF/$ (Stand 20.11.2026).
- Hardwarekosten nicht im Modell, nur als Schwelle ausgewiesen.
- Wärmeabgabe = Strom × 0,8, unabhängig von der Auslastung der GPU im Server. Läuft ein Server, läuft er voll (Alibaba zeigt im Median 4 % GPU-Nutzung: Jobs müssen dicht gepackt werden).
- Stündliche Auflösung, perfekte Kenntnis des Bedarfs der laufenden Stunde, keine Prognose über die Stunde hinaus.
- Speicher ohne Verluste, Warmwasser gleichmässig über den Tag (0,5 kWh pro Stunde).
- Ankünfte nach Alibaba-Tagesform in UTC+8, nicht auf Basel umgerechnet.


<!-- Ende Quelldatei ERGEBNISSE.md -->

<!-- Beginn Quelldatei RESULTATE_EINFACH.md -->

## Rechnen, das heizt – die Resultate einfach erklärt

### Die Idee
Ein Server braucht Strom und macht daraus fast vollständig Wärme. Normalerweise wird diese Wärme weggekühlt. Wir stellen die Server in den Keller eines Hauses: Sie rechnen KI-Aufträge und heizen dabei das Haus und das Warmwasser.

### Das Testhaus
- Einfamilienhaus in Basel, Wetter des ganzen Jahres 2025
- Braucht im Jahr **31'231 kWh Wärme** (Heizung 26'851 + Warmwasser 4'380)
- An den kältesten Tagen bis 10 kW Heizleistung
- Ein Wassertank speichert 35 kWh Wärme
- Ein Server: 1 kW Strom → 0,8 kW nutzbare Wärme

### Das Ergebnis: 8 Server pro Haus

| Kennzahl | Ergebnis | Was das heisst |
|---|---|---|
| Server pro Haus | **8** | |
| Wärmebedarf gedeckt | **93 %** | Nur 7 % muss die normale Heizung liefern, an den kältesten Tagen |
| Verschwendete Wärme | **5 kWh im Jahr** | Praktisch nichts wird weggekühlt |
| Auslastung | **52 %** | Die Server rechnen gut die Hälfte der Zeit |
| Verpasste Fristen | **0 %** | Jeder Auftrag mit Frist wird rechtzeitig fertig |
| Break-even-Preis | **0,23 CHF pro Server-Stunde** | Ab diesem Preis decken die Rechenerlöse den Strom (abzüglich Wert der Wärme) |

### Warum genau 8 Server?
- Mehr Server = mehr Wärme, aber jeder Server rechnet seltener.
- Bis 8 Server bringt jeder weitere Server viel zusätzliche Wärme. Ab dem 9. kaum noch.
- 12–13 Server würden 100 % decken, wären aber nur zu 35 % ausgelastet. Das lohnt sich nicht.

### Das Problem: der Sommer
- Im Winter laufen die Server fast pausenlos (96 % Auslastung).
- Im Sommer braucht das Haus nur Warmwasser, die Server laufen dann nur zu **8 %**.
- **Lösung:** Im Sommer gehen die Aufträge an Orte, die dann Wärme brauchen, etwa ein Hotel mit Spa oder eine Trocknungsanlage in der Landwirtschaft.

### Lohnt es sich?
- **Der Strom ist nicht das Problem.** Schon ab 0,23 CHF pro Server-Stunde rechnet es sich. Rechenzeit wird heute für etwa 1–4 CHF pro Stunde verkauft.
- **Entscheidend sind die Kosten der Hardware.** Bei einem Rechenpreis von 1,06 CHF pro Stunde darf ein Server höchstens rund **3'800 CHF pro Jahr** kosten.
- **Es lohnt sich NICHT, wenn:**
  - der Rechenpreis unter 0,23 CHF pro Stunde fällt, oder
  - die Hardware teurer ist, als die Erlöse hergeben, oder
  - es nicht genug flexible Aufträge gibt. Dann deckt das System nur 52 % und muss im Sommer Wärme wegkühlen.

### Welche Aufträge passen?
| Auftrag | Dauer | Unterbrechbar | Frist | Herkunft der Zahlen |
|---|---|---|---|---|
| Texte für eine Suche aufbereiten (Embeddings) | ca. 1 h | ja | 24 h | **selbst gemessen** auf dem Laptop |
| Bilder auf Objekte prüfen | ca. 7 min | nein | 2 h | MLPerf-Messungen eines Servers |

- Gut passen Aufträge, die **warten können** und sich **pausieren lassen**. Sie werden dann gerechnet, wenn das Haus Wärme braucht.
- Eilige Aufträge laufen sofort. Wird ihre Wärme nicht gebraucht, landet sie im Speicher oder der Auftrag geht an einen anderen Standort.

### Echt getestet
- Ein echter KI-Auftrag läuft auf dem Laptop: 85 Texte pro Sekunde bei 28,9 Watt (gemessen).
- Der Scheduler pausiert und startet ihn je nach Wärmebedarf:
  - **Januar:** Das Haus braucht viel Wärme, der Auftrag läuft durchgehend.
  - **Juli:** Der Speicher ist voll, der Auftrag läuft nur 62 % jeder Stunde und ist sonst pausiert.
- Nach einem Stopp macht der Auftrag genau dort weiter, wo er aufgehört hat. Das Ergebnis ist identisch.

### Wichtigste Annahmen
- Es gibt immer genug Rechenaufträge zu kaufen (Spot-Markt). Ohne diese Annahme sinkt die Deckung auf 52 %.
- Strompreis 33,25 Rp./kWh (IWB Basel 2026). Die Wärme ist 13,3 Rp./kWh wert, weil sie eine Wärmepumpe ersetzt.
- Rechenpreis rund 1,06 CHF pro Server-Stunde (günstigster Marktpreis, 1 $ = 0,84 CHF).
- Hardwarekosten sind nicht eingerechnet, sondern als Grenze angegeben.

### In einem Satz
**8 Server pro Haus decken 93 % der Wärme und verschwenden fast nichts. Es lohnt sich, wenn ein Server weniger als rund 3'800 CHF pro Jahr kostet und es im Sommer einen zweiten Wärmeabnehmer gibt.**


<!-- Ende Quelldatei RESULTATE_EINFACH.md -->

<!-- Beginn Quelldatei KUNDENPERSPEKTIVE.md -->

## Kundenperspektive (Haushalt) – Stand 21.11.2026

> Zusammengeführt in **KUNDENVIEW.md** (Gesamtdokument). Diese Datei bleibt als Arbeitsstand.

Rechnung: `python3 src/kunde/wirtschaftlichkeit.py` → `daten/ergebnisse/win_win_win.json`. Die Physik (Deckung, Strom, Auslastung) kommt aus derselben Jahressimulation wie die Bilanz. «ANNAHME» = selbst gesetzt, noch zu prüfen.

### 1. Vorgehen für die Kundenperspektive
1. **Kunde festlegen:** Eigentümer eines Einfamilienhauses in Basel **mit Ölheizung**, der aus dem Öl aussteigen will, ohne gleich eine teure Wärmepumpe und Sanierung zu finanzieren (Pilot, Abschnitt 3b).
2. **Heutige Kosten kennen:** Was zahlt der Haushalt heute für Wärme (Öl, Gas, Wärmepumpe) und was würde ein Heizungsersatz kosten?
3. **Angebot rechnen:** Wer zahlt was (Server, Strom, Installation, Wärme)? Mehrere Modelle vergleichen.
4. **Einwände sammeln:** Lärm, Platz, Sicherheit, Haftung, Internet, was passiert beim Ausfall, beim Umzug, nach Vertragsende?
5. **Schnittstellen klären:** Was das Kundenangebot von der Firma und vom Pharmakunden braucht (Abschnitt 4), mit den Kollegen abstimmen.
6. **Dashboard ableiten:** Was will der Kunde jeden Tag sehen (Smart-Home-App), was nur ab und zu (eigenes Dashboard)?

### 2. Wer zahlt den Server?
**Empfehlung: DigitalHeat zahlt und besitzt alles** (Server, Installation, Strom der Server). Das ist auch das Modell auf digitalheat.ch («kein Hardwarekauf durch den Wärmeabnehmer») und bei Heata (UK) und Deep Green (UK).

Gründe:
- Eine 8-kW-Einheit kostet rund **258'000 CHF Hardware + 32'000 CHF Kühlung, Einbau, Speicher und Netzwerk = 290'000 CHF** (KOSTEN_DH.md). Das kann und will kein Haushalt tragen.
- Die Hardware ist nach rund 5 Jahren abgeschrieben, das Risiko (Preis der Rechenzeit, Auslastung, Defekte) gehört zu dem, der die Rechenzeit verkauft.
- Der Server hat einen eigenen Stromzähler. Der Haushalt zahlt keinen Server-Strom.

| Modell | Haushalt zahlt | Haushalt bekommt | Bewertung |
|---|---|---|---|
| **A Gratiswärme** (empfohlen für den Pilot) | nichts, stellt Platz und Anschluss | Wärme gratis | sehr einfach zu verkaufen |
| **B Wärmeabo** | Preis pro kWh, legt die Säule Firma fest (Beispiel 9,3 Rp. = 30 % unter Wärmepumpe) | günstigere Wärme | schwächeres Argument, Ersparnis siehe 3d |
| C Kunde kauft die Anlage | ≈ 290'000 CHF | Anteil am Rechenerlös | nicht sinnvoll: zu teuer, zu riskant |

### 3. Was spart der Haushalt? (Modell A, Gratiswärme)

| | Referenzhaus (Case) | Durchschnitts-EFH |
|---|---|---|
| Wärmebedarf (Heizung + Warmwasser) | 31'231 kWh | 17'000 kWh |
| Einheit | 8 kW | 5 kW (kleinste DigitalHeat-Einheit) |
| Wärme vom Server | **92,9 %** | **99,6 %** |
| Heizkosten heute mit **Wärmepumpe** | 4'154 CHF/Jahr | 2'261 CHF/Jahr |
| Heizkosten heute mit **Ölheizung** | 6'118 CHF/Jahr | 3'330 CHF/Jahr |
| **Ersparnis vs. Wärmepumpe** | **3'861 CHF/Jahr** | **2'252 CHF/Jahr** |
| **Ersparnis vs. Ölheizung** | **5'686 CHF/Jahr** | **3'317 CHF/Jahr** |
| Vermiedener Heizungsersatz (Wärmepumpe 45'000 − 10'500 Förderung, 18 Jahre) | + 1'917 CHF/Jahr | + 1'917 CHF/Jahr |
| **Total für Ölheizungs-Besitzer, der ersetzen muss** | **≈ 7'600 CHF/Jahr** | **≈ 5'200 CHF/Jahr** |

Mit Modell B (Wärmeabo) spart der Haushalt noch 1'158 bzw. 676 CHF/Jahr gegenüber einer Wärmepumpe, gegenüber Öl 2'984 bzw. 1'740 CHF/Jahr.

Grundlagen: Strom 33,25 Rp./kWh (ElCom 2026, IWB), Wärmepumpe JAZ 2,5 (Case) → 13,3 Rp./kWh Wärme. Heizöl 1,665 CHF/l (Anfang Nov. 2026), Kessel 85 % → 19,6 Rp./kWh Wärme. Wärmepumpe Basel 31'500–63'000 CHF (handwerker-kosten.ch), Förderung BS 2026 ≈ 10'500 CHF für 8 kW (ion-e.ch, nicht amtlich bestätigt).

**Wichtigster Vorbehalt:** Ob die Serverheizung in Basel als erneuerbarer Heizungsersatz gilt (Energiegesetz BS), ist offen. Nur dann entfällt die neue Wärmepumpe. Klärung beim Amt für Umwelt und Energie, Abteilung Energie.

### 3b. Pilot: Umstieg für Ölheizungs-Besitzer
**Idee:** Die Serverheizung ersetzt keine Wärmepumpe. Sie wird **neben die bestehende Ölheizung** gebaut. Die Ölheizung bleibt als Backup für die kältesten Stunden. So steigt der Haushalt ohne eigene Investition sofort fast ganz aus dem Öl aus und kann später in Ruhe entscheiden, was nach dem Ende des Ölkessels kommt.

**Was sich für den Haushalt ändert** (Gratiswärme, flexible Aufträge vorausgesetzt):

| | Referenzhaus (31'231 kWh) | Durchschnitts-EFH (17'000 kWh) |
|---|---|---|
| Heizöl heute | 3'674 l/Jahr | 2'000 l/Jahr |
| Heizöl mit Serverheizung | **259 l/Jahr (−93 %)** | **8 l/Jahr (−100 %)** |
| Heizkosten heute | 6'118 CHF/Jahr | 3'330 CHF/Jahr |
| Heizkosten mit Serverheizung | **432 CHF/Jahr** | **13 CHF/Jahr** |
| **Ersparnis** | **5'686 CHF/Jahr** | **3'317 CHF/Jahr** |
| CO2 heute → nachher | 9,7 t → **0,7 t** | 5,3 t → **0,0 t** |
| Eigene Investition | **0 CHF** | **0 CHF** |

Gibt es zu wenig flexible Aufträge (Szenario «Nur Jobs mit Frist»), sinkt der Ölverbrauch nur um 52 % bzw. 63 % (Ersparnis 3'164 bzw. 2'104 CHF/Jahr). Die Antwort der Säule Pharma dazu ist deshalb für den Pilot entscheidend.

Grundlagen: Heizöl 1,665 CHF/l (Anfang Nov. 2026), 10 kWh/l, Ölkessel 85 % (ANNAHME), 2,65 kg CO2 pro Liter Heizöl EL. Die CO2-Abgabe steckt im Ölpreis.

**Warum das gerade für Ölheizungs-Häuser passt**
- **Keine Sanierung nötig:** Alte Häuser mit Ölheizung haben oft Radiatoren, die 55–70 °C brauchen. Eine Wärmepumpe arbeitet dort schlecht oder braucht zuerst Dämmung und neue Heizkörper. Die Serverheizung liefert laut DigitalHeat 50–70 °C Vorlauf und passt an die bestehenden Radiatoren.
- **Keine Investition, kein Zeitdruck:** Der Ölkessel läuft weiter als Backup. Der Heizungsersatz wird um Jahre verschoben, und bis dahin sind kaum noch Öl und CO2 im Spiel.
- **Sofort sichtbar:** Der Öltank leert sich kaum noch. Das sieht der Kunde direkt, auch ohne App.
- **Rechtlich einfacher (ANNAHME, zu prüfen):** Weil der Ölkessel nicht ersetzt, sondern ergänzt wird, greift die Ersatzpflicht für erneuerbare Heizungen in Basel-Stadt im Pilot vermutlich noch nicht. Beim späteren Ersatz des Kessels stellt sich die Frage wieder.

**Markt in Basel-Stadt**
- **1'677 Ölfeuerungen (Juni 2026)**, nach 1'729 (Dez. 2025), 1'847 (Ende 2024) und 2'631 (Ende 2018). Quelle: Open Data des Amts für Umwelt und Energie BS, gemeldete Anlagen, alle Gebäudetypen, nicht nur Einfamilienhäuser.
- Öl heizt in BS nur noch 8 % der Wohngebäude (BFS). In den meisten anderen Kantonen sind es 25–40 %.
- Neue Öl- und Gasheizungen sind in BS seit 2017 grundsätzlich verboten. Ziel des Kantons: fossilfreie Wärme bis 2037.
- **Folge für den Pilot:** Basel-Stadt eignet sich als Testgebiet, der grosse Markt liegt aber in den Nachbarkantonen (z. B. Basel-Landschaft) und in der übrigen Schweiz. Spätestens 2037 muss der Öl-Backup in BS durch ein erneuerbares Backup ersetzt werden.

**Gas in Basel-Stadt**
- IWB liefert Gas an **knapp 11'000 Liegenschaften** in Basel, Riehen und Bettingen (Bericht 2024, Liegenschaften, nicht Heizungen). Das sind rund sechsmal mehr als Ölfeuerungen.
- Der Grosse Rat hat im Januar 2023 beschlossen: **Das Gasnetz wird bis 2037 stillgelegt.** Erste Stilllegungen 2026/2027, **ab 2028 nimmt IWB rund 1'000 Gasanschlüsse pro Jahr vom Netz.**
- Rund die Hälfte der Gasheizungen ist älter als 15 Jahre (IWB-CEO, laut Presse).
- Wo möglich, ersetzt IWB das Gas durch **Fernwärme**. Wo Fernwärme noch fehlt, kann der Regierungsrat die Gasversorgung befristet verlängern.

**Was das für die Kundenperspektive heisst**
- **Gas-Haushalte müssen wechseln, ob sie wollen oder nicht**, mit festem Datum. Das ist ein grösserer und dringenderer Markt als Öl.
- **Aber:** Der Gas-Backup läuft mit der Stilllegung aus. Ein Gas-Haushalt braucht beim Umstieg auf die Serverheizung ein anderes Backup (z. B. eine kleine Wärmepumpe oder einen Elektroeinsatz im Speicher).
- **Konkurrenz Fernwärme:** Im Fernwärmegebiet ist der Anschluss an die Fernwärme die naheliegende Lösung, und kantonale Förderung für dezentrale Heizungen ist dort halbiert. Die Serverheizung zielt deshalb auf **Gas-Haushalte ausserhalb des Fernwärmegebiets** (z. B. in Riehen und Bettingen).
- **Folge für die Reihenfolge:** Öl bleibt der beste Einstieg für den Pilot (Backup bleibt, höchste Ersparnis). Gas ist danach der grösste Markt in Basel-Stadt, mit klarem Termindruck bis 2037.

**Backup für Gas-Haushalte: Heizstab statt Gas**
Wird der Gasanschluss aufgegeben, übernimmt ein Heizstab im Wärmespeicher die letzten Prozente (einmalig ≈ 2'000 CHF, ANNAHME).

| Gratiswärme | Referenzhaus | Durchschnitts-EFH |
|---|---|---|
| Strom für den Heizstab | 2'203 kWh = 733 CHF/Jahr | 68 kWh = 23 CHF/Jahr |
| Ersparnis vs. Gas mit Gas-Backup | 4'520 CHF/Jahr | 2'636 CHF/Jahr |
| **Ersparnis vs. Gas mit Heizstab** (keine Grundgebühr mehr) | **4'325 CHF/Jahr** | **2'819 CHF/Jahr** |

**Wichtig:** Der Heizstab lohnt sich nur, wenn die Serverheizung fast alles deckt. Gibt es zu wenig flexible Aufträge, müsste der Heizstab 6'000–15'000 kWh liefern, und die Ersparnis fällt fast auf null (Referenzhaus 44 CHF/Jahr). Ob ein Heizstab als Notheizung erlaubt ist, muss das AUE BS bestätigen.

**Karte:** `dashboard/karte_fernwaerme.html` zeigt die Gebiete ohne Fernwärme (Energierichtplan BS): vor allem Bruderholz, Riehen, Bettingen und Teile am Westrand von Basel, zusammen rund 5,3 km².

**Ganze Nordwestschweiz (BS, BL, AG):** siehe `KUNDE_NORDWESTSCHWEIZ.md`.

**Warum mit Öl anfangen (Einstiegsstrategie)**
Ölheizungs-Besitzer in Basel-Stadt sind die Gruppe mit dem grössten Druck und dem grössten Gewinn: höchste Heizkosten (19,6 Rp./kWh Wärme), politisches Ziel «fossilfrei bis 2037», oft alte Häuser, in denen eine Wärmepumpe schlecht passt. Sie wechseln am schnellsten und werden zu sichtbaren Referenzen. Danach folgen die anderen:

| Phase | Zielgruppe | Argument |
|---|---|---|
| **1 Pilot** | Ölheizungen in Basel-Stadt (5–10 EFH) | −93 bis −100 % Heizöl, 0 CHF Investition, Referenzen schaffen |
| **2 Ausrollen Öl** | Ölheizungen in Basel-Landschaft und weiteren Kantonen (25–40 % Ölanteil) | gleiches Angebot, grosser Markt |
| **3 Gas** | Gasheizungen (BS: Gasnetz wird bis 2037 stillgelegt, siehe unten) | Ausstieg aus Gas ohne eigene Investition |
| **4 Alle Haushalte** | Häuser mit Wärmepumpe oder Neubauten, Mehrfamilienhäuser | Gratiswärme statt Strom für die Wärmepumpe, Warmwasser im Sommer |

**Pilot-Aufbau (Vorschlag)**
| | |
|---|---|
| Teilnehmende | 5–10 Einfamilienhäuser in Basel mit Ölheizung |
| Voraussetzungen | Platz im Keller oder Heizraum (Öltank-Raum wird oft frei), Wasser-Heizsystem, Starkstromanschluss, Glasfaser oder gutes Internet |
| Dauer | 1 Jahr, damit Winter und Sommer drin sind |
| Kosten für den Haushalt | keine. Einbau, Server, Strom und Rückbau zahlt DigitalHeat |
| Was gemessen wird | Heizöl in Litern (vorher/nachher), Wärme vom Server, Raumtemperatur und Komfort, Lärm, Ausfälle, Zufriedenheit |
| Nach dem Pilot | Kunde wählt: weiter mit Gratiswärme oder Wärmeabo, oder Rückbau ohne Kosten |

### 3c. Vergleich: Serverheizung gegen Öl, Gas und Wärmepumpe
**Was kostet 1 kWh Wärme?**

| Heizung | Rp. pro kWh Wärme | Grundlage |
|---|---|---|
| Ölheizung | **19,6** | 1,665 CHF/l, 10 kWh/l, Kessel 85 % |
| Gasheizung | **15,6** + 195 CHF/Jahr Grundgebühr | IWB 2026, Stufe M, inkl. MwSt.: 11,57 + CO2-Abgabe 2,33 + Konzession 0,11 Rp./kWh Gas, Kessel 90 % |
| Wärmepumpe | **13,3** | Strom 33,25 Rp./kWh, JAZ 2,5 |
| Serverheizung, Wärmeabo | 9,3 | 30 % unter Wärmepumpe |
| **Serverheizung, Gratiswärme** | **0** | DigitalHeat zahlt Strom und Anlage |

**Ersparnis pro Jahr, wenn die Serverheizung neben die bestehende Heizung kommt** (Gratiswärme, flexible Aufträge)

| | Referenzhaus (31'231 kWh) | Durchschnitts-EFH (17'000 kWh) |
|---|---|---|
| **Öl:** heute → nachher | 6'118 → 432 CHF, **spart 5'686** | 3'330 → 13 CHF, **spart 3'317** |
| **Gas:** heute → nachher | 5'057 → 538 CHF, **spart 4'520** | 2'841 → 205 CHF, **spart 2'636** |
| **Wärmepumpe:** heute → nachher | 4'154 → 293 CHF, **spart 3'861** | 2'261 → 9 CHF, **spart 2'252** |
| CO2 Öl: heute → nachher | 9,7 → 0,7 t | 5,3 → 0,0 t |
| CO2 Gas: heute → nachher | 6,9 → 0,5 t | 3,7 → 0,0 t |

- Bei Gas bleibt die **Grundgebühr von rund 195 CHF/Jahr**, solange der Gasanschluss als Backup bleibt. Wird er später aufgegeben, fällt auch sie weg.
- Ohne genug flexible Aufträge (Szenario «Nur Jobs mit Frist») spart der Gas-Haushalt nur 2'515 bzw. 1'673 CHF/Jahr.
- Mit Wärmeabo statt Gratiswärme: Gas spart 1'817 bzw. 1'060 CHF/Jahr.
- **Reihenfolge der Attraktivität:** Öl vor Gas vor Wärmepumpe. Das bestätigt die Einstiegsstrategie mit Öl, Gas ist der logische zweite Schritt.

Vorbehalte: Die Stufe M gilt laut IWB-Beispiel für ein Einfamilienhaus mit 20'000 kWh. Für das Referenzhaus (≈ 35'000 kWh Gas) ist die Stufe abgeleitet, nicht bestätigt. Anschlussleistung 15 kW (Referenzhaus) ist eine Annahme, 12 kW (Durchschnitt) aus dem IWB-Beispiel. Kesselwirkungsgrade und CO2-Faktoren sind Annahmen.

### 3d. Ersparnis je nach Wärmepreis
Den Wärmepreis legt die Säule Firma fest (anderer Chat). Für den Haushalt zählt nur: **Bis zu welchem Preis lohnt sich der Wechsel?**

Ersparnis pro Jahr gegenüber der heutigen Heizung, Referenzhaus (29'027 kWh Serverwärme) / Durchschnitts-EFH (16'932 kWh):

| Wärmepreis | vs. Öl | vs. Gas | vs. Wärmepumpe |
|---|---|---|---|
| 0 Rp./kWh (gratis) | 5'686 / 3'317 | 4'520 / 2'636 | 3'861 / 2'252 |
| 3 Rp./kWh | 4'815 / 2'809 | 3'649 / 2'128 | 2'990 / 1'744 |
| 5 Rp./kWh | 4'235 / 2'470 | 3'069 / 1'789 | 2'410 / 1'405 |
| 8 Rp./kWh | 3'364 / 1'962 | 2'198 / 1'281 | 1'539 / 897 |
| 10 Rp./kWh | 2'783 / 1'624 | 1'617 / 943 | 958 / 559 |
| 13,3 Rp./kWh | 1'825 / 1'065 | 659 / 384 | 0 / 0 |

**Schwelle, ab der sich der Wechsel nicht mehr lohnt:** Öl 19,6 Rp., Gas 15,6 Rp., Wärmepumpe 13,3 Rp. pro kWh Wärme.

Damit der Wechsel für einen Öl-Haushalt **deutlich** attraktiv ist (über 2'000 CHF Ersparnis im Durchschnitts-EFH), darf die Wärme höchstens rund **7 Rp./kWh** kosten. Diese Zahl ist die Bitte der Kundenperspektive an die Säule Firma.

### 4. Schnittstellen zu den anderen Säulen (von Kollegen zu bestätigen)
Diese Werte rechnet nicht die Kundenperspektive. Sie sind nur so weit drin, wie das Kundenangebot von ihnen abhängt.

| Was ich brauche | Von wem | Warum es für den Kunden zählt | Arbeitsannahme bis zur Bestätigung |
|---|---|---|---|
| Wer zahlt Hardware, Installation und Server-Strom? | Säule Firma | Davon hängt ab, ob Gratiswärme möglich ist | DigitalHeat zahlt alles |
| Kann sich die Firma Gratiswärme leisten, oder braucht es ein Wärmeabo? | Säule Firma | Bestimmt die Ersparnis (3'861 vs. 1'158 CHF/Jahr gegenüber WP) | Gratiswärme im Pilot |
| Wie viele flexible Aufträge gibt es das ganze Jahr? | Säule Pharma | Davon hängt ab, ob im Winter genug Wärme kommt (93 % vs. 52 % Deckung) | genug flexible Aufträge |
| Welche Einheitengrösse (kW) pro Haus? | Säule Firma | Lärm, Platz, Anschluss | 8 kW Referenzhaus, 5 kW Durchschnitt |
| Sicherheitsauflagen der Pharmakunden im Haus (Zugang, Plombe, Kamera?) | Säule Pharma | Was der Haushalt dulden muss | kein Zugang, verplombtes Gehäuse |
| Vertragslaufzeit, Kündigung, was bei Konkurs | Säule Firma | Vertrauen des Kunden | Backup-Heizung bleibt immer |

Eine erste Rechnung der Firmenseite (zur Kontrolle, nicht mein Teil) liegt in `daten/ergebnisse/win_win_win.json`.

### 5. Förderungen
| Programm | Für wen | Relevanz | Stand |
|---|---|---|---|
| **Förderbeiträge Energie Basel-Stadt** (Gesuch über dasgebaeudeprogramm.ch/bs) | Haushalt | Wärmepumpe 2026: 8'000 CHF + 250 CHF/kWth (Luft/Wasser), max. 40 % der Investition, halbiert im Fernwärmegebiet. **Serverheizung ist keine genannte Kategorie** | klären mit AUE BS |
| **Impulsprogramm Bund** (Klima- und Innovationsgesetz, 2025–2034, 200 Mio. CHF/Jahr, Vollzug durch Kantone) | Haushalt | fördert Ersatz von Elektroheizungen und den Einbau einer Wärmeverteilung (bis 100 %) | prüfen, ob anwendbar |
| **Gebäudeprogramm** (CO2-Abgabe) | Haushalt | Dämmung, erneuerbare Heizungen | über Kanton |
Förderungen sind im Rechenbeispiel nicht eingerechnet (ausser der vermiedenen Wärmepumpenförderung). Sie sind ein Zusatzvorteil.

Hinweis für die Säule Firma (nicht Teil der Kundenperspektive): BFE-Pilot- und Demonstrationsprojekte, Innosuisse und CO2-Bescheinigungen (z. B. Stiftung KliK, 5–10 t CO2 pro Haus und Jahr, wenn Öl verdrängt wird) könnten für DigitalHeat selbst in Frage kommen.

### 6. Partner, die der Kunde spürt
| Partner | Was der Kunde davon hat |
|---|---|
| **IWB** | bekannter Absender, Strom und Glasfaser aus einer Hand, Vertrauen |
| **Lokaler Heizungsinstallateur** | Einbau, Service und Backup-Heizung von jemandem aus der Region |
| **Smart-Home-Anbieter** (Loxone, Home Assistant, Homey, Matter) | Steuerung in der App, die er schon hat |
| **Versicherung** (z. B. Baloise) | Schäden an der Anlage sind nicht sein Risiko |
| **Bank** (grüne Hypothek, z. B. BKB) | günstigere Hypothek für ein Haus mit erneuerbarer Wärme |

### 7. Das Angebot an den Kunden in einem Satz
**DigitalHeat stellt eine Serverheizung kostenlos neben die Ölheizung, zahlt deren Strom und Unterhalt, und der Haushalt braucht über 90 % weniger Heizöl. Das spart 3'300–5'700 CHF pro Jahr, ohne eigene Investition und ohne Sanierung.**

Einwände und Antworten:
| Einwand | Antwort |
|---|---|
| «Was, wenn der Server ausfällt?» | Die Backup-Heizung bleibt und springt automatisch ein, der Speicher überbrückt Stunden |
| «Ist das laut?» | ANNAHME: Flüssigkeitskühlung ohne grosse Lüfter, im Keller hinter einer Tür; vor dem Pilot messen |
| «Wer haftet bei Schäden?» | DigitalHeat, über eine Versicherung |
| «Kommt jemand an meine Daten oder ich an fremde?» | Getrennte Netze, verplombtes Gehäuse, der Haushalt hat keinen Zugang |
| «Was, wenn ich umziehe?» | Vertrag geht auf den neuen Eigentümer über oder die Anlage wird zurückgebaut |
| «Brauche ich trotzdem eine neue Wärmepumpe?» | Offen, hängt vom Kanton ab (siehe Abschnitt 3) |

### 8. Was der Kunde sehen will (Grundlage fürs Dashboard)
**Smart-Home-App (nur das Wichtigste):**
- Wärme heute und diesen Monat vom Server (kWh, Anteil am Bedarf)
- **Ersparnis in CHF** diesen Monat und seit Start
- Speicher (Füllstand in %)
- Status: läuft / pausiert / Störung
- Ein Knopf: «Komfort» (wärmer) und «Abwesend» (Ferien)

**Eigenes Dashboard (Details):**
- Verlauf Wärme, Backup, abgeführte Wärme pro Tag und Monat
- Vergleich mit der alten Heizung (CHF, CO2)
- Rechenleistung: Stunden, für welchen Bereich (z. B. «Medikamentenforschung»), ohne Kundennamen
- Wartung, Vertrag, Förderung, Kontakte
- Prognose der nächsten Tage (Wetter, erwartete Wärme)

### 9. Offene Punkte
- Gilt die Serverheizung im Kanton Basel-Stadt als erneuerbarer Heizungsersatz?
- Lärm und Platzbedarf von 8 kW Servern im Keller
- Vertragslaufzeit, Umzug, was passiert bei Konkurs von DigitalHeat (Backup-Heizung muss bleiben)
- Antworten der anderen Säulen auf die Schnittstellen in Abschnitt 4


<!-- Ende Quelldatei KUNDENPERSPEKTIVE.md -->

<!-- Beginn Quelldatei KUNDE_NORDWESTSCHWEIZ.md -->

## Kundenperspektive Nordwestschweiz (Stand 21.11.2026)

> Zusammengeführt in **KUNDENVIEW.md** (Gesamtdokument). Diese Datei bleibt als Arbeitsstand.

Nordwestschweiz = Grossregion des BFS: **Basel-Stadt, Basel-Landschaft, Aargau**. (Solothurn gehört beim BFS zum Espace Mittelland und ist hier nicht drin.)

Die Physik (Deckung, Backup) ist dieselbe wie in Basel, gerechnet mit dem Wetter Basel 2025. Im Aargau ist es etwas kühler, die Deckung dürfte dort leicht tiefer liegen (nicht gerechnet).

### 1. Markt: Wie viele Öl- und Gasheizungen?
| Kanton | Öl | Gas | Bezug | Quelle |
|---|---|---|---|---|
| **Basel-Stadt** | 1'677 Ölfeuerungen (Juni 2026), 8 % der Wohngebäude | knapp 11'000 Gas-Liegenschaften (2024), Netz bis 2037 stillgelegt | Anlagen bzw. Liegenschaften | [bs.ch](https://www.bs.ch/wsu/aue/abteilung-energie/meldung-fossilbefeuerte-heizungen), [BFS](https://www.bfs.admin.ch/bfs/de/home/statistiken/bau-wohnungswesen/gebaeude/energiebereich.html), [IWB](https://www.iwb.ch/klimadreh/ratgeber/heizung-ersetzen/gasstilllegung-basel-stadt) |
| **Basel-Landschaft** | 28,9 % von 66'780 Wohngebäuden ≈ **19'300** | 30,7 % ≈ **20'500** | Wohngebäude 2024 | [Energiestatistik BL 2024](https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/daten-statistik/abteilung-statistik/publikationen-und-statistiken/energie/webartikel-vom-07-07-2026-energiestatistik-2024) |
| **Aargau** | 135'574 von 348'656 **Wohnungen** (39 %) | 58'620 Wohnungen (17 %) | Wohnungen 2024, nicht Gebäude | [Statistisches Jahrbuch AG 2025](https://www.ag.ch/app/staag/statistisches_jahrbuch/chapters/09_bau.html) |

Gerechnet: Anzahl BL = Anteil × 66'780 (eigene Rechnung). Im Aargau gibt es nur Zahlen pro Wohnung. Ein Mehrfamilienhaus zählt dort mehrfach, die Zahl der Gebäude ist deutlich kleiner.

**Folge:** Basel-Stadt ist der kleinste Markt und dient als Pilot. Allein Basel-Landschaft hat über **zehnmal mehr Ölheizungen** als Basel-Stadt. Im Aargau heizt noch fast jede zweite bis dritte Wohnung mit Öl.

### 2. Ersparnis des Haushalts pro Kanton (Gratiswärme, flexible Aufträge)
| | Basel-Stadt | Basel-Landschaft | Aargau |
|---|---|---|---|
| Strom H4 2026 | 33,25 Rp./kWh (IWB) | 30,20 Rp./kWh (EBL, N-Basis) | 30,15 Rp./kWh (AEW, inkl. MwSt.) |
| Wärme aus Wärmepumpe | 13,3 Rp./kWh | 12,1 Rp./kWh | 12,1 Rp./kWh |
| **Durchschnitts-EFH: spart vs. Öl** | **3'317 CHF** | **3'317 CHF** | **3'317 CHF** |
| Durchschnitts-EFH: spart vs. Gas | 2'636 CHF | ≈ 2'636 CHF* | ≈ 2'636 CHF* |
| Durchschnitts-EFH: spart vs. Wärmepumpe | 2'252 CHF | 2'045 CHF | 2'042 CHF |
| Referenzhaus: spart vs. Öl / Gas / WP | 5'686 / 4'520 / 3'861 | 5'686 / ≈ 4'520* / 3'507 | 5'686 / ≈ 4'520* / 3'501 |

\* Gaspreis aus dem IWB-Tarif 2026 übernommen (IWB beliefert auch Teile von BL, ausserhalb BS +0,06 Rp./kWh Abgaben). Für den Aargau ist das eine **Annahme**, dort liefern andere Gasversorger.

**Lesart:**
- Gegenüber **Öl** ist die Ersparnis überall gleich, weil Heizöl schweizweit ähnlich viel kostet.
- Gegenüber der **Wärmepumpe** ist die Ersparnis in BL und AG etwa 10 % kleiner, weil Strom dort günstiger ist.
- Am meisten gewinnen also überall die **Öl-Haushalte**. Die Einstiegsstrategie gilt in der ganzen Region.

### 3. Förderung und Regeln pro Kanton
| | Basel-Stadt | Basel-Landschaft | Aargau |
|---|---|---|---|
| Förderung Wärmepumpe (Vergleich) | 8'000 + 250 CHF/kWth, halbiert im Fernwärmegebiet | Energiepaket BL; 2026 neue Anreize, Beträge für Ölersatz nicht gefunden | Programm ab 1.5.2026; ältere Broschüre: 6'000 + 180 CHF/kWth; **keine Förderung im Verbundgebiet** |
| Zusatz | Impulsprogramm Bund | Impulsprogramm Bund | Zusatzbeitrag für erstmaliges Wärmeverteilsystem beim Ersatz fossiler Heizungen |
| Druck zum Wechsel | sehr hoch: Gasnetz bis 2037 zu, neue fossile Heizungen seit 2017 verboten | mittel (nicht im Detail geprüft) | eher tief (nicht im Detail geprüft) |
| Fernwärme-Karte | Energierichtplan, siehe `dashboard/karte_fernwaerme.html` | nicht erstellt | Online-Karten «Kommunale Energieplanung» und «Fernwärmekataster» des Kantons |
| Quelle | [ion-e.ch](https://www.ion-e.ch/de/waermepumpe-basel), [bs.ch](https://www.bs.ch/medienmitteilungen/wsu/2023-die-waermeversorgung-basel-stadt-wird-bis-2037-erneuerbar) | [baselland.ch](https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/umweltschutz-energie/medienmitteilungen/neue-anreize-im-kantonalen-foerderprogramm) | [ag.ch Förderung](https://www.ag.ch/de/verwaltung/bvu/energie/foerderung), [Wärmepumpen-Programm](https://www.ag.ch/media/kanton-aargau/bvu/energie/foerderungen/waermepumpen-foerderprogramm.pdf) |

Für die Serverheizung gibt es in keinem Kanton eine eigene Förderkategorie. Ob sie als erneuerbarer Heizungsersatz zählt, muss **jeder Kanton einzeln** beantworten.

### 4. Was das für die Strategie heisst
| Phase | Wo | Warum |
|---|---|---|
| 1 Pilot | Basel-Stadt, Öl, ausserhalb Fernwärme (Bruderholz, Riehen, Bettingen) | höchster Druck, kleine überschaubare Zahl, IWB als Partner |
| 2 Öl ausrollen | **Basel-Landschaft** (≈ 19'300 Öl-Wohngebäude), dann Aargau | grösster Markt, gleiche Ersparnis von 3'300–5'700 CHF/Jahr |
| 3 Gas | Basel-Stadt (Netz geht zu), dann BL (≈ 20'500 Gas-Wohngebäude) | Termindruck in BS, grosse Zahl in BL |
| 4 Alle | Wärmepumpen-Haushalte in der ganzen Region | kleinere Ersparnis (≈ 2'000 CHF/Jahr) |

**Grössenordnung (nur zur Einordnung):** Wechseln 1 % der Öl-Wohngebäude in Basel-Landschaft (≈ 190 Häuser), sparen diese Haushalte zusammen rund **0,6 Mio. CHF und 1'000 t CO2 pro Jahr** (190 × 3'317 CHF bzw. × 5,3 t).

### 5. Offen
- Gaspreise in BL und AG ausserhalb des IWB-Gebiets
- Regeln zum Heizungsersatz in BL und AG (Pflicht zu erneuerbarer Wärme?)
- Förderbeträge BL 2026, Bestätigung AG 2026
- Strompreise der übrigen Versorger (z. B. Primeo Energie in BL). Die ElCom-Schnittstelle lieferte am 21.11.2026 keine Daten, deshalb die Werte aus den Mitteilungen von EBL und AEW
- Ob EBL 30,20 Rp. inkl. oder exkl. MwSt. ist, steht nicht im Dokument


<!-- Ende Quelldatei KUNDE_NORDWESTSCHWEIZ.md -->

<!-- Beginn Quelldatei ANNAHMEN_KUNDE.md -->

## Annahmen der Kundenperspektive mit Quellen (Stand 21.11.2026)

> Zusammengeführt in **KUNDENVIEW.md** (Gesamtdokument). Diese Datei bleibt als Arbeitsstand.

Status:
- **Case** = Vorgabe von DigitalHeat im Hackathon
- **Belegt** = aus einer öffentlichen Quelle übernommen
- **Abgeleitet** = aus belegten Werten gerechnet
- **Annahme** = selbst gesetzt, ohne Quelle. Vor einer Entscheidung prüfen.

Rechnung: `src/kunde/wirtschaftlichkeit.py` (alle Werte stehen dort in `P` mit Quelle), Physik aus `src/scheduler/jahr.py`.

### 1. Haus und Wärmebedarf
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Wetter Basel 2025, stündlich | Open-Meteo, 47.56 N 7.55 E | Case, Belegt | offizielles Case-CSV, identisch mit [Open-Meteo Archiv](https://open-meteo.com/en/docs/historical-weather-api) |
| Heizbedarf Referenzhaus | max(0, 10 kW × (20 − T) ÷ 25,6) an Heiztagen = 26'851 kWh | Case | Case-Formel |
| Warmwasser | 12 kWh/Tag = 4'380 kWh/Jahr, gleichmässig über den Tag | Case | Case; Verteilung über den Tag = Annahme |
| Durchschnitts-EFH | 17'000 kWh/Jahr Wärme | Annahme | abgeleitet aus [Raiffeisen](https://www.raiffeisen.ch/rch/de/wissen/wohnen/energiesparen-erneuerbare-heizung.html): EFH mit 2'000 l Heizöl/Jahr × 10 kWh/l × 85 % |
| Speicher | 35 kWh, verlustfrei | Case | Case |

### 2. Serverheizung
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Wärme pro Server | 1 kW Strom → 0,8 kW nutzbare Wärme | Case | Case |
| Einheitengrösse | 8 kW Referenzhaus, 5 kW Durchschnitts-EFH | Abgeleitet | Jahressimulation; DigitalHeat nennt 5–20 kW pro Einheit ([digitalheat.ch](https://digitalheat.ch)) |
| Vorlauftemperatur | 50–70 °C, passt zu alten Radiatoren | Belegt | [digitalheat.ch](https://digitalheat.ch) |
| Kühlung | direkte Flüssigkeitskühlung, Wärmetauscher trennt Kühlkreis und Heizwasser | Belegt | [digitalheat.ch](https://digitalheat.ch) |
| Deckungsgrad | 93 % (Referenz) / 99,6 % (Durchschnitt) | Abgeleitet | Jahressimulation, **setzt genug flexible Rechenaufträge voraus** (Säule Pharma) |
| Deckung ohne genug Aufträge | 52 % / 63 % | Abgeleitet | Jahressimulation mit Nachfrage aus dem Alibaba-Trace |
| Server-Strom zahlt nicht der Haushalt | eigener Zähler | Annahme | so bei [Heata](https://www.techradar.com/news/this-company-will-pay-for-your-heating-if-you-let-it-install-a-server-in-your-house) und [Deep Green](https://techradar.com/news/this-startup-is-recycling-energy-to-heat-swimming-pools-for-free); von Säule Firma zu bestätigen |
| Haushalt kauft keine Hardware | 0 CHF | Belegt (Absicht) | [digitalheat.ch](https://digitalheat.ch): «kein Hardwarekauf durch den Wärmeabnehmer» |
| Wärmepreis für den Haushalt | 0–13,3 Rp./kWh (Varianten) | offen | legt Säule Firma fest; Kundenperspektive empfiehlt ≤ 7 Rp./kWh |

### 3. Energiepreise
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Strom | 33,25 Rp./kWh (Total, IWB, H4, 2026) | Belegt | [ElCom](https://www.strompreis.elcom.admin.ch) (API-Abruf, `daten/roh/elcom/`) |
| Heizöl | 1,665 CHF/l (3'000 l, Anfang Nov. 2026) | Belegt | [weekend.at](https://www.weekend.at/chronik/heizoelpreise-fallen-gruende-marktuebersicht-und-kaufempfehlung); Preis schwankt stark |
| Heizwert Heizöl | 10 kWh/l | Annahme | Standardwert Heizöl EL |
| Gas Arbeitspreis | 11,57 Rp./kWh (Stufe M, inkl. MwSt.) | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| CO2-Abgabe Gas | 2,333 Rp./kWh (inkl. MwSt.) | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| Konzessionsabgabe Gas BS | 0,11 Rp./kWh | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| Gas Leistungspreis | 12,43 CHF/kW/Jahr, min. 194,58 CHF | Belegt | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife) |
| Tarifstufe M für das Referenzhaus | ≈ 35'000 kWh Gas | Abgeleitet | IWB-Beispiel EFH 20'000 kWh = Stufe M; Grenze der Stufen nicht publiziert |
| Gas-Anschlussleistung | 15 kW Referenz / 12 kW Durchschnitt | Annahme / Belegt | 12 kW aus IWB-Beispiel Typ II; 15 kW Annahme |

### 4. Heute verwendete Heizung
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Wärmepumpe Jahresarbeitszahl | 2,5 | Case | Case («Wärme ersetzt Wärmepumpe, JAZ 2,5») |
| Ölkessel Wirkungsgrad | 85 % | Annahme | älterer Kessel |
| Gaskessel Wirkungsgrad | 90 % | Annahme | |
| CO2 Heizöl | 2,65 kg/l | Annahme | gängiger Emissionsfaktor Heizöl EL |
| CO2 Erdgas | 0,198 kg/kWh | Annahme | gängiger Emissionsfaktor Erdgas |
| Wärme kostet heute | Öl 19,6 / Gas 15,6 / WP 13,3 Rp. pro kWh Wärme | Abgeleitet | aus den Zeilen oben |

### 5. Investitionen und Förderung beim Haushalt
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Neue Wärmepumpe in Basel | 31'500–63'000 CHF, gerechnet 45'000 | Belegt (Spanne) | [handwerker-kosten.ch](https://www.handwerker-kosten.ch/waermepumpe/basel/) |
| Förderung Wärmepumpe BS 2026 | 8'000 + 250 CHF/kWth (Luft/Wasser, ausserhalb Fernwärme), max. 40 %; Beispiel 8 kW = 10'500 | Belegt (nicht amtlich) | [ion-e.ch](https://www.ion-e.ch/de/waermepumpe-basel), [Stiebel Eltron](https://www.stiebel-eltron.ch/de/home/ratgeber/uebersicht/foerderung/basel-stadt.html); amtliche Broschüre 2026 war nicht abrufbar |
| Förderung halbiert im Fernwärmegebiet | ja | Belegt | [bs.ch](https://www.bs.ch/medienmitteilungen/2025-teilrevision-energieverordnung-mehr-foerderbeitraege-fuer-gesamtsanierungen-und-anpassung-beim-heizungsersatz) |
| Lebensdauer Wärmepumpe | 18 Jahre | Annahme | übliche 15–20 Jahre |
| Heizstab im Speicher (Backup ohne Gas) | 2'000 CHF einmalig | Annahme | grobe Schätzung, keine Offerte |
| Heizstab erlaubt? | als Notheizung | **offen** | Elektro-Widerstandsheizungen sind in der Schweiz eingeschränkt; beim AUE BS klären |
| Serverheizung gilt als erneuerbarer Heizungsersatz? | — | **offen** | beim AUE BS klären |
| Impulsprogramm Bund | 2025–2034, 200 Mio. CHF/Jahr, Elektroheizungen, Wärmeverteilung | Belegt | [admin.ch](https://www.admin.ch/de/newnsb/qGTPQ1ZqqKag), [BAFU](https://www.bafu.admin.ch/de/foerderungen-im-gebaeudebereich) |

### 6. Markt Basel-Stadt
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Ölfeuerungen | 1'677 (Juni 2026), alle Gebäudetypen | Belegt | [bs.ch, Open Data AUE](https://www.bs.ch/wsu/aue/abteilung-energie/meldung-fossilbefeuerte-heizungen) |
| Ölanteil Wohngebäude | 8 % BS, 25–40 % in den meisten Kantonen | Belegt | [BFS](https://www.bfs.admin.ch/bfs/de/home/statistiken/bau-wohnungswesen/gebaeude/energiebereich.html) |
| Gas-Liegenschaften | knapp 11'000 (2024) | Belegt | Presse über IWB, siehe [bz Basel](https://www.bzbasel.ch/basel/basel-stadt/netto-null-bis-2037-trotz-fernwaerme-ausbau-stilllegung-des-gasnetzes-wird-zum-mammutprojekt-ld.2531385) |
| Gasnetz stillgelegt | bis 2037, ab 2028 ≈ 1'000 Anschlüsse/Jahr | Belegt | [IWB](https://www.iwb.ch/klimadreh/ratgeber/heizung-ersetzen/gasstilllegung-basel-stadt), [bs.ch](https://www.bs.ch/medienmitteilungen/wsu/2023-die-waermeversorgung-basel-stadt-wird-bis-2037-erneuerbar) |
| Neue Öl-/Gasheizungen verboten | seit 2017 | Belegt | [BKB](https://www.bkb.ch/de/privatkunden/magazin/2024/heizsysteme-basel-stadt-verzicht-auf-gas-und-oel-bis-2037-lohnt-sich-auch-finanziell) |
| Gebiete ohne Fernwärme | 5,3 km² mit dezentraler Lösung vorgesehen (Fernwärme 12,2 km²) | Belegt + Abgeleitet | Geoportal BS, Teilrichtplan Energie (WFS `ms:EP_Energierichtplan_*`), Flächen eigene Berechnung, `dashboard/karte_fernwaerme.html` |

### 8. Nordwestschweiz (siehe KUNDE_NORDWESTSCHWEIZ.md)
| Annahme | Wert | Status | Quelle |
|---|---|---|---|
| Region | BS, BL, AG (BFS-Grossregion) | Belegt | BFS |
| Strom BL | 30,20 Rp./kWh (EBL, N-Basis, 2026; MwSt. nicht angegeben) | Belegt | [EBL Mitteilung 2026](https://www.ebl.ch/hubfs/EBL/_EBL%20Website/Preisbl%C3%A4tter%202026/Mitteilung%20zu%20den%20Tarif%C3%A4nderungen%202026.pdf), Kopie in `daten/roh/elcom/` |
| Strom AG | 30,15 Rp./kWh (AEW, H4, 2026, inkl. MwSt.) | Belegt | [AEW info August 2025](https://www.aew.ch/sites/default/files/2025-11/AEW_info_August_2025_Mitteilungen_zu_Tarifaenderungen_im_Jahr_2026_neu3.pdf) |
| Gas BL/AG | wie IWB 2026 | Annahme | für AG ohne Quelle |
| Öl- und Gas-Wohngebäude BL | 28,9 % / 30,7 % von 66'780 (2024) | Belegt | [Energiestatistik BL 2024](https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/daten-statistik/abteilung-statistik/publikationen-und-statistiken/energie/webartikel-vom-07-07-2026-energiestatistik-2024) |
| Öl- und Gas-Wohnungen AG | 135'574 / 58'620 von 348'656 (2024) | Belegt | [Statistisches Jahrbuch AG 2025](https://www.ag.ch/app/staag/statistisches_jahrbuch/chapters/09_bau.html) |
| Wetter | Basel 2025 für die ganze Region | Annahme | Aargau etwas kühler |

### 9. Was die Kundenperspektive nicht annimmt
- Gewinn und Preise von DigitalHeat: Säule Firma (anderer Chat)
- Rechenpreise, Aufträge und Sicherheit: Säule Pharma
- Hardwarekosten: nur als Begründung, warum der Haushalt nicht selbst kauft


<!-- Ende Quelldatei ANNAHMEN_KUNDE.md -->

<!-- Beginn Quelldatei NOTIZEN.md -->

## Notizen (Joël, 20.11.2026)

### Standorte mit unterschiedlichem Wärmebedarf
- Landwirtschaft, Maistrockner: Sommer
- Hotel mit Spa: ganzjährig
- Einfamilienhäuser: Winter

### Ideen zur Steuerung
- Rechenaufträge zwischen Standorten verschieben
- Rechenaufträge verlangsamen (drosseln statt nur pausieren)
- Klären: was wird dort berechnet?
- Das System steht nur zur Verfügung, wenn der Standort Wärme braucht

### Preisrecherche
- Was kostet Bildverarbeitung (z. B. pro 1'000 Bilder)?
- Was kostet eine GPU-Stunde (on-demand, spot)?
- Strom- und Gaspreise, veröffentlicht auf … (Quelle noch ergänzen)


<!-- Ende Quelldatei NOTIZEN.md -->

<!-- Beginn Quelldatei requirements.txt -->

## Vollständige Softwareabhängigkeiten

```text
anyio==4.16.0
certifi==2026.10.23
charset-normalizer==3.5.2
click==8.5.1
fastembed==0.9.1
filelock==4.2.12
flatbuffers==25.12.19
fsspec==2026.9.0
h11==0.16.0
hf-xet==1.8.0
httpcore==1.0.9
httpx==0.28.1
huggingface_hub==1.33.0
idna==3.20
loguru==0.7.3
mmh3==5.3.1
numpy==2.5.5
onnxruntime==1.32.0
packaging==26.3
pillow==13.0.0
protobuf==7.36.2
psutil==7.2.2
py_rust_stemmers==0.1.8
PyYAML==6.0.3
requests==2.34.2
tokenizers==0.23.3
tqdm==4.70.1
typing_extensions==4.16.0
urllib3==2.8.0
```


<!-- Ende Quelldatei requirements.txt -->

## Prüfung der zusätzlich referenzierten Dateien

Geprüft wurden die konkreten lokalen Dateinamen und Pfade in den acht Ausgangsdateien sowie die darin genannten Rohdatenverzeichnisse. Ein Verweis nur auf `live.py` wurde dem ausdrücklich ebenfalls genannten Pfad `src/scheduler/live.py` zugeordnet. Externe Webseiten sind Quellenlinks und keine fehlenden lokalen Projektdateien. Die folgende Prüfung betrifft die Existenz; sie bestätigt weder die inhaltliche Richtigkeit noch die Ausführbarkeit der Dateien.

### Ergebnis der lokalen Prüfung

**Keine der 15 zusätzlich konkret referenzierten lokalen Projektdateien fehlt im Projektordner.** Alle 15 gehören jedoch nicht zu den acht ausgewählten Ausgangsdateien. Für eine vollständige Weitergabe des Projekts sollten sie mitgegeben werden.

| Zusätzlich referenzierte Datei | Genannt in | Im Projektordner |
|---|---|---|
| `dashboard/daten.js` | ERGEBNISSE.md | vorhanden |
| `dashboard/karte_fernwaerme.html` | ANNAHMEN_KUNDE.md, KUNDENPERSPEKTIVE.md, KUNDENVIEW.md, KUNDE_NORDWESTSCHWEIZ.md | vorhanden |
| `dashboard/starten.sh` | ERGEBNISSE.md | vorhanden |
| `daten/ergebnisse/serverzahl.json` | ERGEBNISSE.md | vorhanden |
| `daten/ergebnisse/stunden_8_spot.csv` | ERGEBNISSE.md | vorhanden |
| `daten/ergebnisse/win_win_win.json` | KUNDENPERSPEKTIVE.md, KUNDENVIEW.md | vorhanden |
| `src/dashboard_daten.py` | ERGEBNISSE.md | vorhanden |
| `src/jobtypen.py` | ERGEBNISSE.md | vorhanden |
| `src/kunde/karte_fernwaerme.py` | KUNDENVIEW.md | vorhanden |
| `src/kunde/wirtschaftlichkeit.py` | ANNAHMEN_KUNDE.md, KUNDENPERSPEKTIVE.md, KUNDENVIEW.md | vorhanden |
| `src/referenzprofil.py` | ERGEBNISSE.md | vorhanden |
| `src/scheduler/annahmen.py` | ERGEBNISSE.md | vorhanden |
| `src/scheduler/jahr.py` | ANNAHMEN_KUNDE.md, ERGEBNISSE.md, KUNDENVIEW.md | vorhanden |
| `src/scheduler/kern.py` | ERGEBNISSE.md, KUNDENVIEW.md | vorhanden |
| `src/scheduler/live.py` | ERGEBNISSE.md | vorhanden |

Die Querverweise auf `KUNDENVIEW.md` und `KUNDE_NORDWESTSCHWEIZ.md` sind bereits durch die ausgewählten Ausgangsdateien abgedeckt. Der dokumentierte Interpreter `.venv/bin/python` ist ebenfalls vorhanden; er ist Teil der lokalen Laufzeitumgebung und keine zusätzliche fachliche Unterlage.

### Rohdaten und nur allgemein bezeichnete Dateien

Die Verzeichnisse `daten/roh/` und `daten/roh/elcom/` sind vorhanden. Der allgemeine Hinweis auf das offizielle Case-CSV lässt sich im Projektbestand der Datei `daten/roh/offiziell/open-meteo-47.56N7.55E247m.csv` zuordnen. Die inhaltliche Gleichheit mit Open-Meteo wurde hier nicht erneut geprüft.

Diese zusätzlichen Dateien liegen in den referenzierten Rohdatenverzeichnissen und gehören ebenfalls nicht zur ursprünglichen Auswahl:

- `daten/roh/agnews/test.parquet`
- `daten/roh/alibaba/pai_group_tag_table.csv`
- `daten/roh/alibaba/pai_group_tag_table.tar.gz`
- `daten/roh/alibaba/pai_job_table.csv`
- `daten/roh/alibaba/pai_job_table.tar.gz`
- `daten/roh/alibaba/pai_machine_spec.csv`
- `daten/roh/alibaba/pai_machine_spec.tar.gz`
- `daten/roh/alibaba/pai_sensor_table.csv`
- `daten/roh/alibaba/pai_sensor_table.tar.gz`
- `daten/roh/alibaba/pai_task_table.csv`
- `daten/roh/alibaba/pai_task_table.tar.gz`
- `daten/roh/elcom/ebl_tarifaenderungen_2026.pdf`
- `daten/roh/elcom/iwb_h4_2026.json`
- `daten/roh/geobs/BS_Hoheitsgrenzen_Gemeindegrenze.geojson`
- `daten/roh/geobs/EP_Energierichtplan_Eignungsgebiet.geojson`
- `daten/roh/geobs/EP_Energierichtplan_Fernwaerme.geojson`
- `daten/roh/geobs/EP_Energierichtplan_Verbunde.geojson`
- `daten/roh/mlperf/summary_results_v5.0.json`
- `daten/roh/mlperf/summary_results_v5.1.json`
- `daten/roh/mlperf/summary_results_v6.0.json`
- `daten/roh/offiziell/open-meteo-47.56N7.55E247m.csv`
- `daten/roh/openmeteo/basel_2025.csv`

### Verlinkte externe PDF Dateien

Die Ausgangsdateien verlinken drei externe PDF-Unterlagen. Die EBL-Unterlage liegt zusätzlich als lokale Kopie vor. Bei den beiden anderen wurde im aufgeführten lokalen Projektbestand keine erkennbare PDF-Kopie gefunden. Das bedeutet nicht, dass der Weblink ungültig ist; seine aktuelle Erreichbarkeit wurde nicht geprüft.

- [AEW Tarifänderungen 2026](https://www.aew.ch/sites/default/files/2025-11/AEW_info_August_2025_Mitteilungen_zu_Tarifaenderungen_im_Jahr_2026_neu3.pdf): Keine erkennbare lokale PDF-Kopie im Projektbestand gefunden.
- [Wärmepumpen Förderprogramm Aargau](https://www.ag.ch/media/kanton-aargau/bvu/energie/foerderungen/waermepumpen-foerderprogramm.pdf): Keine erkennbare lokale PDF-Kopie im Projektbestand gefunden. Die Ausgangsdatei bezeichnet die darin verwendeten Förderansätze als älteren Stand.
- [EBL Tarifänderungen 2026](https://www.ebl.ch/hubfs/EBL/_EBL%20Website/Preisbl%C3%A4tter%202026/Mitteilung%20zu%20den%20Tarif%C3%A4nderungen%202026.pdf): Lokale Kopie vorhanden: `daten/roh/elcom/ebl_tarifaenderungen_2026.pdf`.

### Inhaltlich noch offene Unterlagen

Unabhängig von der Dateiexistenz benennen die Ausgangstexte noch ausstehende Grundlagen: die amtliche Bestätigung der Förderbeiträge Basel-Stadt 2026, konkrete Förderbeträge Basel-Landschaft 2026, die Bestätigung Aargau 2026, die kantonale Beurteilung der Serverheizung und des Heizstabs, Gaspreise ausserhalb des IWB-Gebiets sowie die Bestätigung der Kostenübernahme und der verfügbaren Rechenaufträge durch die Säulen Firma und Pharma. Dafür wird in den acht Dateien kein eindeutiger zusätzlicher lokaler Dateipfad angegeben. Sie sind offene Nachweise und keine nachgewiesen gelöschten Projektdateien.
