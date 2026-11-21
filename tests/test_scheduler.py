"""Tests für Scheduler, Day-ahead-Zusage und Wärme-Router.

Aufruf: python3 -m unittest discover -s tests -v      (ohne Zusatzpakete)

Regressionstest 2: `Haus.schritt` nach der Aufteilung Zeile für Zeile wie vorher (tests/referenz_haus8.json,
erzeugt vor dem Umbau mit Stand f81d801/e90eaf0). Regressionstest 1: Flotte aus genau dem Referenzhaus =
`jahr.simuliere(8)`, inklusive +40'411 CHF/J bei 60 % fest gebucht ohne Fehlmenge.
"""
import hashlib
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler import zusage as Z  # noqa: E402
from src.scheduler.jahr import Haus, profil_laden, simuliere  # noqa: E402
from src.scheduler.kern import Job, Lage, entscheide  # noqa: E402
from src.scheduler.router import Flotte  # noqa: E402
from src.scheduler.serverbetrieb import HausMitServerbetrieb, Leistungsprofil  # noqa: E402
from src.wirtschaft import rechne  # noqa: E402

PROFIL = profil_laden()
KOMBIS = [(sz, r) for sz in ("spot", "alibaba") for r in ("rechnen", "abgeben")]


def kunstprofil(bedarfe):
    """Kleines Profil mit vorgegebenem Wärmebedarf pro Stunde (für Router-Einzeltests)."""
    return [{"zeit": f"2025-01-01T{h % 24:02d}:00", "temp": 0.0, "heizung": b, "ww": 0.0, "sonne": 0.0}
            for h, b in enumerate(bedarfe)]


def standort(name, n, bedarfe, speicher=0.0):
    return Haus(n, "alibaba", "rechnen", kunstprofil(bedarfe), speicher_kwh=speicher, name=name,
                mit_ankuenften=False)


def bad(name, n, bedarfe):
    return Haus(n, "alibaba", "rechnen", kunstprofil(bedarfe), speicher_kwh=0.0, name=name, typ="bad",
                mit_ankuenften=False)


def leere_flotte(standorte):
    """Flotte ohne Ankünfte (nachfrage_server=0); Jobs werden von Hand in den Pool gelegt."""
    return Flotte(standorte, "alibaba", "rechnen", nachfrage_server=0, migration_min=6.0)


def job(f, jid, rest, frist=math.inf, standort=None, typ="A", gelaufen=0.0, ankunft=0):
    j = Job(jid, typ, ankunft, frist, rest, typ == "A", gelaufen)
    j.standort = standort
    f.pool.q.append(j)
    f.pool.z["jobs"] += 1
    if not math.isinf(frist):
        f.pool.z["mit_frist"] += 1
    return j


class Regression(unittest.TestCase):
    def test_2_haus_schritt_zeilengleich(self):
        gold = json.loads((ROOT / "tests" / "referenz_haus8.json").read_text())
        for sz, r in KOMBIS:
            with self.subTest(szenario=sz, regel=r):
                h = Haus(8, sz, r, PROFIL)
                zeilen = [h.schritt(i) for i in range(len(PROFIL))]
                sha = hashlib.sha256(json.dumps(zeilen, sort_keys=True).encode()).hexdigest()
                self.assertEqual(sha, gold[f"{sz}_{r}"]["zeilen_sha256"])
                self.assertEqual(h.bilanz(), gold[f"{sz}_{r}"]["bilanz"])

    def test_1_flotte_mit_einem_haus_gleich_einzelhaus(self):
        for sz, r in KOMBIS:
            with self.subTest(szenario=sz, regel=r):
                f = Flotte([Haus(8, sz, r, PROFIL, mit_ankuenften=False)], sz, r)
                f.simuliere(monatlich=False)
                self.assertEqual(f.bilanz_wie_haus(), simuliere(8, sz, r, profil=PROFIL))
                self.assertEqual(f.pool.z["migrationen"], 0)

    def test_1_geld_referenz(self):
        f = Flotte([Haus(8, "spot", "rechnen", PROFIL, mit_ankuenften=False)], "spot", "rechnen")
        f.simuliere(monatlich=False)
        b = f.bilanz(anteil_fest_gebucht=0.60, fehlmenge_server_h=0.0)
        self.assertEqual(b["dh_ergebnis_pro_jahr_chf"], 40411)
        self.assertEqual(f.bilanz_wie_haus()["dh_ergebnis_pro_jahr_chf"], 40411)

    def test_gleiche_haeuser_spot_wie_einzelhaus(self):
        # Unbegrenzt A: jedes Haus der Flotte rechnet so viel wie allein (Rest: andere Ziehung der B-Ankünfte).
        einzel = simuliere(8, "spot", "rechnen", profil=PROFIL)
        f = Flotte([Haus(8, "spot", "rechnen", PROFIL, name=f"H{i}", mit_ankuenften=False) for i in range(3)],
                   "spot", "rechnen")
        f.simuliere(monatlich=False)
        for s in f.st:
            self.assertAlmostEqual(s.z["strom"] / einzel["server_h"], 1.0, delta=0.001)

    def test_serverregel_referenzhaus_8(self):
        from src.scheduler.flotte import serverzahl_haus
        self.assertEqual(serverzahl_haus(PROFIL), 8)


