"""Jahressimulation für das Referenzhaus: 8'760 Stunden, Speicher, Jobs, Bilanz.

Nachfrage-Szenarien:
- "spot":    Typ A unbegrenzt verfügbar (Spot-Markt nimmt jede Kapazität ab, keine Frist).
             Ausdrücklich eine Annahme. Typ B kommt begrenzt nach Alibaba-Trace.
- "alibaba": A und B begrenzt nach Alibaba-Trace (10,1 Server-h pro Server und Tag, 94 % A / 6 % B).

Aufruf:
  python3 src/scheduler/jahr.py                    # Serverzahl 1–13, beide Szenarien, beide Regeln
  python3 src/scheduler/jahr.py --server 4 --stunden daten/ergebnisse/stunden_4.csv
"""
import argparse
import copy
import csv
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.kern import Job, Lage, entscheide  # noqa: E402

ROOT = A.ROOT
AUS = ROOT / "daten" / "ergebnisse"


def profil_laden():
    with (ROOT / A.wert("profil")).open() as f:
        return [{"zeit": r["zeit"], "temp": float(r["temp_c"]),
                 "heizung": float(r["heizbedarf_kwh"]), "ww": float(r["warmwasser_kwh"]),
                 "sonne": float(r["globalstrahlung_wm2"])} for r in csv.DictReader(f)]


def ankuenfte(n_server, szenario, saat):
    """Poisson-Ankünfte pro Stunde nach Alibaba-Tagesform. Gibt {stunde: [(typ), ...]}."""
    rnd = random.Random(saat)
    form = A.stundenprofil()
    server_h_tag = A.wert("nachfrage_server_h_pro_server_tag") * n_server
    anteil_b = A.wert("anteil_kurze_jobs_gpu_h")
    rate_b_tag = server_h_tag * anteil_b / A.wert("job_b_kwh")
    rate_a_tag = server_h_tag * (1 - anteil_b) / A.wert("job_a_kwh")
    plan = {}
    for h in range(8760):
        f = form[h % 24]
        liste = ["B"] * _poisson(rnd, rate_b_tag * f)
        if szenario == "alibaba":
            liste += ["A"] * _poisson(rnd, rate_a_tag * f)
        if liste:
            plan[h] = liste
    return plan, {"jobs_a_pro_tag": None if szenario == "spot" else round(rate_a_tag, 2),
                  "jobs_b_pro_tag": round(rate_b_tag, 2)}


def _poisson(rnd, lam):
    if lam <= 0:
        return 0
    l, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= l:
            return k
        k += 1


