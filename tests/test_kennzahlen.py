"""Kernzahlen in den Dokumenten müssen zu daten/ergebnisse/kosten_dh.json passen.

Ändert sich eine Annahme, erzeugt `python3 start/alles_neu_rechnen.py` die Zahlen neu. Dieser Test zeigt dann,
in welchem Dokument eine Zahl noch nachgeführt werden muss.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATEN = json.loads((ROOT / "daten" / "ergebnisse" / "kosten_dh.json").read_text(encoding="utf-8"))
HAUSHALT = json.loads((ROOT / "daten" / "ergebnisse" / "haushalt.json").read_text(encoding="utf-8"))

DOKS = {name: (ROOT / pfad).read_text(encoding="utf-8") for name, pfad in {
    "README": "README.md",
    "PITCH": "docs/PITCH.md",
    "KOSTEN_DH": "docs/wirtschaft/KOSTEN_DH.md",
    "ERGEBNISSE": "docs/ergebnisse/ERGEBNISSE.md",
    "PILOTPLAN": "docs/wirtschaft/PILOTPLAN.md",
    "HAUSBESITZER": "docs/kunden/HAUSBESITZER.md",
    "EINFACH": "docs/ergebnisse/RESULTATE_EINFACH.md",
}.items()}


def chf(x, auf=100):
    """Schweizer Schreibweise, gerundet: 34970 → 35'000 (auf Tausend) bzw. 27548 → 27'500 (auf Hundert)."""
    return f"{int(round(x / auf) * auf):,}".replace(",", "'")


def prozent(x, stellen=0):
    return f"{x * 100:.{stellen}f}".replace(".", ",") + " %"


def preis(x):
    return f"{x:.2f}".replace(".", ",") + " CHF"


class Kennzahlen(unittest.TestCase):
    def pruefe(self, text, in_doks):
        for name in in_doks:
            with self.subTest(zahl=text, dokument=name):
                self.assertIn(text, DOKS[name], f"«{text}» fehlt in {name} oder ist veraltet")

    def test_ergebnis_referenzhaus(self):
        self.pruefe(chf(DATEN["referenzhaus"]["ergebnis_chf"], 1000), ["README", "PITCH", "KOSTEN_DH", "ERGEBNISSE", "EINFACH"])

    def test_verkaufte_stunden_nullpunkt(self):
        self.pruefe(prozent(DATEN["pilot_schwellen"]["verkaufte_stunden_min"]),
                    ["README", "PITCH", "KOSTEN_DH", "ERGEBNISSE", "PILOTPLAN", "EINFACH"])

    def test_roche_preis_wenn_rest_spot(self):
        self.pruefe(preis(DATEN["pilot_schwellen"]["roche_preis_min_rest_spot_chf_karte_h"]),
                    ["PITCH", "KOSTEN_DH", "ERGEBNISSE", "PILOTPLAN"])

    def test_mittleres_nachfrageszenario(self):
        n = DATEN["nachfrage_szenarien"]
        self.pruefe(chf(n["winterkunde_sommer_unverkauft"]), ["PITCH", "KOSTEN_DH", "ERGEBNISSE", "PILOTPLAN", "EINFACH"])
        self.pruefe(prozent(n["anteil_stunden_heizsaison"]), ["PITCH", "KOSTEN_DH", "ERGEBNISSE", "PILOTPLAN"])
        self.pruefe(chf(n["nur_roche"]).lstrip("-"), ["KOSTEN_DH", "ERGEBNISSE"])

    def test_pilotschwellen(self):
        s = DATEN["pilot_schwellen"]
        self.pruefe(chf(s["serverpreis_max_chf"]), ["PITCH", "KOSTEN_DH", "PILOTPLAN"])
        self.pruefe(chf(s["pilot_investition_2_server_chf"]), ["PITCH", "KOSTEN_DH", "PILOTPLAN"])
        self.pruefe(prozent(s["anteil_roche_kapazitaet"], 2), ["PITCH", "KOSTEN_DH", "PILOTPLAN"])

    def test_ersparnis_haushalt(self):
        for haus in ("referenzhaus", "efh"):
            for art in ("oel", "gas", "waermepumpe"):
                self.pruefe(chf(HAUSHALT["realistisch"][haus]["spart_chf"][art], 1), ["HAUSBESITZER"])
                self.pruefe(chf(HAUSHALT["idealmodell"][haus]["spart_chf"][art], 1), ["HAUSBESITZER"])
        for rp, werte in HAUSHALT["waermeabo_efh"].items():
            if rp in ("0", "3", "7", "10"):
                for art in ("oel", "gas", "waermepumpe"):
                    self.pruefe(chf(werte[art], 1), ["HAUSBESITZER"])


if __name__ == "__main__":
    unittest.main()