class Router(unittest.TestCase):
    def test_bindung_r3_10_angefangener_job_bleibt(self):
        # A hat mehr freies Wärmeziel und entscheidet zuerst, darf den Job von B aber nicht nehmen,
        # solange B ihn selbst nehmen kann.
        f = leere_flotte([standort("A", 1, [5.0]), standort("B", 1, [0.4])])
        j = job(f, 1, 3.0, standort=1, gelaufen=1.0)
        r = f.schritt(0)
        self.assertEqual(r["standorte"][0]["strom_kwh"], 0.0)
        self.assertAlmostEqual(r["standorte"][1]["strom_kwh"], 0.5)
        self.assertEqual(j.standort, 1)
        self.assertEqual(f.pool.z["migrationen"], 0)

    def test_migration_wenn_eigener_standort_voll(self):
        # B braucht keine Wärme mehr (Speicher 0, Bedarf 0): der Job wandert zu A, Migrationsenergie kommt dazu.
        f = leere_flotte([standort("A", 1, [5.0]), standort("B", 1, [0.0])])
        j = job(f, 1, 3.0, standort=1, gelaufen=1.0)
        r = f.schritt(0)
        self.assertAlmostEqual(r["standorte"][0]["strom_kwh"], 1.0)
        self.assertEqual(j.standort, 0)
        self.assertEqual(f.pool.z["migrationen"], 1)
        self.assertAlmostEqual(j.rest_kwh, 3.0 - 1.0 + 0.1)  # 6 min × 1 kW = 0,1 kWh Migration
        self.assertAlmostEqual(f.mig_st[0], 0.1)

    def test_typ_b_wandert_nie(self):
        f = leere_flotte([standort("A", 1, [5.0]), standort("B", 1, [0.0])])
        j = job(f, 1, 0.5, frist=10, standort=1, typ="B", gelaufen=0.1)
        f.schritt(0)
        self.assertEqual(f.pool.z["migrationen"], 0)
        self.assertEqual(j.standort, 1)

    def test_pflicht_ohne_freien_server_r3_11_einmal_gezaehlt(self):
        # 3 Pflichtjobs, die genau jetzt laufen müssen, aber nur 2 Server in der Flotte:
        # 2 laufen, 1 verpasst die Frist und wird genau einmal gezählt.
        f = leere_flotte([standort("A", 1, [5.0, 5.0]), standort("B", 1, [5.0, 5.0])])
        for i in range(3):
            job(f, i, 1.0, frist=1)
        r = f.schritt(0)
        self.assertAlmostEqual(r["server_laufend"], 2.0)
        self.assertEqual(f.pool.z["fertig"], 2)
        self.assertEqual(f.pool.z["verpasst"], 1)
        self.assertEqual(f.pool.q, [])

    def test_pflicht_geht_an_groesstes_waermeziel(self):
        f = leere_flotte([standort("A", 1, [0.2]), standort("B", 1, [5.0])])
        job(f, 1, 1.0, frist=1)
        r = f.schritt(0)
        self.assertAlmostEqual(r["standorte"][1]["strom_kwh"], 1.0)
        self.assertEqual(r["standorte"][0]["strom_kwh"], 0.0)

    def test_abgeben_bei_ueberschuss_genau_einmal(self):
        f = Flotte([standort("A", 1, [0.0, 0.0]), standort("B", 1, [0.0, 0.0])], "alibaba", "abgeben",
                   nachfrage_server=0)
        job(f, 1, 1.0, frist=1)
        f.schritt(0)
        self.assertEqual(f.pool.z["abgegeben"], 1)
        self.assertEqual(f.pool.z["verpasst"], 0)

    def test_vorrang_haus_vor_bad(self):
        # Das Bad hat viel mehr freies Wärmeziel, trotzdem rechnet zuerst das Haus; das Bad bekommt nur den Rest.
        f = leere_flotte([standort("Haus", 1, [0.4], speicher=0.0), bad("Bad", 2, [100.0])])
        job(f, 1, 3.0)
        job(f, 2, 3.0)
        r = f.schritt(0)
        self.assertAlmostEqual(r["standorte"][0]["strom_kwh"], 0.5)
        self.assertAlmostEqual(r["standorte"][1]["strom_kwh"], 1.0)

    def test_haus_holt_job_vom_bad_zurueck(self):
        f = leere_flotte([standort("Haus", 1, [5.0]), bad("Bad", 1, [100.0])])
        j = job(f, 1, 3.0, standort=1, gelaufen=1.0)
        r = f.schritt(0)
        self.assertAlmostEqual(r["standorte"][0]["strom_kwh"], 1.0)
        self.assertEqual(j.standort, 0)
        self.assertEqual(f.pool.z["migrationen"], 1)

    def test_pflicht_zuerst_ans_haus(self):
        f = leere_flotte([bad("Bad", 1, [100.0]), standort("Haus", 1, [0.4])])
        job(f, 1, 1.0, frist=1)
        r = f.schritt(0)
        self.assertAlmostEqual(r["standorte"][1]["strom_kwh"], 1.0)  # Pflicht läuft ganz, am Haus
        self.assertEqual(r["standorte"][0]["strom_kwh"], 0.0)

    def test_invarianten_flotte_mit_senke(self):
        # Kurzer echter Lauf: 3 Häuser + Senke, Alibaba. Kein Job läuft doppelt, Energie stimmt, Zähler gehen auf.
        from src.scheduler.flotte import bad_profil, baue
        f, _ = baue(3, 8, "alibaba", "abgeben", PROFIL, bad_profil(PROFIL), 10)
        start = next(i for i, p in enumerate(PROFIL) if p["zeit"].startswith("2025-06-01"))
        for h in range(start, start + 24 * 14):
            r = f.schritt(h)
            for s, z in zip(f.st, r["standorte"]):
                self.assertLessEqual(z["strom_kwh"], s.n * A.wert("server_kw") + 1e-6)
        pz = f.pool.z
        offen_mit_frist = sum(1 for j in f.pool.q if not math.isinf(j.frist_h))
        self.assertEqual(pz["mit_frist"], pz["fertig"] + pz["verpasst"] + pz["abgegeben"] + offen_mit_frist)
        strom = sum(s.z["strom"] for s in f.st)
        self.assertAlmostEqual(strom, pz["server_h_a"] + pz["server_h_b"], places=6)


