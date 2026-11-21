"""Bereitet alle Zahlen fürs Dashboard auf → dashboard/daten.js (window.DATEN = …).

Rechnet jede Kombination aus Serverzahl (1–13), Nachfrage (spot, alibaba) und Regel
(rechnen, abgeben) mit derselben Jahressimulation wie die Bilanz und speichert:
Jahreskennzahlen, Monatswerte und die Stundenwerte von zwei Beispieltagen.

Jeder Lauf enthält zusätzlich `abschalten`: dieselbe Kombination mit bedarfsgerechtem Abschalten
(Leistungsprofil unten, src/scheduler/serverbetrieb.py). Die Wärme-Kennzahlen des Case kommen aus
dem Idealmodell, die Wirtschaftlichkeit im Dashboard rechnet mit den Abschaltwerten (KOSTEN_DH.md).

Aufruf: python3 src/dashboard_daten.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.jahr import Haus, profil_laden  # noqa: E402
from src.scheduler.serverbetrieb import HausMitServerbetrieb, Leistungsprofil  # noqa: E402

ROOT = A.ROOT
# Übergangstag: Speicher läuft mittags voll, der 8. Server pausiert 7 h und läuft abends wieder an
TAGE = {"januar": "2025-01-15", "uebergang": "2025-03-07", "juli": "2025-07-15"}
# Wie KOSTEN_DH.md, PITCH.md und daten/ergebnisse/serverbetrieb.json: 230 W Leerlauf, 10 W Standby, 5 min Start
LEISTUNG = Leistungsprofil(230, 10, 5)


def abschalten_daten(n, szenario, regel, profil):
    """Jahreswerte mit bedarfsgerechtem Abschalten: Grundlage der Wirtschaftlichkeit im Dashboard."""
    haus = HausMitServerbetrieb(n, szenario, profil, LEISTUNG, abschalten=True, bei_ueberschuss=regel)
    for h in range(len(profil)):
        haus.schritt(h)
    z = haus.z
    return {"server_h": round(z["rechenstrom"] / A.wert("server_kw"), 1), "strom_kwh": round(z["strom"], 1),
            "genutzt_kwh": round(z["genutzt"], 1), "deckungsgrad": round(z["genutzt"] / z["bedarf"], 4),
            "abgefuehrt_kwh": round(z["abgefuehrt"], 1), "jobs_frist_verpasst": z["verpasst"]}


def flotte_daten(dateiname="flotte.json"):
    """Wärme-Router (daten/ergebnisse/flotte.json, src/scheduler/flotte.py) kompakt fürs Dashboard."""
    p = ROOT / "daten" / "ergebnisse" / dateiname
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    zusage = {}
    for name, z in d["zusage_spot"].items():
        zusage[name] = {k: z[k] for k in ("sicherheitsfaktor", "fehltage_kalibrierung", "fehltage_auswertung",
                                          "jahr", "ergebnis_mit_zusage_chf")}
        zusage[name]["tage"] = [[t["tag"], t["prognose_server_h"], t["geliefert_server_h"]] for t in z["tage"]]
    return {k: d[k] for k in ("server_pro_haus", "server_bad_regel", "server_bad_nach_nachfrage",
                              "suche_senkengroesse_alibaba", "ergebnisse", "regel_ueberschuss")} | {
                                  "zusage": zusage, "leistungsprofil": d.get("leistungsprofil")}


def main():
    profil = profil_laden()
    laeufe = {}
    for sz in ("spot", "alibaba"):
        for regel in ("rechnen", "abgeben"):
            for n in range(1, 14):
                haus = Haus(n, sz, regel, profil)
                monate = defaultdict(lambda: defaultdict(float))
                tage = {k: [] for k in TAGE}
                for h in range(len(profil)):
                    z = haus.schritt(h)
                    m = monate[z["zeit"][:7]]
                    for k in ("bedarf_kwh", "genutzt_kwh", "backup_kwh", "abgefuehrt_kwh", "strom_kwh"):
                        m[k] += z[k]
                    m["stunden"] += 1
                    for name, tag in TAGE.items():
                        if z["zeit"].startswith(tag):
                            tage[name].append({k: z[k] for k in (
                                "zeit", "temp_c", "bedarf_kwh", "heizung_kwh", "warmwasser_kwh",
                                "waerme_kwh", "genutzt_kwh", "speicher_kwh", "abgefuehrt_kwh",
                                "backup_kwh", "server_laufend")})
                b = haus.bilanz()
                b["strom_kwh"] = round(haus.z["strom"], 1)
                b["genutzt_kwh_genau"] = round(haus.z["genutzt"], 1)
                laeufe[f"{sz}|{regel}|{n}"] = {
                    "bilanz": b,
                    "monate": [{"monat": k, **{kk: round(vv, 1) for kk, vv in v.items()}}
                               for k, v in sorted(monate.items())],
                    "tage": tage,
                    "abschalten": abschalten_daten(n, sz, regel, profil),
                }
    messung = json.loads((ROOT / "messungen" / "energie.json").read_text())
    jobtypen = json.loads((ROOT / "daten" / "jobtypen.json").read_text())["typen"]
    serverbetrieb = ROOT / "daten" / "ergebnisse" / "serverbetrieb.json"
    daten = {"erzeugt": "python3 src/dashboard_daten.py", "annahmen": A.als_liste(),
             "messung_a": messung, "jobtypen": jobtypen, "tage": TAGE, "laeufe": laeufe,
             "abschalt_profil": {"leerlauf_watt": LEISTUNG.leerlauf_watt, "standby_watt": LEISTUNG.standby_watt,
                                 "start_minuten": LEISTUNG.start_minuten},
             "flotte": flotte_daten(),
             "flotte_abschalten": flotte_daten("flotte_abschalten.json"),
             "serverbetrieb": json.loads(serverbetrieb.read_text()) if serverbetrieb.exists() else None}
    aus = ROOT / "dashboard" / "daten.js"
    aus.write_text("window.DATEN = " + json.dumps(daten, ensure_ascii=False) + ";\n")
    print(f"{aus.relative_to(ROOT)}: {len(laeufe)} Läufe, {aus.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
