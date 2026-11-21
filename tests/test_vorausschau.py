import unittest

from src.scheduler.jahr import Haus
from src.scheduler.router import Flotte


class VorausschauTest(unittest.TestCase):
    def test_wartet_auf_vollen_waermeslot_und_beendet_job(self):
        profil = [{"zeit": f"2025-01-01T{h:02}:00", "heizung": bedarf, "ww": 0, "temp": 10}
                  for h, bedarf in enumerate((0, 0, 0.8))]
        for prognose in (None, profil):
            with self.subTest(vorausschau=prognose is not None):
                haus = Haus(1, profil=profil, speicher_kwh=0.2, mit_ankuenften=False)
                flotte = Flotte([haus], "alibaba", nachfrage_server=0, prognose=prognose)
                job = flotte.pool._neuer_job("A", 0, 24)
                flotte.schritt(0)
                if prognose is None:
                    self.assertGreater(job.gelaufen_kwh, 0)
                else:
                    self.assertEqual(job.gelaufen_kwh, 0)
                flotte.schritt(1)
                flotte.schritt(2)
                self.assertEqual(flotte.pool.z["fertig"], 1)
                self.assertEqual(flotte.pool.z["pausierte_fortsetzungen"], int(prognose is None))

                mit_prognose = int(prognose is not None)
                self.assertEqual(flotte.pool.z["verschobene_jobs"], mit_prognose)
                self.assertEqual(flotte.pool.z["verschobene_jobstunden"], 2 * mit_prognose)
                self.assertEqual(flotte.pool.z["verschobene_jobs_gestartet"], mit_prognose)
                self.assertEqual(flotte.pool.z["wartezeit_bis_start_h"], 2 * mit_prognose)
                self.assertEqual(flotte.pool.z["verschobene_jobs_fertig"], mit_prognose)
                self.assertEqual(flotte.pool.z["verschobene_jobs_am_stueck_fertig"], mit_prognose)

    def test_pflichtjob_wird_auch_bei_kuenftigem_waermebedarf_gerechnet(self):
        profil = [{"zeit": f"2025-01-01T{h:02}:00", "heizung": bedarf, "ww": 0, "temp": 10}
                  for h, bedarf in enumerate((0, 0.8))]
        haus = Haus(1, profil=profil, speicher_kwh=0, mit_ankuenften=False)
        flotte = Flotte([haus], "alibaba", nachfrage_server=0, prognose=profil)
        job = flotte.pool._neuer_job("A", 0, 1)
        flotte.schritt(0)
        self.assertIn(job.id, flotte.zuteilung)
        self.assertEqual(flotte.pool.z["fertig"], 1)