class Zusage(unittest.TestCase):
    def test_kein_wert_nach_dem_entscheid_r3_17(self):
        verzug = A.wert("prognose_verzug_h")
        tag1 = 0
        for p in PROFIL:
            if p["zeit"] < "2025-01-02":
                continue
            feld, lauf = Z.quelle_pro_stunde(p["zeit"])
            entscheid = Z.entscheid_utc(p["zeit"][:10])
            self.assertLessEqual(lauf.timestamp() + verzug * 3600, entscheid.timestamp(), p["zeit"])
            tag1 += feld.endswith("day1")
        self.assertGreater(tag1, 0)  # die frühen Stunden nutzen den genaueren Vortag

    def test_entscheid_in_utc_sommer_und_winter_r3_16(self):
        self.assertEqual(Z.entscheid_utc("2025-01-16").hour, 11)
        self.assertEqual(Z.entscheid_utc("2025-07-16").hour, 10)

    def test_vortag_genauer_als_zwei_tage(self):
        h = Z.prognose_laden()
        ist = [p["temp"] for p in PROFIL]
        mae = {k: sum(abs(a - b) for a, b in zip(h[k], ist)) / len(ist)
               for k in ("temperature_2m_previous_day1", "temperature_2m_previous_day2")}
        self.assertLess(mae["temperature_2m_previous_day1"], mae["temperature_2m_previous_day2"])

    def test_kalibrierung_und_auswertung(self):
        haus = Haus(8, "spot", "rechnen", PROFIL)
        r, haus = Z.rechne_zusage(haus, Z.prognose_profil(PROFIL))
        self.assertLessEqual(r["fehltage_kalibrierung"], A.wert("zusage_max_fehltage") + 1e-12)
        self.assertGreater(r["sicherheitsfaktor"], 0.5)
        self.assertGreaterEqual(r["jahr"]["zusagbarer_anteil"], r["jahr"]["anteil_fest_gebucht"])
        # der echte Lauf wird durch die Trockenläufe nicht verändert
        self.assertEqual(haus.bilanz(), simuliere(8, "spot", "rechnen", profil=PROFIL))

    def test_auswerten_rechnet_fehlmenge(self):
        tage = [{"tag": "2025-01-02", "prognose_server_h": 10.0, "geliefert_server_h": 5.0, "mit_zusage": True},
                {"tag": "2025-01-03", "prognose_server_h": 10.0, "geliefert_server_h": 15.0, "mit_zusage": True}]
        r = Z.auswerten(tage, 1.0, nachfrage=1.0)
        self.assertEqual(r["fehlmenge_server_h"], 5.0)
        self.assertEqual(r["fest_gebucht_server_h"], 15.0)


