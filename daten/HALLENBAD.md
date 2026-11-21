# Sommersenke Bad Basel: Wärmebedarf (Recherche, Stand 21.11.2026)

## Kurzfazit

- **Ein Hallenbad taugt in Basel nicht als Sommersenke.** Das einzige öffentliche Hallenbad, das Rialto, ist jedes Jahr rund zwei Monate zu, 2026 vom 28.6. bis 31.8. [Q1]. Das Hallenbad Eglisee ist eine Traglufthalle und nur von Mitte September bzw. Oktober bis Anfang Mai in Betrieb [Q3, Q4].
- **Empfohlene Senke: das Sportbad im Gartenbad St. Jakob.** Es hat ein beheiztes 50-m-Wettkampfbecken mit 8 Bahnen [Q5, Q6, Q7] und ist von Ende April bis Anfang Oktober offen: 26.4.–5.10.2025 und 25.4.–4.10.2026 [Q2, Q5]. Laut badi-info (Sekundärquelle) wird es heute mit Fernwärme beheizt [Q6].
- **Rechtlicher Rückenwind:** Freibäder dürfen gemäss MuKEn nur mit erneuerbarer Energie oder mit «nicht anders nutzbarer Abwärme» beheizt werden. Der VHF-Leitfaden nennt Freibäder ausdrücklich als interessante Abnehmer, weil sie Abwärme «vor allem ausserhalb der Heizperiode, also im Sommer» beziehen [Q8, S. 20 und Kap. 2.3.1].

## Empfohlene Zahlen (Sportbad St. Jakob, nur Wettkampfbecken)

| Grösse | Wert | Belastbarkeit |
|---|---|---|
| Wasserfläche | **1 050 m²** (50 m × 21 m) | Annahme. Belegt sind nur 50 m und 8 Bahnen [Q7]. Die Breite von 21 m entspricht dem Standard für 8 Bahnen à 2,5 m plus 2 × 0,5 m Rand und ist nicht belegt. |
| Kennwert Wärme | 430–480 kWh/m² pro Saison (Mitte Mai bis Mitte September, ca. 120 Betriebstage, 24 °C, ohne Abdeckung, inkl. Frischwassererwärmung) | Belegt [Q8, S. 156] |
| Jahresbedarf | **650 000 kWh/a** (Bandbreite 480 000–810 000) | Schätzung, ±30 % |
| Mittlere Leistung Juni–August | **ca. 130 kW** (Bandbreite 100–170 kW) | Schätzung |

### Herleitung Jahresbedarf

1. Gemäss VHF-Leitfaden gilt für eine 120-Tage-Saison: 1 050 m² × 455 kWh/m² (Mitte der Spanne) = **478 MWh**. Das ist die Untergrenze, weil das Sportbad länger offen ist.
2. Das Sportbad hat 163 Betriebstage (26.4.–5.10.2025) statt 123 (15.5.–14.9.).
   - **Methode A** (Bedarf gleichmässig pro Tag): 478 × 163/123 = **633 MWh**.
   - **Methode B** (Tagesbedarf ∝ max(0, 24 °C − Tagesmittel Luft), Basel 2025 aus `daten/referenzprofil_2025.csv`): Faktor 1,69, also **808 MWh**. Diese Methode überschätzt die Randmonate, weil sie die Sonneneinstrahlung ignoriert.
3. Empfehlung: rund **650 MWh/a**, nahe Methode A.
4. Nicht enthalten sind:
   - das ebenfalls beheizte 50-m-Lehrschwimmbecken [Q6], dessen Fläche unbekannt ist (Potenzial nach oben);
   - die Duschen, deren Warmwasser von den Besuchern abhängt;
   - der Unterschied zwischen Nutz- und Endenergie.

Plausibilitätscheck mit dem KEA-BW Energiespiegel 2022 (Baden-Württemberg, Tab. 5) [Q9]: Für ganze Freibäder mit 1 000–2 000 m² Beckenfläche liegt der Median bei 155 kWh/m²a, bei über 2 000 m² bei 167 kWh/m²a. Das ist tiefer als der VHF-Wert, weil dort auch unbeheizte Becken mitzählen. Der VHF-Wert für ein dauerbeheiztes Becken bleibt deshalb die passendere Grundlage.

### Monatsanteile (Schätzung)

