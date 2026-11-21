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


def cloud_daten():
    """ML-Wärmeprognose, Strategievergleich, Pausieren vs. Abschalten und Service-ML für die Cloud-Ebene."""
    out = {}
    ml = ERG / "ml" / "zusammenfassung.json"
    if ml.exists():
        d = json.loads(ml.read_text())
        # Stichproben der Auswertung: je Zielstunde Ist-Bedarf, ML-Prognose und «wie gestern» (Persistenz)
        reihen = sorted(([s["target"][5:13], round(s["actual_kwh"], 2), round(s["ml_kwh"], 2),
                          round(s["persistence_kwh"], 2), s["horizon_hours"]] for s in d["forecast_samples"]))
        fm = d["forecast_metrics"]
        out["ml"] = {"mae_ml": round(fm["ml_mae_kwh"], 3), "mae_persistenz": round(fm["persistence_mae_kwh"], 3),
                     "horizont_h": fm["horizon_hours"], "modell": d["model"]["model"], "reihen": reihen,
                     "zeitraum": f'{d["period"]["start"][:10]} bis {d["period"]["end_exclusive"][:10]}'}
    sv = ERG / "strategievergleich" / "zusammenfassung.json"
    if sv.exists():
        d = json.loads(sv.read_text())
        out["strategien"] = [{"name": r["strategie"], "strom_kwh": round(r["gesamtstrom_kwh"])} for r in d["table"]]
        out["strategien_zeitraum"] = f'{d["period"]["start"][:10]} bis {d["period"]["end_exclusive"][:10]}'
    sb = json.loads((ERG / "serverbetrieb.json").read_text())["ergebnisse"]
    for name in ("pausieren", "abschalten"):
        r = next(r for r in sb if r["strategie"] == name and r["szenario"] == "spot"
                 and (r.get("leistungsprofil") or {}).get("leerlauf_watt") == 230)
        out[name] = {"strom_kwh": round(r["strom_kwh"]), "abgefuehrt_kwh": round(r["waerme_abgefuehrt_kwh"]),
                     "deckung": r["deckungsgrad"], "starts": r["serverstarts"]}
    svc = ERG / "service_ml" / "service_plan.json"  # erzeugt mit: python3 service_start.py --demo --case
    if svc.exists():
        d = json.loads(svc.read_text())
        out["service"] = {
            "synthetisch": True, "stand": d["servers"][0]["as_of"],
            "brier_modell": d["model"]["test_brier"], "brier_konstant": d["model"]["baseline_brier"],
            "server": [{"id": s["server_id"], "risiko_30d": round(s["risk_next_30_days_without_service"], 3),
                        "naechste_wartung": s["next_routine_date"], "intervall_tage": s["recommended_interval_days"],
                        "ungeplant_pro_jahr": round(s["selected"]["expected_unplanned"], 2),
                        "kosten_chf": round(s["selected"]["expected_total_cost_chf"])} for s in d["servers"]]}
    return out


def main():
    profil = profil_laden()
    f, _ = baue(N_HAEUSER, N_HAUS, "spot", "abgeben", profil, bad_profil(profil), N_BAD, leistung=LEISTUNG)
    s = {k: [] for k in ("zeit", "temp", "h_bed", "h_gen", "h_sp", "h_on", "h_lauf", "h_backup", "h_abg",
                         "h2_bed", "h2_gen", "h2_sp", "h2_on", "h2_lauf",
                         "b_bed", "b_gen", "b_sp", "b_on", "b_lauf", "mig", "flotte_lauf", "rest_on")}
    mig_vorher = 0
    for h in range(len(profil)):
        r = f.schritt(h)
        haus, haus2, bad = r["standorte"][0], r["standorte"][1], r["standorte"][-1]
        s["zeit"].append(r["zeit"][5:13])
        s["temp"].append(haus["temp_c"])
        for p, z in (("h", haus), ("h2", haus2), ("b", bad)):
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
        # die übrigen 18 Häuser: eingeschaltete Server im Mittel (für die leuchtenden Nachbarkeller)
        rest = r["standorte"][2:-1]
        s["rest_on"].append(round(sum(z["server_eingeschaltet"] for z in rest) / len(rest), 2))

    # Day-ahead-Zusage der Flotte mit Bad (aus flotte_abschalten.json) und Prognose-Temperatur pro Tag
    from src.scheduler.zusage import prognose_profil
    fl = json.loads((ERG / "flotte_abschalten.json").read_text())
    z = fl["zusage_spot"]["Sportbad 50 (nach Nachfrage)"]
    prog = prognose_profil(profil)
    t_prog = {}
    for p in prog:
        t_prog.setdefault(p["zeit"][:10], []).append(p["temp"])
    zusage = {"sicherheitsfaktor": z["sicherheitsfaktor"], "zusagbar": z["jahr"]["zusagbarer_anteil"],
              "fehltage_auswertung": z["fehltage_auswertung"], "methode": z["methode"],
              "tag": [t["tag"][5:] for t in z["tage"]],
              "prognose_temp": [round(sum(t_prog[t["tag"]]) / len(t_prog[t["tag"]]), 1) for t in z["tage"]],
              "zugesagt": [round(z["sicherheitsfaktor"] * t["prognose_server_h"]) if t["mit_zusage"] else None
                           for t in z["tage"]],
              "geliefert": [round(t["geliefert_server_h"]) for t in z["tage"]]}

    daten = {
        "erzeugt": "python3 src/dashboard3d_daten.py",
        "modell": {"haeuser": N_HAEUSER, "server_haus": N_HAUS, "server_bad": N_BAD,
                   "leerlauf_watt": LEISTUNG.leerlauf_watt, "standby_watt": LEISTUNG.standby_watt,
                   "start_minuten": LEISTUNG.start_minuten, "szenario": "spot",
                   "speicher_haus_kwh": A.wert("speicher_kwh"), "speicher_bad_kwh": A.wert("bad_speicher_kwh"),
                   "bad_betrieb": A.wert("bad_betrieb_2025")},
        "kennzahlen": kennzahlen(),
        "cloud": cloud_daten(),
        "zusage": zusage,
        "waerme": {  # Raummodell für Anzeige und Thermostat-Simulation
            "ua_kw_k": round(10 / 25.6, 4),
            "ua_quelle": "Case-Formel: 10 kW bei 20 °C innen und −5,6 °C aussen (src/referenzprofil.py)",
            "zeitkonstante_h": 40,
            "zeitkonstante_quelle": "Schätzung: Einfamilienhaus mittelschwerer Bauweise, 30–60 h",
            "waermerueckgewinnung": A.wert("waermerueckgewinnung"),
            "heizoel_kwh_l": 10.0, "kessel_wirkungsgrad": 0.9, "co2_kg_l": 2.65,
            "oel_quelle": "Heizöl EL ≈ 10 kWh/l (Heizwert), Kessel 90 %, 2,65 kg CO₂/l (BAFU-Emissionsfaktor)",
        },
        "stunden": s,
    }
    ziel = ROOT / "dashboard" / "3d" / "daten3d.js"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text("window.D3 = " + json.dumps(daten, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"{ziel.relative_to(ROOT)}: {ziel.stat().st_size / 1e6:.2f} MB, {len(s['zeit'])} Stunden, "
          f"{sum(s['mig'])} Migrationen")


if __name__ == "__main__":
    main()