class Wirtschaft(unittest.TestCase):
    def test_fehlmenge_null_aendert_nichts(self):
        self.assertEqual(rechne(8, 36290, 29027)["ergebnis_pro_jahr_chf"], 40412)
        self.assertEqual(rechne(8, 36290, 29027, 0.0), rechne(8, 36290, 29027))

    def test_fehlmenge_kostet_gutschrift(self):
        a = rechne(8, 36290, 29027)
        b = rechne(8, 36290, 29027, fehlmenge_server_h=100)
        erwartet = 100 * 8 * A.wert("vertragspreis_chf_karte_h") * A.wert("sla_gutschrift_anteil")
        self.assertEqual(b["jahre"][0]["fehlmenge"], round(erwartet))
        self.assertLess(b["ergebnis_pro_jahr_chf"], a["ergebnis_pro_jahr_chf"])

    def test_zustandsstrom_erhoeht_kosten_ohne_mehrerloes(self):
        basis = rechne(8, 36290, 29027)
        mit_leerlauf = rechne(8, 36290, 29027, strom_kwh=37290)
        self.assertEqual(basis["jahre"][0]["erloes"], mit_leerlauf["jahre"][0]["erloes"])
        self.assertEqual(mit_leerlauf["jahre"][0]["strom"] - basis["jahre"][0]["strom"], 333)