Die Anteile sind das Mittel aus Methode A (Anteil Betriebstage) und Methode B (Anteil Temperaturdifferenz), gerechnet mit den Temperaturen Basel 2025.

| Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | 0 % | 0 % | 4,0 % | 23,8 % | 13,8 % | 16,2 % | 15,6 % | 21,8 % | 4,8 % | 0 % | 0 % |

Summe 100 %. Hinweise zur Verteilung:

- Juni 2025 war mit 21,2 °C wärmer als Juli (19,8 °C), deshalb fällt der Juni-Anteil tiefer aus.
- Laut VHF wird «ein Grossteil der Wärmeenergie für die Erstaufheizung im Frühling benötigt» [Q8, S. 155]. April und Mai sind daher eher unterschätzt.
- Hochsommer: Juni–August zusammen ergeben 45,6 % von 650 MWh = 296 MWh. Verteilt auf 92 Tage (2 208 h) sind das **134 kW** im Mittel, mit Bandbreite (478 bzw. 808 MWh) 99–167 kW.
- Das Becken braucht auch nachts Wärme (Verluste über die Wasserfläche). Bei Hitzewellen mit Sonne sinkt der Bedarf stark. Die Senke ist also im Juli zwar vorhanden, aber kleiner als im Mai oder September.

Reproduzierbar: Die Tagesmittel der Spalte `temp_c` aus `daten/referenzprofil_2025.csv` ergeben die Monatsgewichte. Das Python-Snippet ist in der Recherche gelaufen, eine Code-Datei wurde nicht angelegt.

## Schliessungszeiten Basler Bäder

| Bad | Betrieb | Quelle |
|---|---|---|
| Hallenbad Rialto | September bis Ende Juni, Sommerpause 28.6.–31.8.2026 | Q1, Q10 |
| Hallenbad Eglisee (Traglufthalle über dem 50-m-Becken) | Aufbau Mitte September, Abbau Anfang Mai; 2025 offen ab 6.10. | Q3, Q4, Q2 |
| Sportbad St. Jakob (beheizt) | 26.4.–5.10.2025 und 25.4.–4.10.2026 | Q2, Q5 |
| Gartenbad Eglisee, Familienbad St. Jakob | 2025: 17.5. bzw. 10.5. bis 14.9. | Q2, Q11 |
| Gartenbad Bachgraben | 10.5.–28.9.2025 | Q2, Q11 |

Das Hallenbad Eglisee wird im Winter mit Abwärme aus der Kälteanlage der Kunsteisbahn beheizt [Q4]. Dieser Abwärme-Konkurrent besetzt also schon die Wintersenke am Eglisee.

## Temperaturniveau

- Hallenbad: Beckenwasser «meist über 28 °C», Schwimmhalle 30 °C, Warmbecken 32 °C [Q8, S. 34 und Kap. 3].
- Freibad: 22–26 °C. Der VHF-Leitfaden hält sogar Kunsteisbahn-Abwärme mit **höchstens 34 °C** Kondensator-Austritt für die direkte Freibad-Beheizung für geeignet [Q8, S. 34].
- **Folgerung:** Ein Vorlauf von 45–60 °C reicht für die Beckenwassererwärmung über einen Wärmetauscher direkt aus, ohne Wärmepumpe.
- Duschen-Warmwasser: Wegen Legionellen ist üblicherweise ein Speicher mit ≥ 60 °C nötig (SIA 385/1; die Norm wurde nicht im Original geprüft). Bei 45–55 °C Vorlauf deckt die Abwärme deshalb nur die Vorwärmung, der Rest braucht Nachheizung.

## Vergleich Rialto (falls eine Winter- bzw. Ganzjahressenke gesucht wird)

- Planungskennwerte nach der Gesamtsanierung 2024: Heizwärmebedarf 62 kWh/m², Warmwasser 250 kWh/m², EBF 6 644 m², Wärme aus Fernwärme [Q10, S. 4].
- Das ergibt 312 × 6 644 = **ca. 2,07 GWh/a**. Die Zahl ist ein Planungswert und gilt für das ganze Gebäude inkl. 28 Wohnungen und Restaurant, nicht für das Bad allein. Im Juli und August fällt der Badanteil weg (Sommerpause).

## Quellen