class Haus:
    """Zustand eines Hauses über das Jahr. `schritt(h)` rechnet eine Stunde mit dem Scheduler-Kern.

    Die Jahresbilanz (simuliere), die Live-Steuerung (live.py), die Day-ahead-Zusage (zusage.py) und
    der Wärme-Router (router.py) benutzen alle diese Klasse.

    `schritt(h)` besteht aus vier Teilen, die der Router einzeln aufruft:
      vorbereiten(h)          Ankünfte und Spot-Nachschub (nur Einzelhaus; in der Flotte macht das der Pool)
      lage(h)                 Eingang für den Kern
      fristen(h, e)           Jobs fortschreiben, Fristprüfung, Job-Zähler (in der Flotte: der Pool)
      verbuchen(h, e)         Wärmebilanz, Speicher, Strom, Backup – nur Physik dieses Standorts
    """

    def __init__(self, n_server, szenario="spot", bei_ueberschuss="rechnen", profil=None,
                 speicher_kwh=None, name="Referenzhaus", typ="haus", mit_ankuenften=True):
        self.n, self.szenario, self.regel = n_server, szenario, bei_ueberschuss
        self.name, self.typ = name, typ
        self.profil = profil or profil_laden()
        self.plan, self.raten = ankuenfte(n_server, szenario, A.wert("zufallssaat")) if mit_ankuenften else ({}, {})
        self.eta = A.wert("waermerueckgewinnung")
        self.smax = A.wert("speicher_kwh") if speicher_kwh is None else speicher_kwh
        self.s = 0.0
        self.q, self.nid = [], 0
        self.z = dict(strom=0.0, waerme=0.0, genutzt=0.0, aus_speicher=0.0, abgefuehrt=0.0, backup=0.0,
                      bedarf=0.0, jobs=0, mit_frist=0, fertig=0, verpasst=0, abgegeben=0,
                      abgegeben_kwh=0.0, verpasst_kwh=0.0, server_h_a=0.0, server_h_b=0.0)

    def _neuer_job(self, typ, h, frist):
        j = Job(self.nid, typ, h, frist, A.wert(f"job_{typ.lower()}_kwh"), typ == "A")
        self.nid += 1
        self.q.append(j)
        self.z["jobs"] += 1
        return j

    def vorbereiten(self, h):
        for typ in self.plan.get(h, []):
            self._neuer_job(typ, h, h + A.wert(f"job_{typ.lower()}_frist_h"))
            self.z["mit_frist"] += 1
        if self.szenario == "spot":
            # unbegrenzt A: immer so viel Spot-Arbeit bereithalten, dass alle Server eine Stunde voll sind
            kw = A.wert("server_kw")
            while sum(min(j.rest_kwh, kw) for j in self.q if j.typ == "A") < self.n * kw - 1e-9:
                self._neuer_job("A", h, math.inf)

    def bedarf(self, h):
        p = self.profil[h]
        return p["heizung"] + p["ww"]

    def lage(self, h):
        return Lage(h, self.bedarf(h), self.s, self.smax, self.n, A.wert("server_kw"), self.eta)

    def fristen(self, h, e):
        """Jobs fortschreiben und Fristen prüfen. Gilt für Einzelhaus und Pool (router.Pool erbt die Logik)."""
        fristen_buchen(self.q, self.z, h, e.abgegeben, e.laeufe)

    def verbuchen(self, h, e, *, zusatzstrom_kwh=0.0, zusatzwaerme_kwh=0.0):
        p, z = self.profil[h], self.z
        bedarf = self.bedarf(h)
        speicher_vorher = self.s
        strom = e.strom_kwh + zusatzstrom_kwh
        waerme = e.strom_kwh * self.eta + zusatzwaerme_kwh
        direkt = min(waerme, bedarf)
        rest = bedarf - direkt
        aus_sp = min(self.s, rest)
        self.s -= aus_sp
        backup = rest - aus_sp
        ueber = waerme - direkt
        rein = min(ueber, self.smax - self.s)
        self.s += rein
        abgef = ueber - rein
        for k, v in (("strom", strom), ("waerme", waerme), ("genutzt", direkt + aus_sp),
                     ("aus_speicher", aus_sp), ("abgefuehrt", abgef), ("backup", backup), ("bedarf", bedarf)):
            z[k] += v
        return {"zeit": p["zeit"], "temp_c": p["temp"], "bedarf_kwh": round(bedarf, 3),
                "heizung_kwh": round(p["heizung"], 3), "warmwasser_kwh": round(p["ww"], 3),
                "strom_kwh": round(strom, 3), "waerme_kwh": round(waerme, 3),
                "genutzt_kwh": round(direkt + aus_sp, 3), "speicher_vorher_kwh": round(speicher_vorher, 3),
                "speicher_kwh": round(self.s, 3), "abgefuehrt_kwh": round(abgef, 3),
                "backup_kwh": round(backup, 3), "server_laufend": round(e.strom_kwh / A.wert("server_kw"), 3),
                "warteschlange": len(self.q), "abgegeben": len(e.abgegeben)}

    def schritt(self, h):
        self.vorbereiten(h)
        e = entscheide(self.lage(h), self.q, self.regel)
        self.fristen(h, e)
        return self.verbuchen(h, e)

    def kopie(self, profil=None):
        """Unabhängige Kopie des Zustands (Jobs, Speicher, Zähler), optional mit anderem Profil (Prognose)."""
        k = copy.copy(self)
        k.q = [copy.copy(j) for j in self.q]
        k.z = dict(self.z)
        if profil is not None:
            k.profil = profil
        return k

    def bilanz(self):
        return bilanz(self.n, self.szenario, self.regel, self.z, self.raten)


def fristen_buchen(q, z, h, abgegeben, laeufe):
    """Abgaben, Fortschritt, fertige Jobs und verpasste Fristen buchen – genau einmal pro Stunde."""
    for j in abgegeben:
        q.remove(j)
        z["abgegeben"] += 1
        z["abgegeben_kwh"] += j.rest_kwh
    for j, m in laeufe:
        j.rest_kwh -= m
        j.gelaufen_kwh += m
        z[f"server_h_{j.typ.lower()}"] += m / A.wert("server_kw")
        if j.rest_kwh <= 1e-9:
            q.remove(j)
            if not math.isinf(j.frist_h):
                z["fertig"] += 1
    # Fristen prüfen: Job kann nicht mehr fertig werden
    for j in [j for j in q if not math.isinf(j.frist_h) and h + 1 >= j.frist_h]:
        q.remove(j)
        z["verpasst"] += 1
        z["verpasst_kwh"] += j.rest_kwh


def simuliere(n_server, szenario="spot", bei_ueberschuss="rechnen", stunden_csv=None, profil=None):
    haus = Haus(n_server, szenario, bei_ueberschuss, profil)
    zeilen = [haus.schritt(h) for h in range(len(haus.profil))]
    if stunden_csv:
        Path(stunden_csv).parent.mkdir(parents=True, exist_ok=True)
        with open(stunden_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(zeilen[0]))
            w.writeheader()
            w.writerows(zeilen)
    return haus.bilanz()


