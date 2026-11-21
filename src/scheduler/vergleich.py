"""Reproduzierbarer Jahresvergleich: python3 -m src.scheduler.vergleich."""
import argparse
import json
from pathlib import Path

from src import referenzprofil as R

from src.scheduler import annahmen as A
from src.scheduler.flotte import bad_profil, baue, serverzahl_haus
from src.scheduler.jahr import profil_laden
from src.scheduler.zusage import prognose_laden


def rollierende_prognose(profil):
    """48-h-Temperaturen sind selbst am Ende des 24-h-Horizonts verfügbar.

    Der gleitende Temperaturmittelwert nutzt nur Werte bis zur Zielstunde.
    Damit braucht die Heizgrenze keine später veröffentlichten Prognosen.
    """
    archiv = prognose_laden()
    if archiv["time"] != [p["zeit"] for p in profil]:
        raise ValueError("Zeitachsen von Prognose und Profil stimmen nicht überein")
    temps = archiv["temperature_2m_previous_day2"]
    prognose = []
    for i, (p, t) in enumerate(zip(profil, temps)):
        fenster = temps[max(0, i - 23):i + 1]
        heizt = sum(fenster) / len(fenster) < R.HEIZGRENZE_C
        heizung = max(0.0, R.AUSLEGUNG_KW * (R.INNEN_C - t) / R.KONSTANTE) if heizt else 0.0
        prognose.append({"zeit": p["zeit"], "heizung": heizung, "ww": p["ww"]})
    return prognose


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--haeuser", type=int, default=A.wert("flotte_haeuser"))
    parser.add_argument("--ohne-bad", action="store_true")
    args = parser.parse_args()
    if args.haeuser < 1:
        parser.error("--haeuser muss mindestens 1 sein")
    profil = profil_laden()
    bad = None if args.ohne_bad else bad_profil(profil)
    n_haus = serverzahl_haus(profil)
    flotte_datei = Path(__file__).resolve().parents[2] / "daten" / "ergebnisse" / "flotte.json"
    n_bad = 0 if bad is None else json.loads(flotte_datei.read_text())["server_bad_nach_nachfrage"]
    regel = "abgeben"
    ergebnisse = {}
    for name, prognose in (("stundenregel", None), ("vorausschau", rollierende_prognose(profil))):
        flotte, _ = baue(args.haeuser, n_haus, "alibaba", regel, profil, bad, n_bad, prognose=prognose)
        bilanz = flotte.simuliere(monatlich=False)
        zaehler = flotte.pool.z
        gestartet = zaehler["verschobene_jobs_gestartet"]
        ergebnisse[name] = {
            "waerme_genutzt_kwh": round(sum(s.z["genutzt"] for s in flotte.st), 2),
            "waerme_abgefuehrt_kwh": round(sum(s.z["abgefuehrt"] for s in flotte.st), 2),
            "jobs_mit_frist": zaehler["mit_frist"],
            "jobs_fertig": zaehler["fertig"],
            "jobs_verpasst": zaehler["verpasst"],
            "arbeit_verpasst_kwh": round(zaehler["verpasst_kwh"], 2),
            "arbeit_abgegeben_kwh": round(zaehler["abgegeben_kwh"], 2),
            "offene_jobs_am_jahresende": len(flotte.pool.q),
            "pausierte_fortsetzungen": zaehler["pausierte_fortsetzungen"],
            "migrationen": bilanz["migrationen"],
            "verschobene_jobs": zaehler["verschobene_jobs"],
            "verschobene_jobstunden": zaehler["verschobene_jobstunden"],
            "verschobene_jobs_gestartet": gestartet,
            "mittlere_wartezeit_bis_start_h": round(zaehler["wartezeit_bis_start_h"] / gestartet, 2)
            if gestartet else None,
            "verschobene_jobs_fertig": zaehler["verschobene_jobs_fertig"],
            "verschobene_jobs_am_stueck_fertig": zaehler["verschobene_jobs_am_stueck_fertig"],
        }
    print(json.dumps({"haeuser": args.haeuser, "server_pro_haus": n_haus, "server_bad": n_bad,
                      "regel_ueberschuss": regel, **ergebnisse}, indent=2))


if __name__ == "__main__":
    main()