class Serverbetrieb(unittest.TestCase):
    def test_flotte_bad_startet_bei_waermebedarf_und_geht_in_standby(self):
        leistung = Leistungsprofil(230, start_minuten=5)
        haus = HausMitServerbetrieb(1, "spot", kunstprofil([0.8, 0, 0]), leistung,
                                    abschalten=True, bei_ueberschuss="abgeben", speicher_kwh=0,
                                    mit_ankuenften=False)
        bad = HausMitServerbetrieb(2, "spot", kunstprofil([0, 1.6, 0]), leistung,
                                   abschalten=True, bei_ueberschuss="abgeben", speicher_kwh=0,
                                   mit_ankuenften=False, typ="bad")
        f = Flotte([haus, bad], "spot", "abgeben", nachfrage_server=0)
        f.schritt(0)
        self.assertEqual(bad.eingeschaltet, 0)
        self.assertAlmostEqual(bad.z["standbystrom"], 0.02)
        kopie = f.kopie()
        r = kopie.schritt(1)
        self.assertEqual(bad.eingeschaltet, 0)
        self.assertEqual(r["standorte"][1]["server_eingeschaltet"], 2)
        self.assertEqual(r["standorte"][1]["server_starts"], 2)
        self.assertLess(r["standorte"][1]["server_laufend"], 2.0)
        self.assertEqual(f.schritt(1), r)
        r = f.schritt(2)
        self.assertEqual(r["standorte"][1]["server_standby"], 2)
        self.assertAlmostEqual(r["standorte"][1]["strom_kwh"], 0.02)
        self.assertAlmostEqual(r["standorte"][1]["waerme_kwh"], 0)
        b = f.bilanz()
        self.assertGreater(b["strom_kwh"], b["server_h_verkauft"])
        self.assertAlmostEqual(bad.z["strom"], sum(bad.z[k] for k in (
            "rechenstrom", "leerlaufstrom", "standbystrom", "startstrom")))

    def test_flotte_haus_hat_vorrang_vor_bad_beim_start(self):
        profil = kunstprofil([0.8])
        leistung = Leistungsprofil(230)
        standorte = [HausMitServerbetrieb(1, "alibaba", profil, leistung,
                                          abschalten=True, bei_ueberschuss="abgeben", speicher_kwh=0,
                                          mit_ankuenften=False, typ=typ) for typ in ("haus", "bad")]
        f = Flotte(standorte, "alibaba", "abgeben", nachfrage_server=0)
        job(f, 1, 0.5, frist=1, typ="B")
        f.schritt(0)
        self.assertEqual(standorte[0].z["serverstarts"], 1)
        self.assertEqual(standorte[1].z["serverstarts"], 0)
        self.assertEqual(f.pool.z["fertig"], 1)

    def test_flotte_gibt_dringenden_job_bei_vollem_speicher_ab(self):
        haus = HausMitServerbetrieb(1, "alibaba", kunstprofil([0]), Leistungsprofil(230),
                                    abschalten=True, bei_ueberschuss="abgeben", mit_ankuenften=False)
        haus.s = haus.smax
        f = Flotte([haus], "alibaba", "abgeben", nachfrage_server=0)
        job(f, 1, 0.5, frist=1, typ="B")
        f.schritt(0)
        self.assertEqual(haus.z["serverstarts"], 0)
        self.assertEqual(f.pool.z["abgegeben"], 1)
        self.assertEqual(f.pool.z["verpasst"], 0)

    def test_start_nachlauf_standby_und_waerme(self):
        haus = HausMitServerbetrieb(1, "spot", kunstprofil([0.8, 0.0, 0.0]),
                                    Leistungsprofil(230, start_minuten=15), abschalten=True,
                                    speicher_kwh=0, mit_ankuenften=False)
        start, leerlauf, standby = (haus.schritt(h) for h in range(3))
        self.assertAlmostEqual(start["server_laufend"], 0.75)
        self.assertAlmostEqual(start["strom_kwh"], 1.0)
        self.assertAlmostEqual(start["genutzt_kwh"], 0.8)
        self.assertAlmostEqual(leerlauf["strom_kwh"], 0.23)
        self.assertAlmostEqual(leerlauf["abgefuehrt_kwh"], 0.184)
        self.assertAlmostEqual(standby["strom_kwh"], 0.01)
        self.assertEqual(standby["waerme_kwh"], 0)
        self.assertEqual(haus.z["serverstarts"], 1)

    def test_nicht_unterbrechbarer_job_passt_nur_auf_einen_server(self):
        lage = Lage(0, 1, 0, 0, 2, server_kapazitaeten_kwh=(0.4, 0.4))
        pflicht = Job(0, "B", 0, 1, 0.7, False)
        ergebnis = entscheide(lage, [pflicht])
        self.assertEqual(ergebnis.laeufe, [])
        self.assertEqual(ergebnis.server_belegt_kwh, (0, 0))

    def test_pflichtjob_weckt_server_auch_bei_vollem_speicher(self):
        haus = HausMitServerbetrieb(2, "alibaba", kunstprofil([0.0]), Leistungsprofil(230),
                                    abschalten=True, mit_ankuenften=False)
        haus.s = haus.smax
        haus.plan = {0: ["B"]}
        haus.schritt(0)
        self.assertEqual(haus.z["serverstarts"], 1)
        self.assertEqual(haus.z["fertig"], 1)
        self.assertEqual(haus.z["verpasst"], 0)

    def test_pflichtjob_weckt_server_vor_der_naechsten_stunde(self):
        haus = HausMitServerbetrieb(1, "alibaba", kunstprofil([0.0, 0.0]),
                                    Leistungsprofil(230, start_minuten=59), abschalten=True,
                                    mit_ankuenften=False)
        haus.s = haus.smax
        haus.plan = {0: ["B"]}
        self.assertEqual(haus.schritt(0)["server_laufend"], 0)
        self.assertEqual(haus.z["serverstarts"], 1)
        haus.schritt(1)
        self.assertEqual(haus.z["fertig"], 1)
        self.assertEqual(haus.z["verpasst"], 0)


if __name__ == "__main__":
    unittest.main()
