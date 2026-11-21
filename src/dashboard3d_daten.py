"""Stundendaten für das 3D-Dashboard (dashboard/3d/).

Rechnet die Flotte aus 20 Referenzhäusern und dem Sportbad St. Jakob (50 Server) mit bedarfsgerechtem
Abschalten (230 W Leerlauf, 10 W Standby, 5 min Start), Szenario «Genug Aufträge», ein Jahr lang
mit demselben Router wie src/scheduler/flotte.py. Gespeichert werden Haus 01 und das Bad pro Stunde,
dazu die Migrationen der Flotte. Kennzahlen kommen aus den bestehenden Ergebnisdateien.

    python3 src/dashboard3d_daten.py      # → dashboard/3d/daten3d.js (≈ 30 s)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scheduler.flotte import baue, bad_profil  # noqa: E402
from src.scheduler.jahr import profil_laden  # noqa: E402
from src.scheduler.serverbetrieb import Leistungsprofil  # noqa: E402
from src.scheduler import annahmen as A  # noqa: E402

N_HAEUSER, N_HAUS, N_BAD = 20, 8, 50
LEISTUNG = Leistungsprofil(230, 10, 5)
ERG = ROOT / "daten" / "ergebnisse"


def kennzahlen():
    case = next(r for r in json.loads((ERG / "serverzahl.json").read_text())["ergebnisse"]
                if r["server_pro_haus"] == 8 and r["szenario"] == "spot" and r["regel_ueberschuss"] == "rechnen")
    sb = json.loads((ERG / "serverbetrieb.json").read_text())["ergebnisse"]
    ab = next(r for r in sb if r["strategie"] == "abschalten" and r["szenario"] == "spot"
              and (r.get("leistungsprofil") or {}).get("leerlauf_watt") == 230)
    fl = json.loads((ERG / "flotte_abschalten.json").read_text())["ergebnisse"]
    flotte = {f"{r['szenario']}|{r['variante']}": {
        "ergebnis_chf": r["dh_ergebnis_pro_jahr_chf"], "abgegeben_server_h": round(r["abgegeben_server_h"]),
        "migrationen": r["migrationen"], "strom_kwh": round(r["strom_kwh"])} for r in fl}
    return {
        "case": {  # Case-Regel (Idealmodell, 0 W Leerlauf)
            "server_pro_haus": case["server_pro_haus"], "deckung": case["deckungsgrad"],
            "abgefuehrt_kwh": case["waerme_abgefuehrt_kwh"], "auslastung": case["auslastung"],
            "verpasst": case["verpasste_fristen_anteil"],
            "break_even_chf_server_h": case["break_even_chf_pro_server_h"],
        },
        "abschalten": {  # Betriebsmodell der Szene
            "deckung": ab["deckungsgrad"], "auslastung": ab["auslastung"], "strom_kwh": ab["strom_kwh"],
            "abgefuehrt_kwh": ab["waerme_abgefuehrt_kwh"], "serverstarts": ab["serverstarts"],
        },
        "flotte": flotte,
        "vertragspreis_chf_server_h": round(A.wert("vertragspreis_chf_karte_h") * A.wert("karten_pro_server"), 2),
    }


def main():
    profil = profil_laden()
    f, _ = baue(N_HAEUSER, N_HAUS, "spot", "abgeben", profil, bad_profil(profil), N_BAD, leistung=LEISTUNG)
    s = {k: [] for k in ("zeit", "temp", "h_bed", "h_gen", "h_sp", "h_on", "h_lauf", "h_backup", "h_abg",
                         "b_bed", "b_gen", "b_sp", "b_on", "b_lauf", "mig", "flotte_lauf")}
    mig_vorher = 0
    for h in range(len(profil)):
        r = f.schritt(h)
        haus, bad = r["standorte"][0], r["standorte"][-1]
        s["zeit"].append(r["zeit"][5:13])
        s["temp"].append(haus["temp_c"])
        for p, z in (("h", haus), ("b", bad)):
            s[f"{p}_bed"].append(round(z["bedarf_kwh"], 2))
            s[f"{p}_gen"].append(round(z["genutzt_kwh"], 2))
            s[f"{p}_sp"].append(round(z["speicher_kwh"], 1))
            s[f"{p}_on"].append(z["server_eingeschaltet"])
            s[f"{p}_lauf"].append(round(z["server_laufend"], 2))
        s["h_backup"].append(round(haus["backup_kwh"], 2))
        s["h_abg"].append(round(haus["abgefuehrt_kwh"], 2))
        s["mig"].append(f.pool.z["migrationen"] - mig_vorher)
        mig_vorher = f.pool.z["migrationen"]
        s["flotte_lauf"].append(round(r["server_laufend"], 1))

    daten = {
        "erzeugt": "python3 src/dashboard3d_daten.py",
        "modell": {"haeuser": N_HAEUSER, "server_haus": N_HAUS, "server_bad": N_BAD,
                   "leerlauf_watt": LEISTUNG.leerlauf_watt, "standby_watt": LEISTUNG.standby_watt,
                   "start_minuten": LEISTUNG.start_minuten, "szenario": "spot",
                   "speicher_haus_kwh": A.wert("speicher_kwh"), "speicher_bad_kwh": A.wert("bad_speicher_kwh"),
                   "bad_betrieb": A.wert("bad_betrieb_2025")},
        "kennzahlen": kennzahlen(),
        "stunden": s,
    }
    ziel = ROOT / "dashboard" / "3d" / "daten3d.js"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text("window.D3 = " + json.dumps(daten, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"{ziel.relative_to(ROOT)}: {ziel.stat().st_size / 1e6:.2f} MB, {len(s['zeit'])} Stunden, "
          f"{sum(s['mig'])} Migrationen")


if __name__ == "__main__":
    main()
