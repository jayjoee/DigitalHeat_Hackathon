"""Docking-Auftrag: Bibliothek, Dateien, Einbindung in live.py; echtes Docking nur, wenn Vina installiert ist."""
import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DOCK = ROOT / "daten" / "docking"


class Bibliothek(unittest.TestCase):
    def test_jedes_molekuel_hat_eine_vorbereitete_datei(self):
        with (DOCK / "molekuele.csv").open(encoding="utf-8") as f:
            namen = [z["name"] for z in csv.DictReader(f)]
        self.assertEqual(len(namen), 28)
        self.assertEqual(len(set(namen)), 28)
        for n in namen:
            with self.subTest(molekuel=n):
                self.assertTrue((DOCK / "liganden" / f"{n}.pdbqt").read_text().startswith("REMARK"))
        self.assertTrue((DOCK / "1iep_receptor.pdbqt").exists())

    def test_live_kennt_den_docking_auftrag(self):
        from src.scheduler.live import JOBS
        skript, einheit, _, _, _ = JOBS["docking"]
        self.assertTrue((ROOT / skript).exists())
        self.assertEqual(einheit, "Moleküle")


@unittest.skipUnless(importlib.util.find_spec("vina"), "AutoDock Vina nicht installiert")
class EchtesDocking(unittest.TestCase):
    def test_koffein_docken_mit_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(ROOT / "src/jobs/docking_job.py"), "--arbeitsordner", d,
                                "--anzahl", "1", "--erschoepfend", "2"], capture_output=True, text=True, timeout=300)
            self.assertEqual(r.returncode, 0, r.stderr)
            stand = json.loads((Path(d) / "stand.json").read_text())
            self.assertEqual(stand["naechster"], 1)
            e = stand["ergebnisse"][0]
            self.assertEqual(e["name"], "Koffein")
            self.assertLess(e["energie_kcal_mol"], -3)


if __name__ == "__main__":
    unittest.main()
