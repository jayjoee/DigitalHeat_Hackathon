"""Firmenrechnung (src/firma.py): Reproduzierbarkeit, Halbjahres-Konvention, Absatz und Eingabeprüfung."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import firma  # noqa: E402
from src.scheduler import annahmen as A  # noqa: E402


class FirmaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basis = firma.rechne_firma()

    def test_basis_entspricht_gespeicherter_firma_json(self):
        gold = json.loads((ROOT / "daten/ergebnisse/firma.json").read_text())
        self.assertEqual(self.basis["kennzahlen"], gold["kennzahlen"])
        self.assertEqual(self.basis["jahre"], gold["jahre"])

    def test_eine_generation_mit_halbem_ersten_jahr(self):
        jahre = self.basis["jahre"]
        self.assertEqual([j["jahr"] for j in jahre], list(range(2027, 2037)))
        self.assertTrue(all(j["capex"] == 0 for j in jahre if j["jahr"] > 2031))
        # Die Häuser von 2031 laufen bis Mitte 2036: kein Haus mehr am Jahresende, aber noch Umsatz
        self.assertEqual(jahre[-1]["haeuser"], 0)
        self.assertGreater(jahre[-1]["umsatz"], 0)
        self.assertEqual(self.basis["kennzahlen"]["endwert_restbuchwert"], 0)

    def test_fixkosten_steigen_mit_teuerung(self):
        W, plan = firma.W, firma.W("ausbau_neue_haeuser")
        for n, j in enumerate(self.basis["jahre"][:len(plan)]):
            # Halbjahres-Konvention: neue Häuser zählen im Einbaujahr halb
            haeuser_mittel = sum(plan[:n]) + plan[n] / 2
            fte = W("fte_grundteam") + W("fte_pro_haus") * haeuser_mittel
            ohne = fte * W("fte_kosten_chf") + W("iso27001_chf") + W("buero_it_chf") + W("vertrieb_chf")
            self.assertAlmostEqual(j["fixkosten_firma"], ohne * (1 + A.wert("kostensteigerung")) ** n, delta=1)

    def test_weniger_absatz_senkt_irr(self):
        irrs = [firma.rechne_firma(absatz_anteil=x)["kennzahlen"]["projekt_irr"] for x in (1.0, 0.9, 0.8, 0.72, 0.6)]
        self.assertEqual(irrs, sorted(irrs, reverse=True))
        self.assertLess(irrs[-1], 0)

    def test_absatz_ausserhalb_der_grenzen_bricht_ab(self):
        fest = A.wert("anteil_fest_gebucht")
        for x in (fest - 0.01, 1.01):
            with self.assertRaises(ValueError):
                firma.rechne_firma(absatz_anteil=x)
        firma.rechne_firma(absatz_anteil=fest)

    def test_szenario_veraendert_annahmen_nicht(self):
        vorher = dict(firma.F)
        firma.rechne_firma(absatz_anteil=0.8, foerderung_erhalten=False)
        self.assertEqual(firma.F, vorher)

    def test_zehn_jahre_mit_ersatz_hat_endwert(self):
        zehn = firma.rechne_firma(nur_erste_generation=False)["kennzahlen"]
        self.assertGreater(zehn["endwert_restbuchwert"], 0)
        self.assertGreater(zehn["projekt_irr_mit_endwert"], zehn["projekt_irr"])


class KostenDhAbsatzTests(unittest.TestCase):
    def test_nullpunkt_mit_festem_roche_anteil(self):
        k = json.loads((ROOT / "daten/ergebnisse/kosten_dh.json").read_text())
        s, haus = k["sensitivitaeten"], k["referenzhaus"]
        self.assertGreaterEqual(s["verkaufte_stunden_nullpunkt"], A.wert("anteil_fest_gebucht"))
        # 60 % verkauft heisst: nur Roche, die übrigen Stunden unverkauft
        self.assertEqual(s["verkaufte_stunden"]["60%"], haus["ergebnis_rest_unverkauft_chf"])
        self.assertEqual(s["verkaufte_stunden"]["100%"], haus["ergebnis_chf"])


if __name__ == "__main__":
    unittest.main()
