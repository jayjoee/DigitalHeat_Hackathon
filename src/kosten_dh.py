"""Alle Zahlen für docs/wirtschaft/KOSTEN_DH.md aus einer Quelle.

Simuliert das Referenzhaus und das Durchschnitts-EFH (17'000 kWh) im Abschaltmodell
(230 W Leerlauf, 10 W Standby, 5 min Start) und im Idealmodell des Case. Danach rechnet
es mit src/wirtschaft.py Ergebnis, Rückzahlung, Zinsfuss, Break-even und die Sensitivitäten.

Aufruf: python3 src/kosten_dh.py        # schreibt daten/ergebnisse/kosten_dh.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.dashboard3d_daten import profil_haus2  # noqa: E402
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.jahr import Haus, profil_laden  # noqa: E402
from src.scheduler.serverbetrieb import HausMitServerbetrieb, Leistungsprofil  # noqa: E402
from src.wirtschaft import break_even, rechne  # noqa: E402

AUS = A.ROOT / "daten" / "ergebnisse" / "kosten_dh.json"
SPOT = 0.294  # L4-Spot-Preis (AWS g6 Spot), Untergrenze für die übrigen Stunden


def simuliere(n, profil, strategie="abschalten", leerlauf_watt=230):
    """Jahreswerte eines Hauses: verkaufte Server-h, genutzte Wärme, Gesamtstrom, Deckung."""
    if strategie == "case":
        haus = Haus(n, "spot", profil=profil)
    else:
        haus = HausMitServerbetrieb(n, "spot", profil, Leistungsprofil(leerlauf_watt, 10, 5),
                                    abschalten=strategie == "abschalten")
    monate = [0.0] * 12
    for h in range(len(profil)):
        vorher = haus.z.get("rechenstrom", haus.z["strom"])
        haus.schritt(h)
        monate[int(profil[h]["zeit"][5:7]) - 1] += haus.z.get("rechenstrom", haus.z["strom"]) - vorher
    z = haus.z
    kw = A.wert("server_kw")
    return {"n": n, "server_h": z.get("rechenstrom", z["strom"]) / kw,
            "waerme_kwh": z["genutzt"], "strom_kwh": z["strom"],
            "deckung": z["genutzt"] / z["bedarf"], "monate_server_h": [m / kw for m in monate]}


def rueckzahlung(r):
    """Jahre bis das kumulierte Geld (inkl. Restwert im letzten Jahr) die Investition deckt."""
    kum = -r["investition_chf"]
    for j in r["jahre"]:
        if kum + j["cashflow"] >= 0:
            return j["jahr"] - 1 + -kum / j["cashflow"]
        kum += j["cashflow"]
    return None


def zinsfuss(r):
    cfs = [-r["investition_chf"]] + [j["cashflow"] for j in r["jahre"]]
    lo, hi = -0.9, 1.0
    for _ in range(100):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if sum(c / (1 + m) ** t for t, c in enumerate(cfs)) > 0 else (lo, m)
    return m


def nullstelle(f, lo=0.0, hi=3.0):
    """Wert x, bei dem f(x) (steigend) das Vorzeichen wechselt."""
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) < 0 else (lo, m)
    return hi


def haus_kennzahlen(s, **ue):
    a = (s["n"], s["server_h"], s["waerme_kwh"])
    r = rechne(*a, strom_kwh=s["strom_kwh"], **ue)
    erg = lambda **k: rechne(*a, strom_kwh=s["strom_kwh"], **{**ue, **k})["ergebnis_pro_jahr_chf"]  # noqa: E731
    vorsichtig = rechne(*a, strom_kwh=s["strom_kwh"], **{**ue, "spotpreis_chf_karte_h": SPOT})
    return {
        "server": s["n"], "deckung": round(s["deckung"], 4), "server_h": round(s["server_h"]),
        "strom_kwh": round(s["strom_kwh"], 1), "waerme_kwh": round(s["waerme_kwh"], 1),
        "hardware_chf": r["hardware_chf"], "investition_chf": r["investition_chf"],
        "erloes_jahr1_chf": r["jahre"][0]["erloes"], "laufend_jahr1_chf": r["jahre"][0]["laufend"],
        "ergebnis_chf": r["ergebnis_pro_jahr_chf"],
        "ergebnis_rest_spot_chf": vorsichtig["ergebnis_pro_jahr_chf"],
        "ergebnis_rest_unverkauft_chf": erg(spotpreis_chf_karte_h=0.0),
        "gewinn_nach_steuer_mittel_chf": r["gewinn_nach_steuer_mittel_chf"],
        "rueckzahlung_jahre": round(rueckzahlung(r), 2), "zinsfuss": round(zinsfuss(r), 4),
        "zinsfuss_rest_spot": round(zinsfuss(vorsichtig), 4),
        "break_even_anker_chf_karte_h": break_even(*a, strom_kwh=s["strom_kwh"], **ue),
        "break_even_anker_rest_spot_chf_karte_h": break_even(*a, strom_kwh=s["strom_kwh"],
                                                             **{**ue, "spotpreis_chf_karte_h": SPOT}),
        "break_even_rest_chf_karte_h": round(nullstelle(lambda x: erg(spotpreis_chf_karte_h=x)), 4),
        "jahre": r["jahre"],
    }


def sensitivitaeten(s):
    a = (s["n"], s["server_h"], s["waerme_kwh"])
    erg = lambda h=None, **k: rechne(s["n"], h if h is not None else s["server_h"], s["waerme_kwh"],  # noqa: E731
                                     strom_kwh=s["strom_kwh"], **k)["ergebnis_pro_jahr_chf"]
    p = {k: A.wert(k) for k in ("vertragspreis_chf_karte_h", "spotpreis_chf_karte_h", "anteil_fest_gebucht",
                                "server_preis_chf")}
    mix = p["anteil_fest_gebucht"] * p["vertragspreis_chf_karte_h"] + (1 - p["anteil_fest_gebucht"]) * p["spotpreis_chf_karte_h"]
    guenstig = dict(vertragspreis_chf_karte_h=0.55, spotpreis_chf_karte_h=0.65, server_preis_chf=p["server_preis_chf"] * 0.85,
                    kuehlung_chf_pro_kw=1260, einbau_chf=6400, zins=0.035, versicherung_anteil=0.003, gpu_ausfall=0.03)
    teuer = dict(vertragspreis_chf_karte_h=0.45, spotpreis_chf_karte_h=0.45, server_preis_chf=p["server_preis_chf"] * 1.15,
                 kuehlung_chf_pro_kw=3780, einbau_chf=12800, zins=0.055, versicherung_anteil=0.01, gpu_ausfall=0.061)
    ohne_preis = lambda d: {k: v for k, v in d.items() if k != "vertragspreis_chf_karte_h"}  # noqa: E731
    return {
        "mischpreis_chf_karte_h": round(mix, 4),
        # Weniger verkauft: Roche nimmt seinen festen Anteil der vollen Stunden immer ab, es fehlen Stunden aus dem Rest
        # (gleiche Regel wie src/firma.py). Darum höchstens bis auf den festen Anteil hinunter.
        "verkaufte_stunden": {f"{x:.0%}": erg(s["server_h"] * x, anteil_fest_gebucht=p["anteil_fest_gebucht"] / x)
                              for x in (1.0, 0.9, 0.8, 0.7, 0.6) if x >= p["anteil_fest_gebucht"]},
        "verkaufte_stunden_nullpunkt": round(nullstelle(
            lambda x: erg(s["server_h"] * x, anteil_fest_gebucht=p["anteil_fest_gebucht"] / x),
            p["anteil_fest_gebucht"], 1), 4),
        "anker_preis": {f"{x:.2f}": erg(vertragspreis_chf_karte_h=x) for x in (0.40, 0.45, 0.50, 0.55, 0.60)},
        "rest_preis": {f"{x:.3f}": erg(spotpreis_chf_karte_h=x) for x in (0.0, SPOT, 0.40, 0.50, 0.55, 0.60, 0.68)},
        "fest_gebucht": {f"{x:.0%}": erg(anteil_fest_gebucht=x) for x in (0.0, 0.42, 0.60, 0.80, 1.0)},
        "fest_gebucht_rest_spot": {f"{x:.0%}": erg(anteil_fest_gebucht=x, spotpreis_chf_karte_h=SPOT)
                                   for x in (0.0, 0.42, 0.60, 0.80, 1.0)},
        "anker_preis_faellt_auch": erg(anteil_fest_gebucht=0.0, spotpreis_chf_karte_h=mix),
        "rest_preis_fest": erg(spot_preisverfall=0.0),
        "zins": {f"{x:.3f}": erg(zins=x) for x in (0.035, 0.045, 0.055, 0.08, 0.12)},
        "hardware_minus15": erg(server_preis_chf=p["server_preis_chf"] * 0.85),
        "hardware_plus15": erg(server_preis_chf=p["server_preis_chf"] * 1.15),
        "firmenanteil": {str(x): erg(firmenanteil_chf=x) for x in (1200, 5400, 10000)},
        "versicherung": {str(x): erg(versicherung_anteil=x) for x in (0.003, 0.006, 0.01)},
        "einbau": {str(x): erg(einbau_chf=x) for x in (6400, 9000, 12800)},
        "waermepreis_7rp": erg(waermepreis_haushalt_chf_kwh=0.07),
        "strompreis_c2": erg(strompreis_chf_kwh=0.32745),
        "marktplatz_preis_jahr1": round(nullstelle(lambda x: erg(anteil_fest_gebucht=0.0, plattform_anteil=0.20,
                                                                 spotpreis_chf_karte_h=x)), 4),
        "bandbreite": {
            "guenstig": {"ergebnis_chf": erg(**guenstig),
                         "break_even_anker": break_even(*a, strom_kwh=s["strom_kwh"], **ohne_preis(guenstig))},
            "teuer": {"ergebnis_chf": erg(**teuer),
                      "break_even_anker": break_even(*a, strom_kwh=s["strom_kwh"], **ohne_preis(teuer))},
            "annahmen": {"guenstig": guenstig, "teuer": teuer},
        },
    }


def zusage_idealmodell(profil):
    """Referenzhaus im Idealmodell ohne und mit Zusage am Vortag (daten/ergebnisse/zusage_8_spot.json)."""
    z = json.loads((A.ROOT / "daten" / "ergebnisse" / "zusage_8_spot.json").read_text())["jahr"]
    s = simuliere(8, profil, "case")
    a = (8, s["server_h"], s["waerme_kwh"])
    mit = rechne(*a, z["fehlmenge_server_h"], strom_kwh=s["strom_kwh"], anteil_fest_gebucht=z["anteil_fest_gebucht"])
    return {"ohne_chf": rechne(*a, strom_kwh=s["strom_kwh"])["ergebnis_pro_jahr_chf"],
            "mit_chf": mit["ergebnis_pro_jahr_chf"], "gutschrift_jahr1_chf": mit["jahre"][0]["fehlmenge"],
            "anteil_fest_gebucht": z["anteil_fest_gebucht"], "fehlmenge_server_h": z["fehlmenge_server_h"]}


HEIZSAISON = (10, 11, 12, 1, 2, 3)  # Case: Heizung Oktober–März


def nachfrage_szenarien(s):
    """Zwischen «genug Aufträge» und «nur Roche»: Roche nimmt seinen Anteil aller wärmegeführten Stunden,
    ein Winterkunde die übrigen Stunden der Heizsaison zum Preis der übrigen Stunden."""
    H = s["server_h"]
    fest = A.wert("anteil_fest_gebucht")
    rest_preis = A.wert("spotpreis_chf_karte_h")
    winter = sum(s["monate_server_h"][m - 1] for m in HEIZSAISON)
    rest_w, rest_s = (1 - fest) * winter, (1 - fest) * (H - winter)
    a = (s["n"], s["waerme_kwh"])

    def erg(verkauft, preis_rest):
        return rechne(a[0], verkauft, a[1], strom_kwh=s["strom_kwh"], anteil_fest_gebucht=fest * H / verkauft,
                      spotpreis_chf_karte_h=preis_rest)["ergebnis_pro_jahr_chf"]
    return {
        "heizsaison_monate": list(HEIZSAISON),
        "anteil_stunden_heizsaison": round(winter / H, 4),
        "genug_auftraege": erg(H, rest_preis),
        "winterkunde_sommer_spot": erg(H, (rest_w * rest_preis + rest_s * SPOT) / (rest_w + rest_s)),
        "winterkunde_sommer_unverkauft": erg(fest * H + rest_w, rest_preis),
        "anteil_verkauft_sommer_unverkauft": round((fest * H + rest_w) / H, 4),
        "nur_roche": erg(fest * H, rest_preis),
    }


def pilot_schwellen(s, sens, r):
    """Werte, ab denen sich das Referenzhaus nicht mehr trägt (alles andere wie gerechnet)."""
    a = (s["n"], s["server_h"], s["waerme_kwh"])
    erg = lambda **k: rechne(*a, strom_kwh=s["strom_kwh"], **k)["ergebnis_pro_jahr_chf"]  # noqa: E731
    l4_h = s["server_h"] * A.wert("karten_pro_server")
    roche_gpus = 3500  # «über 3'500 GPUs» (docs/kunden/PHARMA_SICHT.md)
    return {
        "verkaufte_stunden_min": sens["verkaufte_stunden_nullpunkt"],
        "roche_preis_min_rest_spot_chf_karte_h": r["break_even_anker_rest_spot_chf_karte_h"],
        "roche_preis_min_rest_055_chf_karte_h": r["break_even_anker_chf_karte_h"],
        "rest_preis_min_chf_karte_h": r["break_even_rest_chf_karte_h"],
        "serverpreis_max_chf": round(nullstelle(lambda x: -erg(server_preis_chf=x), 0, 200000)),
        "serverpreis_gerechnet_chf": A.wert("server_preis_chf"),
        "l4_stunden_pro_haus": round(l4_h),
        "roche_l4_stunden_pro_haus": round(l4_h * A.wert("anteil_fest_gebucht")),
        "roche_gpus": roche_gpus,
        "anteil_roche_kapazitaet": round(l4_h * A.wert("anteil_fest_gebucht") / (roche_gpus * 8760), 4),
        # Pilot: Einbau, Speicher und Netzwerk wie für 8 kW, aber nur 2 Server bestückt
        "pilot_investition_2_server_chf": rechne(2, 1.0, 0.0)["investition_chf"],
    }


def main():
    profil = profil_laden()
    efh, _ = profil_haus2(profil)
    ref = {n: simuliere(n, profil) for n in (6, 7, 8, 9, 10, 13)}
    daten = {
        "erzeugt": "python3 src/kosten_dh.py",
        "betrieb": "Abschaltmodell: 230 W Leerlauf, 10 W Standby, 5 min Start (src/scheduler/serverbetrieb.py)",
        "preise": {k: A.wert(k) for k in ("vertragspreis_chf_karte_h", "anteil_fest_gebucht", "spotpreis_chf_karte_h",
                                          "spot_preisverfall", "plattform_anteil")},
        "spot_untergrenze_chf_karte_h": SPOT,
        "referenzhaus": haus_kennzahlen(ref[8]),
        "efh_4": haus_kennzahlen(simuliere(4, efh)),
        "efh_5": haus_kennzahlen(simuliere(5, efh)),
        "idealmodell": {name: haus_kennzahlen(simuliere(n, p, "case"))
                        for name, n, p in (("referenzhaus", 8, profil), ("efh_4", 4, efh), ("efh_5", 5, efh))},
        "serverzahl": [{"server": n, "deckung": round(s["deckung"], 4),
                        "ergebnis_chf": rechne(n, s["server_h"], s["waerme_kwh"], strom_kwh=s["strom_kwh"])["ergebnis_pro_jahr_chf"]}
                       for n, s in ref.items()],
        "leerlauf": {str(w): haus_kennzahlen(simuliere(8, profil, "abschalten", w))["ergebnis_chf"] for w in (100, 350)},
        "pausieren_230w": haus_kennzahlen(simuliere(8, profil, "pausieren", 230))["ergebnis_chf"],
        "sensitivitaeten": sensitivitaeten(ref[8]),
        "zusage_idealmodell": zusage_idealmodell(profil),
        "nachfrage_szenarien": nachfrage_szenarien(ref[8]),
    }
    daten["pilot_schwellen"] = pilot_schwellen(ref[8], daten["sensitivitaeten"], daten["referenzhaus"])
    AUS.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    r = daten["referenzhaus"]
    print(f"Referenzhaus: {r['ergebnis_chf']:,} CHF/J, Rest nur Spot {r['ergebnis_rest_spot_chf']:,}, "
          f"Break-even Ankerkunde {r['break_even_anker_chf_karte_h']} CHF/L4-h  → {AUS.relative_to(A.ROOT)}")


if __name__ == "__main__":
    main()
