"""Standorte der Flotte und Vergleich 0/1 Senke (Design-Doc Baustein 1, 4, 7).

- Häuser: vorerst 20 × Referenzhaus (TODOS.md, D3). Serverzahl nach Serverregel: kleinste Zahl mit
  Deckung ≥ 92,9 % im Szenario «spot» → 8.
- Senke: Sportbad im Gartenbad St. Jakob (daten/HALLENBAD.md). Ein Hallenbad scheidet aus (Rialto
  Sommerpause, Eglisee nur im Winter). Profil aus Jahresbedarf und Monatsanteilen, gleichmässig auf die
  Betriebstage 26.4.–5.10.2025 verteilt. Serverzahl nach Senkenregel: Median des Wärmebedarfs Juni–August
  ÷ 0,8 ÷ 1 kW, abgerundet (→ 170 Server). Befund: Das ist viel mehr, als Aufträge da sind. Darum wird
  zusätzlich die Senkengrösse nach Nachfrage gesucht (10–80 Server, bestes Ergebnis im Szenario
  «Nur Jobs mit Frist») und beide Varianten werden ausgewiesen.
- Vergleich: dieselben 20 Häuser mit und ohne Senke, derselbe Jobstrom (Alibaba-Rate × Server der Häuser).

Aufruf: python3 src/scheduler/flotte.py        → daten/ergebnisse/flotte.json
"""
import json
import math
import statistics
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.jahr import Haus, profil_laden, simuliere  # noqa: E402
from src.scheduler.router import Flotte  # noqa: E402

AUS = A.ROOT / "daten" / "ergebnisse"
DECKUNG_ZIEL = 0.929  # Design-Doc: kleinste Serverzahl mit Deckung ≥ 92,9 % (Referenzhaus → 8)


def serverzahl_haus(profil, n_max=13):
    for n in range(1, n_max + 1):
        if simuliere(n, "spot", "rechnen", profil=profil)["deckungsgrad"] >= DECKUNG_ZIEL:
            return n
    return n_max


def bad_profil(profil):
    """Stundenprofil Sportbad St. Jakob auf der Zeitachse des Referenzprofils (Bedarf in Spalte 'heizung')."""
    jahr_kwh = A.wert("bad_jahresbedarf_kwh")
    anteile = A.wert("bad_monatsanteile")
    von, bis = (date.fromisoformat(d) for d in A.wert("bad_betrieb_2025"))
    offen = [von <= date.fromisoformat(p["zeit"][:10]) <= bis for p in profil]
    stunden_offen = {}
    for p, o in zip(profil, offen):
        if o:
            stunden_offen[p["zeit"][5:7]] = stunden_offen.get(p["zeit"][5:7], 0) + 1
    neu = []
    for p, o in zip(profil, offen):
        m = p["zeit"][5:7]
        kw = jahr_kwh * anteile[int(m) - 1] / stunden_offen[m] if o and stunden_offen.get(m) else 0.0
        neu.append({**p, "heizung": kw, "ww": 0.0})
    return neu


def serverzahl_senke(profil_senke):
    sommer = [p["heizung"] + p["ww"] for p in profil_senke if p["zeit"][5:7] in ("06", "07", "08")]
    return math.floor(statistics.median(sommer) / A.wert("waermerueckgewinnung") / A.wert("server_kw"))


def kosten_bad(n):
    """Eigene Kosten der Senke (Schätzung): kein neuer Speicher (Becken), Einbau pro Server wie im Haus."""
    return {"speicher_chf": 0, "einbau_chf": A.wert("einbau_chf") * n / 8}


def baue(n_haeuser, n_haus, szenario, regel, profil, bad=None, n_bad=0):
    st = [Haus(n_haus, szenario, regel, profil, name=f"Haus {i + 1:02d}", mit_ankuenften=False)
          for i in range(n_haeuser)]
    kosten = {}
    if n_bad:
        st.append(Haus(n_bad, szenario, regel, bad, speicher_kwh=A.wert("bad_speicher_kwh"),
                       name="Sportbad St. Jakob", typ="bad", mit_ankuenften=False))
        kosten["Sportbad St. Jakob"] = kosten_bad(n_bad)
    # derselbe Jobstrom in allen Varianten: Alibaba-Rate × Server der Häuser
    return Flotte(st, szenario, regel, nachfrage_server=n_haeuser * n_haus), kosten


