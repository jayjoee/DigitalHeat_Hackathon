# TODOS

Verschoben im CEO-Review vom 21.11.2026 (Plan: `docs/designs/waerme-router-basel.md`, Modus «Umfang kürzen»). Jeder Punkt wurde einzeln mit «Verschieben» entschieden.

- **Verschiedene Häuser in der Flotte** (D3). Vorerst 20 × Referenzhaus. Später: Heizlast 6–14 kW, Warmwasser 8–20 kWh/Tag, Speicher 35–100 kWh, je mit Quelle. Grund: Häuser mit demselben Wetter gleichen sich kaum aus. Der Nutzen der Verteilung liegt bei den rund 9'000 Sommer-Server-h pro Haus (Szenario «Nur Jobs mit Frist»: abgeben → −8'403 CHF/J).
- **Zweite Senke: Hotel mit Spa** (D4). Vorerst nur Hallenbad, Vergleich 0/1 Senke. Offen: Wärmebedarf mit Quelle, 60-°C-Warmwasser.
- **Kalibrierung der Day-ahead-Zusage auf 2024** (D5). Vorerst Rückfall: Januar–Juni 2025 kalibrieren, Juli–Dezember auswerten, Saisonverschiebung unter Grenzen nennen. Später: Previous Runs 2024, Ist-Profil 2024, Flottenlauf 2024.
- **Wärmeverkauf an Senken** (D6). Vorerst kein Preis-Parameter; im Pitch nur als Ausblick («Ein Bad könnte sogar für die Wärme zahlen»).

Offen nach Ansatz A, Router, Dashboard und Live-Demo (21.11.2026):
- Wärmebedarf des Sportbads mit Messwert ersetzen (Anfrage Sportamt, Immobilien Basel-Stadt oder IWB; `daten/HALLENBAD.md`).
- Übertragung von Checkpoint und Modell über das Netz bei der Migration messen.