- Q1: Erziehungsdepartement Basel-Stadt, Medienmitteilung «Vorhang auf für die Summer-Kunschti Margarethen / Sommerpause im Hallenbad Rialto», 2.6.2026. https://www.bs.ch/medienmitteilungen/ed/2026-vorhang-auf-fuer-die-summer-kunschti-margarethen-sommerpause-im-hallenbad-rialto
- Q2: Erziehungsdepartement Basel-Stadt, Medienmitteilung «Saison-Eröffnung und -Abschluss Bäder und Kunsteisbahnen», 3.10.2025. https://www.bs.ch/medienmitteilungen/ed/2025-saison-eroeffnung-und-abschluss-baeder-und-kunsteisbahnen
- Q3: SRF News, «Hallenbad Eglisee: Basel hat endlich ein 50-Meter-Hallenbad», 29.10.2017. https://www.srf.ch/news/hallenbad-eglisee-basel-hat-endlich-ein-50-meter-hallenbad
- Q4: Basel-Stadt, Bauprojekt «Traglufthalle Gartenbad Eglisee, Neubau». https://www.bs.ch/schwerpunkte/bauprojekte/seiten/hochbauprojekte/traglufthalle-gartenbad-eglisee-neubau (Projektdoku: https://www.hochbauamt.bs.ch/dam/jcr:2bda5f3b-e4b5-47b6-8a64-1f8255bf2a79/RZ2_BAU_PD_Traglufthalle_Eglisee_web.pdf). Die Angaben zur Beheizung stammen aus der Suchzusammenfassung; das PDF selbst wurde nicht geöffnet.
- Q5: Sportamt Basel-Stadt, Seite «Gartenbad St. Jakob», abgerufen 21.11.2026. https://www.bs.ch/themen/kultur-sport-und-freizeit/baeder-kunsteisbahnen-sportanlagen-und-raeume/gartenbaeder/gartenbad-st-jakob
- Q6: badi-info.ch, «Gartenbad St. Jakob» (Sekundärquelle: Fernwärme, min. 24 °C, 50-m-Lehrschwimmbecken beheizt), abgerufen 21.11.2026. https://www.badi-info.ch/bs/st-jakob.html
- Q7: Swiss Aquatics, Reglement 3.1.7 «Homologierte Wettkampfbecken», V2023, Liste: «Basel Freibad St. Jakob FB A 50m 8R autom-2». https://www.swiss-aquatics.ch/wp-content/uploads/2023/12/3.1.7_d_Homologierte-Wettkampfbecken_V2023.pdf
- Q8: Verband Hallen- und Freibäder (VHF) mit EnergieSchweiz/BFE, «Leitfaden Energie in Hallen- und Freibädern», Version 1, 2018. Benutzte Stellen: S. 20 (MuKEn, Wärmeanteil), Kap. 2.3.1 (Freibäder als Sommer-Abwärmesenke), S. 34 (Temperaturen Kunsteisbahn-Abwärme), S. 151 (Hallenbad 43–52 kWh/m³ Kubatur), S. 155–156 (Freibad 430–480 kWh/m² pro Saison). https://pubdb.bfe.admin.ch/de/publication/download/9728
- Q9: KEA Klimaschutz- und Energieagentur Baden-Württemberg, «Energiespiegel 2022», Tabelle 5 «Deskriptive Statistik Wärme – Bäder». https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Wissensportal/Benchmarkbericht/KEA_BW_Energiespiegel_2022_neu.pdf
- Q10: Basel-Stadt, Städtebau & Architektur, Projektdokumentation «Rialto, Gesamtsanierung» (Übergabe Sommer 2024), S. 4 «Umwelt- und Energiekennwerte». https://media.bs.ch/original_file/061db24301b94c6df1b4b19f30d1b108a7a767fe/s-und-a-projektdoku-hochbau-rialto-lowres.pdf
- Q11: Jugend, Familie und Sport Basel-Stadt, «JFS in Zahlen 2024», S. 21. Die Gartenbäder hatten 2024 zusammen 429 742 Eintritte. https://media.bs.ch/original_file/51293fd3a60e672fd09f6b6499a6e76cf307cb67/sport-jfs-in-zahlen-2024.pdf

## Offene Punkte

- Wasserfläche und gemessener Fernwärmebezug des Sportbads: beim Sportamt bzw. bei Immobilien Basel-Stadt oder IWB anfragen. Ein Messwert würde die Schätzung ersetzen.
