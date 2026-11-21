"""Deterministischer Nachtbatch-Vergleich: python3 -m src.scheduler.engpass."""
import json

from src.scheduler.jahr import Haus
from src.scheduler.router import Flotte


def profil(bedarfe):
    return [{"zeit": f"2025-01-01T{h:02}:00", "heizung": bedarf, "ww": 0, "temp": 10}
            for h, bedarf in enumerate(bedarfe)]


def lauf(bedarf, prognose, anzahl, frist):
    haus = Haus(2, profil=profil(bedarf), speicher_kwh=0.2, mit_ankuenften=False)
    flotte = Flotte([haus], "alibaba", nachfrage_server=0,
                    prognose=None if prognose is None else profil(prognose))
    for _ in range(anzahl):
        flotte.pool._neuer_job("A", 0, frist)
        flotte.pool.z["mit_frist"] += 1
    starts = {}
    for h in range(len(bedarf)):
        flotte.schritt(h)
        for job_id in flotte.zuteilung:
            starts.setdefault(job_id, h)
    return starts, {
        "jobs_fertig": flotte.pool.z["fertig"],
        "jobs_verpasst": flotte.pool.z["verpasst"],
        "fortsetzungen_nach_pause": flotte.pool.z["pausierte_fortsetzungen"],
        "waerme_genutzt_kwh": round(haus.z["genutzt"], 3),
        "waerme_abgefuehrt_kwh": round(haus.z["abgefuehrt"], 3),
        "startstunden_ab_batchbeginn": [starts.get(job_id) for job_id in range(anzahl)],
    }


def main():
    # Sechs gleichzeitige Standardjobs, ein kompakter Speicher und ein knappes Wärmefenster.
    anzahl, frist = 6, 8
    bedarf = [0, 0, 0, 1.6, 1.6, 0.05, 0.05, 0.05]
    basis_starts, basis = lauf(bedarf, None, anzahl, frist)
    ergebnisse = {"stundenregel": basis}
    for name, vorhersage in (
        ("vorausschau_genau", bedarf),
        ("vorausschau_zwei_stunden_zu_spaet", [0, 0, 0, 0, 0, 1.6, 1.6, 0.05]),
    ):
        starts, ergebnis = lauf(bedarf, vorhersage, anzahl, frist)
        ergebnis["startdifferenz_zur_stundenregel_h"] = [
            starts[j] - basis_starts[j] if j in starts and j in basis_starts else None
            for j in range(anzahl)
        ]
        ergebnisse[name] = ergebnis
    print(json.dumps({"server": 2, "jobs": anzahl, "frist_h": frist,
                      "bedarf_kwh_pro_stunde": bedarf, **ergebnisse}, indent=2))


if __name__ == "__main__":
    main()