def lauf(n_h, n_haus, sz, regel, profil, bad, n_bad, name, monatlich=True):
    f, kosten = baue(n_h, n_haus, sz, regel, profil, bad, n_bad)
    f.simuliere(monatlich)
    b = f.bilanz(kosten=kosten)
    b["variante"], b["server_bad"] = name, n_bad
    if monatlich:
        b["monate"] = [{"monat": k, **{kk: round(vv, 1) for kk, vv in v.items()}} for k, v in sorted(f.monate.items())]
    return b, f, kosten


def zeile(b):
    g = b["gruppen"]
    return (f"{b['szenario']:7s} {b['variante']:34s} Ausl. Haus {g['haus']['auslastung']:.1%}"
            + (f" Bad {g['bad']['auslastung']:.1%}" if "bad" in g else "          ")
            + f"  abgeführt {b['waerme_abgefuehrt_kwh']:>6,} kWh  abgegeben {b['abgegeben_server_h']:>8,.0f} h"
            f"  verpasst {b['verpasste_fristen_anteil']:.2%}  Migr. {b['migrationen']:>5,}"
            f"  Ergebnis {b['dh_ergebnis_pro_jahr_chf']:>10,} CHF/J")


def main():
    from src.scheduler.zusage import prognose_profil, rechne_zusage
    profil = profil_laden()
    n_haus = serverzahl_haus(profil)
    bad = bad_profil(profil)
    n_regel = serverzahl_senke(bad)
    n_h = A.wert("flotte_haeuser")
    regel = "abgeben"  # Wärme zuerst: kein Dauerbetrieb mit Rückkühler (Premise 2)

    # Senkengrösse nach Nachfrage: bestes Ergebnis im Hauptszenario «Nur Jobs mit Frist»
    suche = []
    for n_bad in range(10, 90, 10):
        b, _, _ = lauf(n_h, n_haus, "alibaba", regel, profil, bad, n_bad, f"Sportbad {n_bad}", monatlich=False)
        suche.append({"server_bad": n_bad, "ergebnis_chf": b["dh_ergebnis_pro_jahr_chf"],
                      "abgegeben_server_h": b["abgegeben_server_h"]})
        print(f"Suche Sportbad {n_bad:3d} Server: {b['dh_ergebnis_pro_jahr_chf']:>10,} CHF/J", flush=True)
    n_best = max(suche, key=lambda r: r["ergebnis_chf"])["server_bad"]

    varianten = [("0 Senken", 0), (f"Sportbad {n_best} (nach Nachfrage)", n_best),
                 (f"Sportbad {n_regel} (Senkenregel)", n_regel)]
    ergebnisse = []
    for sz in ("alibaba", "spot"):
        for name, n_bad in varianten:
            b, f, kosten = lauf(n_h, n_haus, sz, regel, profil, bad, n_bad, name)
            ergebnisse.append(b)
            print(zeile(b), flush=True)

    # Day-ahead-Zusage auf Flottenebene (Szenario spot = verfügbare Kapazität), Senke ohne Prognosefehler
    zusage = {}
    for name, n_bad in varianten[:2]:
        f, kosten = baue(n_h, n_haus, "spot", regel, profil, bad, n_bad)
        r, f = rechne_zusage(f, prognose_profil(profil))
        j = r["jahr"]
        b = f.bilanz(anteil_fest_gebucht=j["anteil_fest_gebucht"], fehlmenge_server_h=j["fehlmenge_server_h"],
                     kosten=kosten)
        zusage[name] = dict(r)
        zusage[name]["ergebnis_mit_zusage_chf"] = b["dh_ergebnis_pro_jahr_chf"]
        print(f"Zusage {name}: Faktor {r['sicherheitsfaktor']}, zusagbar {j['zusagbarer_anteil']:.1%}, "
              f"fest {j['anteil_fest_gebucht']:.1%}, Fehltage Auswertung {r['fehltage_auswertung']:.1%}, "
              f"Ergebnis {b['dh_ergebnis_pro_jahr_chf']:,} CHF/J", flush=True)

    AUS.mkdir(parents=True, exist_ok=True)
    (AUS / "flotte.json").write_text(json.dumps({
        "erzeugt": "python3 src/scheduler/flotte.py", "regel_ueberschuss": regel,
        "server_pro_haus": n_haus, "server_bad_regel": n_regel, "server_bad_nach_nachfrage": n_best,
        "suche_senkengroesse_alibaba": suche, "zusage_spot": zusage,
        "annahmen": {k: A.als_liste()[k] for k in ("flotte_haeuser", "bad_jahresbedarf_kwh", "bad_monatsanteile",
                                                    "bad_betrieb_2025", "bad_speicher_kwh", "migration_min")},
        "ergebnisse": ergebnisse}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