def bilanz(n, szenario, regel, z, raten):
    from src.wirtschaft import rechne, break_even  # Wirtschaftlichkeit DigitalHeat (KOSTEN_DH.md)
    preis_strom, preis_waerme = A.wert("strompreis_chf_kwh"), A.wert("waermewert_chf_kwh")
    server_h = z.get("rechenstrom", z["strom"]) / A.wert("server_kw")
    stromkosten = z["strom"] * preis_strom
    waermewert = z["genutzt"] * preis_waerme
    w = rechne(n, server_h, z["genutzt"], strom_kwh=z["strom"])
    be = break_even(n, server_h, z["genutzt"], strom_kwh=z["strom"])
    karten = A.wert("karten_pro_server")
    return {
        "server_pro_haus": n, "szenario": szenario, "regel_ueberschuss": regel,
        "waermebedarf_kwh": round(z["bedarf"]),
        "deckungsgrad": round(z["genutzt"] / z["bedarf"], 4),
        "waerme_genutzt_kwh": round(z["genutzt"]),
        "waerme_abgefuehrt_kwh": round(z["abgefuehrt"]),
        "anteil_abgefuehrt_von_serverwaerme": round(z["abgefuehrt"] / z["waerme"], 4) if z["waerme"] else 0,
        "backup_kwh": round(z["backup"]),
        "auslastung": round(server_h / (n * 8760), 4),
        "server_h": round(server_h),
        "server_h_a": round(z["server_h_a"]), "server_h_b": round(z["server_h_b"]),
        "jobs_mit_frist": z["mit_frist"], "jobs_fertig": z["fertig"],
        "verpasste_fristen_anteil": round(z["verpasst"] / z["mit_frist"], 4) if z["mit_frist"] else 0,
        "jobs_abgegeben": z["abgegeben"], "abgegeben_server_h": round(z["abgegeben_kwh"], 1),
        "stromkosten_chf": round(stromkosten),
        "waermewert_chf": round(waermewert),
        # Case-Definition: (Strom − Wert der genutzten Wärme) ÷ verkaufte Server-Stunden, ohne Hardware
        "break_even_chf_pro_server_h": round((stromkosten - waermewert) / server_h, 4) if server_h else None,
        # Vollrechnung DigitalHeat (src/wirtschaft.py): alle Kosten, Steuern, Zins, Restwert, 5 Jahre
        "dh_investition_chf": w["investition_chf"],
        "dh_rechenerloes_jahr1_chf": w["jahre"][0]["erloes"],
        "dh_gewinn_nach_steuer_mittel_chf": w["gewinn_nach_steuer_mittel_chf"],
        "dh_ergebnis_pro_jahr_chf": w["ergebnis_pro_jahr_chf"],
        "dh_break_even_chf_karte_h": be,
        "dh_break_even_chf_server_h": round(be * karten, 3),
        "ankuenfte": raten,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", type=int)
    ap.add_argument("--szenario", default="spot", choices=["spot", "alibaba"])
    ap.add_argument("--regel", default="rechnen", choices=["rechnen", "abgeben"])
    ap.add_argument("--stunden")
    a = ap.parse_args()
    AUS.mkdir(parents=True, exist_ok=True)
    profil = profil_laden()

    if a.server:
        r = simuliere(a.server, a.szenario, a.regel, a.stunden, profil)
        print(json.dumps(r, indent=1, ensure_ascii=False))
        return

    alle = []
    for sz in ("spot", "alibaba"):
        for regel in ("rechnen", "abgeben"):
            for n in range(1, 14):
                alle.append(simuliere(n, sz, regel, profil=profil))
    (AUS / "serverzahl.json").write_text(json.dumps(
        {"annahmen": A.als_liste(), "ergebnisse": alle}, indent=1, ensure_ascii=False))
    for sz in ("spot", "alibaba"):
        for regel in ("rechnen", "abgeben"):
            print(f"\n== Nachfrage {sz}, Überschuss: {regel}")
            print(" N  Deckung  abgeführt  Auslast.  verpasst  abgegeben  Strom CHF  Break-even Case  DH Ergebnis/J  DH Break-even CHF/L4-h")
            for r in alle:
                if r["szenario"] == sz and r["regel_ueberschuss"] == regel:
                    print(f"{r['server_pro_haus']:2d}  {r['deckungsgrad']:6.1%}  {r['waerme_abgefuehrt_kwh']:7,d} kWh"
                          f"  {r['auslastung']:6.1%}  {r['verpasste_fristen_anteil']:7.2%}  {r['jobs_abgegeben']:7d}"
                          f"  {r['stromkosten_chf']:8,d}      {r['break_even_chf_pro_server_h']:.3f}"
                          f"     {r['dh_ergebnis_pro_jahr_chf']:9,d}     {r['dh_break_even_chf_karte_h']:.3f}")


if __name__ == "__main__":
    main()
