# Vergleich der Auftragswarteschlangen

SYNTHETISCHER FUNKTIONSVERGLEICH – KEIN GEMESSENER EFFIZIENZNACHWEIS

Alle Varianten prüfen dieselben Ressourcen- und Sicherheitsbedingungen und erhalten dieselben Aufträge. Geändert werden Reihenfolge, Platzierung und die simulierte Standby-Steuerung.

| Strategie | Fertig | Frist verpasst | Serverstrom kWh | Strom CHF | Mittlere Wartezeit s |
|---|---:|---:|---:|---:|---:|
| fifo_spread | 48 | 0 | 6.189 | 2.058 | 0.0 |
| priority_pack | 48 | 0 | 6.189 | 2.058 | 0.0 |
| priority_pack_sleep | 48 | 0 | 2.323 | 0.772 | 211.0 |

Identische fertiggestellte Aufträge: True

## Annahmen

- **workload:** 48 frei erzeugte Metadatenaufträge, keine Pharma-Nachfrage
- **nodes:** 3 simulierte Hosts mit je 8 L4, 24 GB je GPU, 192 GB Host-RAM, 16 CPU-Kernen; Ressourcenwerte sind Teamannahmen
- **energy:** 1 kW aktiv, 230 W Leerlauf, 10 W Standby, 5 Minuten Start aus bestehendem Serverbetriebsmodell; nicht an L4 gemessen
- **power_curve:** Leerlauf + (Aktiv−Leerlauf) × Ressourcenbelegung; lineare Testannahme, keine gemessene Kennlinie
- **sleep:** Nach 300 Sekunden ohne passende Arbeit; eigener Testwert. Aufwachen wird ausschliesslich im Simulator bestätigt.
- **runtime:** Bekannte Laufzeiten und perfekte Einhaltung im Simulator; reale Überschreitungen können Backfill-Zusagen verschieben
- **price:** 0,3325 CHF/kWh als Projektwert; nur Stromkosten, keine Unternehmensrendite
- **exclusions:** Steuerungsenergie, Datenübertragung, Speicherung, reale Wärmeabnahme, Pumpen, Ersatzheizung und Wartungsausfälle fehlen.

Die Ergebnisse dürfen nicht mit der Jahresbilanz oder dem früheren Halbjahresvergleich gleichgesetzt werden. Forschungsgrundlage und übernommene Verfahren stehen in docs/technik/RESSOURCEN_SCHEDULER.md im Projekt.
