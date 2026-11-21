"""Firmenrechnung DigitalHeat: Ausbau über mehrere Jahre, Skaleneffekte, Förderbeiträge, Holz statt Öl.

Grundlage pro Haus ist das Abschaltmodell des Referenzhauses (src/scheduler/serverbetrieb.py, 230 W Leerlauf,
genug Aufträge) und dieselbe Kostenformel wie in src/wirtschaft.py. Neu auf Firmenebene:

1. Ausbauplan: neue Häuser pro Jahr (Pilot zuerst). Hardware hält 5 Jahre, danach wird sie ersetzt.
2. Skaleneffekte
   - Mengenrabatt Server ab einer Bestellmenge pro Jahr,
   - Lernkurve beim Einbau (jede Verdopplung der eingebauten Häuser senkt die Einbaukosten),
   - Fixkosten der Firma (Team, ISO 27001, Büro) verteilen sich auf mehr Häuser,
   - dichtere Servicetouren senken die Einsatzkosten.
3. Förderbeiträge wie für eine Luft/Wasser-Wärmepumpe in Basel-Stadt (DigitalHeat erwartet die Anerkennung):
   Fr. 8'000 + Fr. 250 pro kW thermisch ausserhalb, halb so viel innerhalb des Fernwärmegebiets, höchstens 40 %
   der Investition (bs.ch/en/node/39393, node/28384, Stand Oktober 2026). Ausbezahlt an den Eigentümer, der sie
   vertraglich an DigitalHeat abtritt.
4. Keine Ölheizung mehr: Ölkessel und Tank werden zurückgebaut. Die restlichen Prozente liefert der Holzofen
   oder das Cheminée, das viele ältere Häuser schon haben (Team-Annahme, keine Kosten für DigitalHeat).
5. Steuer auf Firmenebene mit Verlustvortrag (7 Jahre), Gewinnsteuer Basel-Stadt.

6. Preise nach Kalenderjahr: Der Preis der übrigen Stunden sinkt jedes Kalenderjahr (nicht pro Kohorte neu ab
   Listenpreis), die laufenden Kosten steigen ebenso nach Kalenderjahr. Roche-Preis fest.
7. Absatz: Anteil der Server-Stunden, die verkauft werden. Roche nimmt seinen Anteil fest ab, es fehlen Stunden
   aus dem Rest. Der Strom bleibt gleich, weil das Haus die Wärme trotzdem braucht (vorsichtig).

Kennzahlen: Jahresrechnung, freier Cashflow, Kapitalbedarf und Payback ohne Kredit, Projekt-IRR über 10 Jahre
ohne Endwert (Hauptzahl) und mit Restbuchwert als Endwert. Die Eigenkapitalsicht mit 50 % Kredit steht nur
noch zur Information in der JSON-Datei.

    python3 src/firma.py                 # → daten/ergebnisse/firma.json
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.wirtschaft import rechne, parameter  # noqa: E402
from src.scheduler import annahmen as A  # noqa: E402

# ---- Annahmen der Firmenrechnung (Wert, Quelle) ----
F = {
    "ausbau_neue_haeuser": ([5, 15, 30, 50, 70], "Annahme Team: Pilot 5 Häuser, dann Ausbau in Basel-Stadt; "
                            "170 Häuser = 10'880 L4, rund dreimal so viele GPUs, wie Roche heute betreibt (PHARMA_SICHT.md)"),
    "horizont_jahre": (10, "Zwei Hardware-Generationen à 5 Jahre (nur wenn nur_erste_generation=False)"),
    "nur_erste_generation": (True, "Hauptrechnung: jedes Haus läuft 5 Jahre mit seiner ersten Hardware, kein Ersatz, "
                             "Horizont bis die letzte Kohorte ausläuft (2027–2035); kein Endwert nötig"),
    "start_jahr": (2027, "Pilot nach dem Hackathon"),
    # Skaleneffekte
    "mengenrabatt": ([(0, 0.0), (80, 0.05), (300, 0.10)],
                     "Schätzung: Rabatt auf den Serverpreis ab 80 bzw. 300 Servern pro Jahr; übliche Volumenrabatte "
                     "für Server 5–15 %, keine Offerte"),
    "lernrate_einbau": (0.15, "Schätzung: −15 % Einbaukosten je Verdopplung der eingebauten Häuser "
                        "(Lernraten bei PV- und Wärmepumpen-Installation 10–20 %), Untergrenze 50 %"),
    "service_dichte_rabatt": ([(0, 0.0), (50, 0.10), (150, 0.20)],
                              "Schätzung: kürzere Anfahrten bei dichterem Netz (Anfahrt 1,60 CHF/km, SAK)"),
    # Fixkosten der Firma (ersetzen den bisherigen Firmenanteil von 1'200 CHF pro Haus)
    "fte_kosten_chf": (130_000, "Schätzung: Lohn inkl. Sozialleistungen, ICT/Technik in der Schweiz ≈ 9'000 CHF × 13 + 15 %"),
    "fte_grundteam": (2.0, "Annahme: Gründerteam Technik und Kunden"),
    "fte_pro_haus": (1 / 40, "Annahme: 1 Person Betrieb/Einbauplanung pro 40 Häuser"),
    "iso27001_chf": (40_000, "Schätzung: Zertifizierung und jährliche Audits für Pharma-Kunden"),
    "buero_it_chf": (40_000, "Schätzung: Büro, Software, Firmenversicherung, Treuhand"),
    "vertrieb_chf": (30_000, "Schätzung: Vertrieb bei Pharma, Banken, Spitälern"),
    # Förderung und Holz
    "foerderung_basis_chf": (8_000, "bs.ch/en/node/39393: Luft/Wasser-WP ausserhalb Fernwärmegebiet Fr. 8'000 + 250/kWth"),
    "foerderung_pro_kwth_chf": (250, "bs.ch/en/node/39393"),
    "anteil_fernwaermegebiet": (0.5, "Annahme: die Hälfte der Öl-Häuser liegt im Fernwärmegebiet (dort halbe Beiträge)"),
    "foerderung_max_anteil": (0.40, "bs.ch/en/node/28384: höchstens 40 % der Investition"),
    "foerderung_erhalten": (True, "DigitalHeat-Angabe: Anerkennung wie Wärmepumpe wahrscheinlich; nicht zugesichert"),
    "holzofen_chf": (0, "Team-Annahme: Zielhäuser (ältere Öl- und Gas-Häuser) haben oft schon einen Holzofen oder ein "
                     "Cheminée, das für die wenigen kalten Tage genutzt wird; keine BFS-Zahl zu Zusatzheizungen gefunden"),
    "rueckbau_oel_chf": (4_000, "Schätzung: Ölkessel und Tank zurückbauen und entsorgen"),
    "absatz_anteil": (1.0, "Annahme Basisfall: alle Server-Stunden verkauft (KOSTEN_DH.md); Szenarien 90/80/72/60 %"),
    "ersatz_einbau_anteil": (0.25, "Annahme: Hardwareersatz nach 5 Jahren braucht 25 % des ersten Einbaus"),
    # Finanzierung
    "fremdkapital_anteil_hardware": (0.0, "Hauptrechnung ohne Kredit (Eigenkapital trägt alles). Nur zur Information: "
                                     "Rechnung mit 50 % Kredit/Leasing in nur_information_mit_kredit"),
    "eigenkapitalkosten": (0.12, "Annahme: erwartete Rendite der Investoren für ein junges Unternehmen"),
    "verlustvortrag_jahre": (7, "Schweiz: Verluste 7 Jahre vortragbar (DBG Art. 67)"),
}
W = lambda k: F[k][0]  # noqa: E731

# Haus: Abschaltmodell, Referenzhaus 8 Server (daten/ergebnisse/serverbetrieb.json)
HAUS = {"server": 8, "server_h": 34512, "strom_kwh": 35662.1, "deckung": 0.9053,
        "waerme_bedarf_kwh": 31231, "quelle": "daten/ergebnisse/serverbetrieb.json, abschalten, 230 W, spot"}
HOLZ = {"ster_chf": 250, "kwh_pro_ster": 2100, "ofen_wirkungsgrad": 0.75,
        "quelle": "Buche ≈ 500 kg/Ster × 4,2 kWh/kg (landi.ch); Händlerpreise 250–320 CHF/Ster (hornbach.ch); Ofen 75 %"}


def stufe(tabelle, x):
    wert = 0.0
    for schwelle, w in tabelle:
        if x >= schwelle:
            wert = w
    return wert


def foerderung_pro_haus(investition):
    kwth = HAUS["server"] * A.wert("server_kw") * A.wert("waermerueckgewinnung")
    voll = W("foerderung_basis_chf") + W("foerderung_pro_kwth_chf") * kwth
    mittel = voll * (1 - W("anteil_fernwaermegebiet")) + voll / 2 * W("anteil_fernwaermegebiet")
    return min(mittel, W("foerderung_max_anteil") * investition) if W("foerderung_erhalten") else 0.0, kwth


def irr(cfs):
    """Interner Zinsfuss: erste Nullstelle des Barwerts zwischen −50 % und 500 %."""
    npv = lambda r: sum(c / (1 + r) ** t for t, c in enumerate(cfs))  # noqa: E731
    raster = [-0.5 + 0.01 * n for n in range(551)]
    for lo, hi in zip(raster, raster[1:]):
        if npv(lo) * npv(hi) <= 0:
            for _ in range(80):
                m = (lo + hi) / 2
                lo, hi = (m, hi) if npv(lo) * npv(m) > 0 else (lo, m)
            return round((lo + hi) / 2, 4)
    return None


def rechne_firma(**ueber):
    F_alt = {k: F[k] for k in ueber}
    for k, v in ueber.items():
        F[k] = (v, "Szenario")
    try:
        return _rechne()
    finally:
        F.update(F_alt)


def _rechne():
    p = parameter()
    J = p["abschreibung_jahre"]
    erste = W("nur_erste_generation")
    T = len(W("ausbau_neue_haeuser")) + J - 1 if erste else W("horizont_jahre")
    plan = W("ausbau_neue_haeuser") + [0] * (T - len(W("ausbau_neue_haeuser")))
    kohorten = []  # (startjahr, häuser, investition pro Haus, Abschreibung, Restwert, Jahreszeilen)
    kumuliert = 0
    for j in range(T):
        # Ersatz der Hardware nach J Jahren
        neu, ersatz = plan[j], (plan[j - J] if j >= J and not erste else 0)
        n = neu + ersatz
        if n == 0:
            continue
        server_jahr = n * HAUS["server"]
        rabatt = stufe(W("mengenrabatt"), server_jahr)
        # Lernkurve: Einbaukosten des nächsten Hauses nach kumulierter Anzahl
        einbau_neu = 0.0
        for k in range(neu):
            b = math.log2(1 / (1 - W("lernrate_einbau")))   # Lernkurve: Kosten ∝ Anzahl^(−b)
            faktor = max(0.5, (kumuliert + k + 1) ** (-b))
            einbau_neu += p["einbau_chf"] * faktor
        kumuliert += neu
        bestand = sum(plan[max(0, j - J + 1):j + 1])
        dichte = stufe(W("service_dichte_rabatt"), bestand)
        for art, anzahl in (("neu", neu), ("ersatz", ersatz)):
            if anzahl == 0:
                continue
            einbau = einbau_neu / neu if art == "neu" else p["einbau_chf"] * W("ersatz_einbau_anteil")
            ueber = dict(server_preis_chf=p["server_preis_chf"] * (1 - rabatt), einbau_chf=einbau,
                         firmenanteil_chf=0.0, einsaetze_chf_pro_8_server=p["einsaetze_chf_pro_8_server"] * (1 - dichte))
            if art == "ersatz":
                ueber.update(speicher_chf=0.0, netzwerk_chf=0.0)
            # Kalenderjahr statt Kohortenjahr: übriger Preis ist schon j Jahre gesunken (Ersatz-Kohorten auch)
            ueber["spotpreis_chf_karte_h"] = A.wert("spotpreis_chf_karte_h") * (1 - A.wert("spot_preisverfall")) ** j
            absatz = W("absatz_anteil")
            fest = A.wert("anteil_fest_gebucht")
            if absatz < fest:
                raise ValueError("Absatz kleiner als der fest gebuchte Roche-Anteil")
            ueber["anteil_fest_gebucht"] = fest / absatz
            r = rechne(HAUS["server"], HAUS["server_h"] * absatz, 0, strom_kwh=HAUS["strom_kwh"], **ueber)
            teuerung = (1 + A.wert("kostensteigerung")) ** j
            for z in r["jahre"]:
                z["laufend"] = z["laufend"] * teuerung
            inv = r["investition_chf"]
            zusatz = (W("holzofen_chf") + W("rueckbau_oel_chf")) if art == "neu" else 0.0
            foerd, kwth = foerderung_pro_haus(inv + zusatz) if art == "neu" else (0.0, 0.0)
            inv_netto = inv + zusatz - foerd
            abschreibung = (inv_netto - r["restwert_chf"]) / J
            kohorten.append({"jahr": j, "art": art, "haeuser": anzahl, "inv": inv, "zusatz": zusatz,
                             "foerderung": foerd, "inv_netto": inv_netto, "abschreibung": abschreibung,
                             "restwert": r["restwert_chf"], "zeilen": r["jahre"], "rabatt": rabatt, "einbau": einbau})

    jahre, verlust, cf_projekt, cf_eigen, schuld, endwert = [], [], [], [], 0.0, 0.0
    for j in range(T):
        akt = [k for k in kohorten if k["jahr"] <= j < k["jahr"] + J]
        haeuser = sum(k["haeuser"] for k in akt)
        erloes = sum(k["haeuser"] * k["zeilen"][j - k["jahr"]]["erloes"] for k in akt)
        strom = sum(k["haeuser"] * k["zeilen"][j - k["jahr"]]["strom"] for k in akt)
        betrieb = sum(k["haeuser"] * k["zeilen"][j - k["jahr"]]["laufend"] for k in akt)
        fte = W("fte_grundteam") + W("fte_pro_haus") * haeuser
        fix = fte * W("fte_kosten_chf") + W("iso27001_chf") + W("buero_it_chf") + W("vertrieb_chf")
        ebitda = erloes - strom - betrieb - fix
        abschreibung = sum(k["haeuser"] * k["abschreibung"] for k in akt)
        capex = sum(k["haeuser"] * (k["inv"] + k["zusatz"]) for k in kohorten if k["jahr"] == j)
        foerderung = sum(k["haeuser"] * k["foerderung"] for k in kohorten if k["jahr"] == j)
        restwert = sum(k["haeuser"] * k["restwert"] for k in kohorten if k["jahr"] + J - 1 == j)
        # Fremdkapital: Anteil der Hardware-Investition, Annuität über 5 Jahre
        neu_kredit = W("fremdkapital_anteil_hardware") * (capex - foerderung)
        schuld += neu_kredit
        zins = schuld * p["zins"]
        tilgung = sum(k["haeuser"] * W("fremdkapital_anteil_hardware") * k["inv_netto"] / J for k in akt)
        ebt = ebitda - abschreibung - zins
        # Verlustvortrag
        verlust.append(min(0.0, ebt))
        verlust = verlust[-W("verlustvortrag_jahre"):]
        steuerbar = ebt
        if ebt > 0:
            vortrag = -sum(verlust[:-1])
            nutz = min(vortrag, ebt)
            steuerbar = ebt - nutz
            rest = nutz
            for n in range(len(verlust) - 1):
                if rest <= 0:
                    break
                abbau = min(-verlust[n], rest)
                verlust[n] += abbau
                rest -= abbau
        steuer = max(0.0, steuerbar) * p["gewinnsteuer"]
        gewinn = ebt - steuer
        # Endwert: Restbuchwert der Hardware, die nach dem Horizont noch läuft (vorsichtig, ohne künftige Gewinne)
        if j == T - 1:
            # nur Kohorten, die nach dem Horizont weiterlaufen (auslaufende sind schon mit ihrem Restwert drin)
            endwert = sum(k["haeuser"] * (k["inv_netto"] - k["abschreibung"] * (j - k["jahr"] + 1))
                          for k in akt if k["jahr"] + J - 1 > j)
            restwert += endwert
        fcf = ebitda - steuer - capex + foerderung + restwert
        cf_projekt.append(fcf)  # ohne Kredit: Steuer mit Verlustvortrag, kein Zins
        cf_eigen.append(fcf - zins + neu_kredit - tilgung)
        schuld = max(0.0, schuld - tilgung)
        jahre.append({"jahr": W("start_jahr") + j, "haeuser": haeuser, "neue_haeuser": plan[j],
                      "server": haeuser * HAUS["server"], "umsatz": round(erloes), "strom": round(strom),
                      "betrieb_haeuser": round(betrieb), "fixkosten_firma": round(fix), "fte": round(fte, 1),
                      "ebitda": round(ebitda), "abschreibung": round(abschreibung), "zins": round(zins),
                      "steuer": round(steuer), "gewinn": round(gewinn), "capex": round(capex),
                      "foerderung": round(foerderung), "restwert": round(restwert), "freier_cashflow": round(fcf),
                      "cashflow_projekt": round(cf_projekt[-1]),
                      "cashflow_eigenkapital": round(cf_eigen[-1]), "schuld_ende": round(schuld)})
    cf_projekt_ohne_endwert = cf_projekt[:-1] + [cf_projekt[-1] - endwert]
    kum, minimum, payback = 0.0, 0.0, None
    for n, c in enumerate(cf_eigen):
        kum += c
        minimum = min(minimum, kum)
        if payback is None and kum >= 0 and n > 0 and minimum < 0:
            payback = W("start_jahr") + n
    kum_p, min_p, payback_p = 0.0, 0.0, None
    for n, c in enumerate(cf_projekt_ohne_endwert):
        kum_p += c
        min_p = min(min_p, kum_p)
        if payback_p is None and kum_p >= 0 and n > 0 and min_p < 0:
            payback_p = W("start_jahr") + n
    # Break-even Firma: ab wie vielen Häusern deckt der Beitrag der Häuser die Fixkosten?
    z1 = kohorten[0]["zeilen"][0]
    beitrag_haus = z1["erloes"] - z1["strom"] - z1["laufend"] - kohorten[0]["abschreibung"]
    grund = W("fte_grundteam") * W("fte_kosten_chf") + W("iso27001_chf") + W("buero_it_chf") + W("vertrieb_chf")
    break_even_haeuser = grund / (beitrag_haus - W("fte_pro_haus") * W("fte_kosten_chf"))
    k0 = kohorten[0]
    holz_kwh = HAUS["waerme_bedarf_kwh"] * (1 - HAUS["deckung"])
    ster = holz_kwh / HOLZ["kwh_pro_ster"] / HOLZ["ofen_wirkungsgrad"]
    return {
        "erzeugt": "python3 src/firma.py",
        "annahmen": {k: {"wert": v[0], "quelle": v[1]} for k, v in F.items()},
        "haus": HAUS, "holz": HOLZ,
        "pro_haus_pilot": {"investition": round(k0["inv"]), "holzofen_und_rueckbau": round(k0["zusatz"]),
                           "foerderung": round(k0["foerderung"]), "investition_netto": round(k0["inv_netto"]),
                           "beitrag_vor_fixkosten_jahr1": round(beitrag_haus)},
        "skaleneffekte": [{"jahr": W("start_jahr") + k["jahr"], "art": k["art"], "haeuser": k["haeuser"],
                           "rabatt_server": k["rabatt"], "einbau_chf": round(k["einbau"]),
                           "investition_pro_haus": round(k["inv_netto"])} for k in kohorten],
        "holz_reserve": {"waerme_kwh": round(holz_kwh), "ster_pro_jahr": round(ster, 1),
                         "kosten_haushalt_chf": round(ster * HOLZ["ster_chf"])},
        "jahre": jahre,
        "kennzahlen": {
            "projekt_irr": irr(cf_projekt_ohne_endwert), "projekt_irr_mit_endwert": irr(cf_projekt),
            "endwert_restbuchwert": round(endwert),
            "kapitalbedarf": round(-min_p), "payback_projekt": payback_p,
            "npv_projekt_12": round(sum(c / (1 + W("eigenkapitalkosten")) ** t
                                        for t, c in enumerate(cf_projekt_ohne_endwert))),
            "umsatz_ende_ausbau": jahre[len(W("ausbau_neue_haeuser")) - 1]["umsatz"],
            "break_even_haeuser": round(break_even_haeuser, 1),
            "haeuser_ende_ausbau": sum(W("ausbau_neue_haeuser")),
        },
        "eigenkapital": {"irr": irr(cf_eigen), "kapitalbedarf": round(-minimum), "payback": payback},
    }


def main():
    basis = rechne_firma()
    kredit = rechne_firma(fremdkapital_anteil_hardware=0.5)
    basis["nur_information_mit_kredit"] = {
        "hinweis": "50 % der Hardware über Kredit/Leasing zu 4,5 %; für ein junges Unternehmen ohne Sicherheiten "
                   "kaum erhältlich, deshalb nicht in den Unterlagen", **kredit["eigenkapital"]}
    zehn = rechne_firma(nur_erste_generation=False)
    basis["zehn_jahre_mit_ersatz"] = {"kennzahlen": zehn["kennzahlen"], "jahre": zehn["jahre"]}
    szen = {
        "ohne_foerderung": rechne_firma(foerderung_erhalten=False),
        "absatz_90": rechne_firma(absatz_anteil=0.9),
        "absatz_80": rechne_firma(absatz_anteil=0.8),
        "absatz_72": rechne_firma(absatz_anteil=0.72),
        "nur_roche_60": rechne_firma(absatz_anteil=0.6),
        "rest_spot": None,
        "halbes_wachstum": rechne_firma(ausbau_neue_haeuser=[5, 8, 15, 25, 35]),
    }
    # Vorsichtig: übrige Stunden nur zum L4-Spot-Preis (0,294 CHF), Roche bleibt bei 0,50 CHF
    alt = A.ANNAHMEN["spotpreis_chf_karte_h"]
    A.ANNAHMEN["spotpreis_chf_karte_h"] = (0.294, alt[1])
    try:
        szen["rest_spot"] = rechne_firma()
    finally:
        A.ANNAHMEN["spotpreis_chf_karte_h"] = alt
    # Knappe Nachfrage: nur Aufträge mit Frist (Alibaba-Trace), Wärme zuerst (Überschuss geht an andere Clouds).
    # Pro Haus aus der Flottenrechnung mit Abschalten, 20 Häuser ohne Bad (daten/ergebnisse/flotte_abschalten.json).
    fl = json.loads((ROOT / "daten" / "ergebnisse" / "flotte_abschalten.json").read_text())["ergebnisse"]
    ali = next(r for r in fl if r["szenario"] == "alibaba" and r["variante"] == "0 Senken")
    alt_haus = dict(HAUS)
    HAUS.update(server_h=ali["server_h_verkauft"] / 20, strom_kwh=ali["strom_kwh"] / 20, deckung=0.568)
    try:
        szen["knappe_nachfrage"] = rechne_firma()
    finally:
        HAUS.clear(); HAUS.update(alt_haus)
    basis["szenarien"] = {k: v["kennzahlen"] for k, v in szen.items()}
    basis["szenarien_jahre"] = {k: [{kk: j[kk] for kk in ("jahr", "umsatz", "ebitda", "gewinn", "cashflow_projekt")}
                                    for j in v["jahre"]] for k, v in szen.items()}
    ziel = ROOT / "daten" / "ergebnisse" / "firma.json"
    ziel.write_text(json.dumps(basis, indent=1, ensure_ascii=False))
    k = basis["kennzahlen"]
    print(f"Häuser bis {basis['jahre'][4]['jahr']}: {k['haeuser_ende_ausbau']}, Projekt-IRR {k['projekt_irr']} "
          f"(mit Endwert {k['projekt_irr_mit_endwert']}), Kapitalbedarf {k['kapitalbedarf']:,} CHF, "
          f"Payback {k['payback_projekt']}, Break-even ab {k['break_even_haeuser']} Häusern")
    for j in basis["jahre"]:
        print(j["jahr"], j["haeuser"], "Umsatz", f"{j['umsatz']:>10,}", "EBITDA", f"{j['ebitda']:>10,}",
              "Gewinn", f"{j['gewinn']:>10,}", "Capex", f"{j['capex']:>11,}", "CF", f"{j['cashflow_projekt']:>11,}")
    for n, s in basis["szenarien"].items():
        print(n, s)


if __name__ == "__main__":
    main()
