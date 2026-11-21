"""Wärme-Router: ein gemeinsamer Auftragspool für mehrere Standorte (Häuser und Sommer-Senken).

Der Router verteilt die Jobs. Standorte mit Serverbetrieb wählen zusätzlich ihre aktive Kapazität.
Design: docs/technik/waerme-router-basel.md, Baustein 3. Pro Stunde h:

  0. Pool: Ankünfte (Alibaba-Rate × Server der Häuser) und Spot-Nachschub für alle Server der Flotte.
  Vorrang (Team-Entscheid 21.11.2026): Wohnhäuser haben immer Vorrang vor Senken. Senken (Sportbad) nehmen
  nur die Rechenlast auf, die kein Haus als Wärme brauchen kann. Umsetzung: Häuser entscheiden zuerst,
  Pflichtjobs gehen zuerst an Häuser mit freiem Wärmeziel, und ein Haus darf einen angefangenen Job von
  einer Senke zurückholen (die Bindungsregel schützt nur Jobs an Häusern).

  a. Pflichtjobs (spätester Start erreicht, `kern.spaetester_start`) nach EDF verteilen:
     - ein angefangener Job geht zuerst an seinen bisherigen Standort, solange dort ein Server frei ist;
     - nicht unterbrechbare angefangene Jobs (Typ B) bleiben immer an ihrem Standort;
     - sonst an den Standort mit dem grössten freien Wärmeziel (Bedarf + freier Speicher − schon
       zugeteilte Pflichtarbeit), der noch einen freien Server hat.
     R3-11: Hat kein Standort mehr einen freien Server, geht der Pflichtjob trotzdem an den Standort mit
     dem grössten freien Wärmeziel. Der Kern entscheidet dort wie heute (Abbruch bei voller Kapazität oder
     `abgeben`); der Pool zählt den Ausgang genau einmal (fertig, abgegeben oder verpasst).
  b. Erst die Häuser, dann die Senken, jeweils nach freiem Wärmeziel absteigend: `kern.entscheide(lage, zugeteilte Pflichtjobs +
     noch freie Jobs)`. Was ein Standort nimmt, ist für die folgenden weg.
     R3-10 (Bindungsregel): Ein angefangener Job steht erst dann in der Liste eines anderen Standorts,
     wenn sein eigener Standort schon entschieden hat (und ihn nicht genommen hat).
  b2. Verwaiste angefangene Jobs (eigener Standort hat sie nicht genommen) bekommen danach die Standorte mit
     freiem Wärmeziel, in derselben Reihenfolge. Erst hier wandert ein Job (Migration).
  c. R3-15: Danach bucht der Pool Fortschritt, Abgaben und Fristen einmal (`jahr.fristen_buchen`, dieselbe
     Funktion und dieselbe Stelle wie in `Haus.schritt`), jeder Standort bucht nur seine Physik
     (`Haus.verbuchen`).

Migration: Läuft ein Job in h an Standort X und danach an Standort Y, zählt das als Migration. Am Ziel
kommen `migration_min / 60 × server_kw` kWh zur Restarbeit dazu (Checkpoint laden, Modell starten). Diese
Energie wird Wärme, aber nicht als verkaufte Server-Stunde gezählt.

Mit einem einzigen Standort ist jeder Kernaufruf identisch mit `Haus.schritt` (Regressionstest 1).
"""
import math
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.jahr import Haus, ankuenfte, bilanz as haus_bilanz, fristen_buchen  # noqa: E402
from src.scheduler.kern import Job, entscheide, spaetester_start  # noqa: E402
from src.scheduler.serverbetrieb import HausMitServerbetrieb  # noqa: E402


def _schluessel(j):
    return (j.frist_h, j.ankunft_h, j.id)


class Pool:
    """Gemeinsame Warteschlange der Flotte: Ankünfte, Spot-Nachschub, Job-Zähler."""

    def __init__(self, n_nachfrage, n_alle, szenario, saat=None):
        self.szenario, self.n_alle = szenario, n_alle
        self.mehrere_standorte = False
        self.plan, self.raten = ankuenfte(n_nachfrage, szenario, A.wert("zufallssaat") if saat is None else saat)
        self.q, self.nid = [], 0
        self.z = dict(verschobene_jobs=0, verschobene_jobstunden=0, verschobene_jobs_gestartet=0,
                      wartezeit_bis_start_h=0, verschobene_jobs_fertig=0,
                      verschobene_jobs_am_stueck_fertig=0, jobs=0, mit_frist=0, fertig=0, verpasst=0, abgegeben=0, abgegeben_kwh=0.0,
                      verpasst_kwh=0.0, pausierte_fortsetzungen=0, server_h_a=0.0, server_h_b=0.0, migrationen=0, migration_kwh=0.0)

    def _neuer_job(self, typ, h, frist):
        j = Job(self.nid, typ, h, frist, A.wert(f"job_{typ.lower()}_kwh"), typ == "A")
        j.standort = None
        self.nid += 1
        self.q.append(j)
        self.z["jobs"] += 1
        return j

    def vorbereiten(self, h):
        """Wie `Haus.vorbereiten`, aber für die ganze Flotte."""
        for typ in self.plan.get(h, []):
            self._neuer_job(typ, h, h + A.wert(f"job_{typ.lower()}_frist_h"))
            self.z["mit_frist"] += 1
        if self.szenario == "spot":
            kw = A.wert("server_kw")
            if self.mehrere_standorte:
                # Unbegrenzt A heisst: jeder Standort findet immer genug Arbeit. Angefangene Teil-Jobs sind an
                # ihren Standort gebunden, und jeder Standort kann einen frischen Job anbrechen, dessen Rest in
                # dieser Stunde für die anderen verloren ist. Darum frische Arbeit ≥ (Server + Standorte) × 1 kWh.
                frisch = sum(j.rest_kwh for j in self.q if j.typ == "A" and j.gelaufen_kwh == 0)
                while frisch < (self.n_alle + self.n_standorte) * kw - 1e-9:
                    frisch += self._neuer_job("A", h, math.inf).rest_kwh
                return
            vorrat = sum(min(j.rest_kwh, kw) for j in self.q if j.typ == "A")
            while vorrat < self.n_alle * kw - 1e-9:
                vorrat += min(self._neuer_job("A", h, math.inf).rest_kwh, kw)


class Flotte:
    """Mehrere Standorte (`jahr.Haus` ohne eigene Ankünfte) an einem Pool.

    `standorte`: Liste von Haus-Objekten (mit_ankuenften=False). `nachfrage_server`: Serverzahl, nach der die
    Alibaba-Ankünfte skaliert werden (Standard: Server der Standorte vom Typ «haus»).
    """

    def __init__(self, standorte, szenario="spot", bei_ueberschuss="rechnen", nachfrage_server=None,
                 migration_min=None, saat=None, prognose=None):
        self.st, self.szenario, self.regel = standorte, szenario, bei_ueberschuss
        n_haus = sum(s.n for s in standorte if s.typ == "haus")
        self.n_alle = sum(s.n for s in standorte)
        self.pool = Pool(n_haus if nachfrage_server is None else nachfrage_server, self.n_alle, szenario, saat)
        self.pool.mehrere_standorte = len(standorte) > 1
        self.pool.n_standorte = len(standorte)
        self.kw = A.wert("server_kw")
        mm = A.wert("migration_min") if migration_min is None else migration_min
        self.migration_kwh = mm / 60 * self.kw
        self.mig_st = [0.0] * len(standorte)       # Migrationsenergie pro Zielstandort
        self.profil = standorte[0].profil         # Zeitachse (für zusage.py)
        self.vorausschau = None
        if prognose is not None:
            from src.scheduler.vorausschau import Vorausschau
            if [p["zeit"] for p in prognose] != [p["zeit"] for p in self.profil]:
                raise ValueError("Zeitachsen von Vorausschau und Flotte stimmen nicht überein")
            self.vorausschau = Vorausschau(prognose, self.pool.raten,
                                           n_haus if nachfrage_server is None else nachfrage_server)

    # --- eine Stunde -------------------------------------------------------------------------------
    def schritt(self, h):
        pool, kw, st = self.pool, self.kw, self.st
        pool.vorbereiten(h)
        q = sorted(pool.q, key=_schluessel)
        if self.vorausschau is not None:
            warten = self.vorausschau.zurueckhalten(h, st, q, kw)
            pool.z["verschobene_jobstunden"] += len(warten)
            for j in q:
                if j.id in warten and j.erstmals_verschoben_h is None:
                    j.erstmals_verschoben_h = h
                    pool.z["verschobene_jobs"] += 1
            q = [j for j in q if j.id not in warten]
        lagen = [s.lage(h) for s in st]
        haus = [s.typ == "haus" for s in st]
        leistung = [isinstance(s, HausMitServerbetrieb) for s in st]
        offen = [i for i, l in enumerate(lagen) if haus[i] or not leistung[i] or l.bedarf_kwh > 0]
        ziel = [min(l.n_server * l.server_kw, (s.waermeziel(l)[0] if leistung[i] else
                    l.bedarf_kwh + l.speicher_max_kwh - l.speicher_kwh) / l.eta)
                for i, (s, l) in enumerate(zip(st, lagen))]

        # a) Pflichtjobs verteilen
        pflicht = [j for j in q if spaetester_start(j, kw) <= h]
        pflicht_ids = {j.id for j in pflicht}
        zu = [[] for _ in st]
        zu_kwh = [0.0] * len(st)
        zu_n = [0] * len(st)
        for j in pflicht:
            frei = [i for i in offen if zu_n[i] < st[i].n]
            alt = j.standort
            haus_frei = [k for k in frei if haus[k] and ziel[k] - zu_kwh[k] > 1e-9]
            if alt is not None and not j.unterbrechbar:
                i = alt
            elif alt is not None and alt in frei and (haus[alt] or not haus_frei):
                i = alt  # Bindung; ein Job an der Senke bleibt nur, wenn kein Haus Wärme braucht (Vorrang)
            else:
                kandidaten = haus_frei or frei or offen or list(range(len(st)))
                i = max(kandidaten, key=lambda k: (ziel[k] - zu_kwh[k], -k))
            zu[i].append(j)
            zu_kwh[i] += min(j.rest_kwh, kw)
            zu_n[i] += 1

        # b) Häuser vor Senken, jeweils nach freiem Wärmeziel absteigend
        # Vorrang der Wohnhäuser: erst alle Häuser, dann die Senken (jeweils nach freiem Wärmeziel)
        reihenfolge = sorted(range(len(st)), key=lambda k: (not haus[k], -(ziel[k] - zu_kwh[k]), k))
        genommen, entschieden = set(), set()
        entscheidungen = [None] * len(st)
        betriebsplaene = [None] * len(st)
        alle_laeufe, alle_abgegeben = [], []
        for i in reihenfolge:
            kap = st[i].n * kw
            liste = list(zu[i])
            vorrat = 0.0
            for j in q if not leistung[i] or ziel[i] > 1e-9 else ():
                if vorrat >= kap - 1e-9:
                    break  # mehr freie Jobs kann der Kern in dieser Stunde nicht nehmen (siehe Docstring Test)
                if j.id in pflicht_ids or j.id in genommen:
                    continue
                if j.standort is not None and j.standort != i:
                    vorrang = haus[i] and not haus[j.standort]  # Haus holt Arbeit von der Senke zurück
                    if not j.unterbrechbar or (j.standort not in entschieden and not vorrang):
                        continue  # Bindungsregel (R3-10)
                liste.append(j)
                if j.unterbrechbar:
                    vorrat += min(j.rest_kwh, kw)
            if leistung[i]:
                betrieb = st[i].betrieb_planen(lagen[i], liste)
                betriebsplaene[i] = betrieb
                e = st[i].betrieb_entscheiden(betrieb, liste)
            else:
                e = entscheide(lagen[i], liste, self.regel)
            for j in e.abgegeben:
                genommen.add(j.id)
            for j, m in e.laeufe:
                genommen.add(j.id)
            entscheidungen[i] = e
            entschieden.add(i)

        # b2) Verwaiste angefangene Jobs: Ihr Standort hat entschieden und sie nicht genommen. Standorte mit
        #     freiem Wärmeziel bekommen sie in derselben Reihenfolge (Kern mit dem Rest von Ziel und Kapazität).
        #     Bei einem einzigen Standort gibt es keine solchen Jobs; der Lauf ist dann identisch mit heute.
        if len(st) > 1:
            waisen = [j for j in q if j.standort is not None and j.unterbrechbar
                      and j.id not in genommen and j.id not in pflicht_ids]
            for i in reihenfolge:
                waisen = [j for j in waisen if j.id not in genommen and (leistung[i] or j.standort != i)]
                if not waisen:
                    break
                e, l = entscheidungen[i], lagen[i]
                rest_ziel = e.ziel_strom_kwh - e.strom_kwh
                if rest_ziel <= 1e-9:
                    continue
                if leistung[i]:
                    kapazitaeten = betriebsplaene[i].lage.server_kapazitaeten_kwh
                    rest = tuple(max(0.0, k - b) for k, b in zip(kapazitaeten, e.server_belegt_kwh))
                    l2 = replace(l, server_kapazitaeten_kwh=rest, rechenziel_kwh=rest_ziel)
                    kandidaten = [j for j in waisen if j.standort != i]
                else:
                    rest_kap = l.n_server * kw - e.strom_kwh
                    if rest_kap <= 1e-9:
                        continue
                    l2 = replace(l, bedarf_kwh=l.bedarf_kwh - e.strom_kwh * l.eta, n_server=rest_kap / kw)
                    kandidaten = waisen
                e2 = entscheide(l2, kandidaten, self.regel)
                e.laeufe += e2.laeufe
                e.strom_kwh += e2.strom_kwh
                for j, m in e2.laeufe:
                    genommen.add(j.id)

        self.zuteilung = {}  # Job-ID → (Standort, kWh) dieser Stunde, für live.py
        migrationsstrom = 0.0
        for i in reihenfolge:
            e = entscheidungen[i]
            for j, m in e.laeufe:
                self.zuteilung[j.id] = (i, m)
                if j.standort is not None and j.standort != i:
                    pool.z["migrationen"] += 1
                    pool.z["migration_kwh"] += self.migration_kwh
                    self.mig_st[i] += self.migration_kwh
                    migrationsstrom += self.migration_kwh
                    j.rest_kwh += self.migration_kwh
                if j.letzter_lauf_h is not None and j.letzter_lauf_h < h - 1:
                    pool.z["pausierte_fortsetzungen"] += 1
                    j.pausiert = True
                if j.erstmals_verschoben_h is not None and j.letzter_lauf_h is None:
                    pool.z["verschobene_jobs_gestartet"] += 1
                    pool.z["wartezeit_bis_start_h"] += h - j.erstmals_verschoben_h
                j.letzter_lauf_h = h
                j.standort = i
            alle_laeufe += e.laeufe
            alle_abgegeben += e.abgegeben

        # c) einmal buchen: Pool (Jobs, Fristen), Standorte (Physik)
        ids = [j.id for j, _ in alle_laeufe] + [j.id for j in alle_abgegeben]
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"Stunde {h}: ein Job wurde mehrfach zugeteilt")
        fristen_buchen(pool.q, pool.z, h, alle_abgegeben, alle_laeufe)
        for j, _ in alle_laeufe:
            if j.erstmals_verschoben_h is not None and j.rest_kwh <= 1e-9:
                pool.z["verschobene_jobs_fertig"] += 1
                pool.z["verschobene_jobs_am_stueck_fertig"] += int(not j.pausiert)

        zeilen = [
            s.betrieb_verbuchen(h, e, betrieb) if betrieb is not None else s.verbuchen(h, e)
            for s, e, betrieb in zip(st, entscheidungen, betriebsplaene)
        ]

        rechenstunden = sum(e.strom_kwh for e in entscheidungen) / kw if any(leistung) else sum(
            z["server_laufend"] for z in zeilen
        )

        betriebsdaten = {}
        if any(leistung):
            # Für Kapazitätszusagen zählt nur die Arbeit, die Kunden in dieser Stunde erhalten.
            betriebsdaten["server_h_lieferbar"] = max(0.0, rechenstunden - migrationsstrom / kw)
        return {"zeit": zeilen[0]["zeit"], "stunde": h,
                "server_laufend": round(rechenstunden, 3),
                "abgefuehrt_kwh": round(sum(z["abgefuehrt_kwh"] for z in zeilen), 3),
                "warteschlange": len(pool.q), "standorte": zeilen, **betriebsdaten}

    def markierter_job(self, standort=0):
        """Ein Demo-Job im Pool (live.py): unbegrenzter Typ A ohne Frist, angefangen an `standort`."""
        j = self.pool._neuer_job("A", 0, math.inf)
        j.rest_kwh = 1e9
        j.standort = standort
        return j

    def kopie(self, prognose=None):
        """Unabhängige Kopie (Pool-Jobs, Speicher, Zähler) für den Trockenlauf der Zusage.

        `prognose`: Liste von Profilen pro Standort (None = eigenes Profil behalten, z. B. Senken ohne
        Wetterprognose) oder ein einzelnes Profil für alle Häuser.
        """
        import copy
        k = copy.copy(self)
        k.pool = copy.copy(self.pool)
        k.pool.q = [copy.copy(j) for j in self.pool.q]
        k.pool.z = dict(self.pool.z)
        k.mig_st = list(self.mig_st)
        if prognose is not None and not isinstance(prognose[0], list):
            prognose = [prognose if s.typ == "haus" else None for s in self.st]
        k.st = [s.kopie(None if prognose is None else prognose[i]) for i, s in enumerate(self.st)]
        return k

    def simuliere(self, monatlich=True):
        monate = {}
        for h in range(len(self.profil)):
            abg_vorher = self.pool.z["abgegeben_kwh"]
            r = self.schritt(h)
            if monatlich:
                m = monate.setdefault(r["zeit"][:7], {"stunden": 0, "haus_server_h": 0.0, "senke_server_h": 0.0,
                                                      "abgegeben_server_h": 0.0, "abgefuehrt_kwh": 0.0,
                                                      "haus_bedarf_kwh": 0.0, "haus_genutzt_kwh": 0.0})
                m["stunden"] += 1
                m["abgefuehrt_kwh"] += r["abgefuehrt_kwh"]
                m["abgegeben_server_h"] += (self.pool.z["abgegeben_kwh"] - abg_vorher) / self.kw
                for s, z in zip(self.st, r["standorte"]):
                    if s.typ == "haus":
                        m["haus_bedarf_kwh"] += z["bedarf_kwh"]
                        m["haus_genutzt_kwh"] += z["genutzt_kwh"]
                for s, z in zip(self.st, r["standorte"]):
                    m["haus_server_h" if s.typ == "haus" else "senke_server_h"] += z["server_laufend"]
                    if "server_eingeschaltet" in z:
                        m["strom_kwh"] = m.get("strom_kwh", 0.0) + z["strom_kwh"]
                        k = "haus_eingeschaltet_h" if s.typ == "haus" else "bad_eingeschaltet_h"
                        m[k] = m.get(k, 0) + z["server_eingeschaltet"]
        self.monate = monate
        return self.bilanz()

    # --- Bilanz -----------------------------------------------------------------------------------
    def bilanz_standort(self, i):
        """Bilanz eines Standorts im Format von `jahr.bilanz` (Job-Zähler: Anteil des Pools nach Server-h).

        Bei einem einzigen Standort sind das genau die Zahlen von `jahr.simuliere` (Regressionstest 1).
        """
        s = self.st[i]
        z = dict(s.z)
        if len(self.st) == 1:
            for k in ("jobs", "mit_frist", "fertig", "verpasst", "abgegeben", "abgegeben_kwh", "verpasst_kwh",
                      "server_h_a", "server_h_b"):
                z[k] = self.pool.z[k]
        else:
            z.update(jobs=0, mit_frist=0, fertig=0, verpasst=0, abgegeben=0, abgegeben_kwh=0.0,
                     verpasst_kwh=0.0, server_h_a=z["strom"] / self.kw, server_h_b=0.0)
        return z

    def bilanz(self, anteil_fest_gebucht=None, fehlmenge_server_h=0.0, kosten=None):
        """Flottenbilanz. Wirtschaft pro Standort, dann summiert.

        R3-5: Der fest gebuchte Anteil gilt für alle Standorte gleich (Flottenanteil).
        R3-4: Die Fehlmenge wird anteilig nach den verkauften Server-h der Standorte verteilt.
        `kosten`: {Standortname: {Parameter: Wert}} für eigene Kosten (z. B. Senke ohne neuen Speicher).
        """
        from src.wirtschaft import rechne
        kosten = kosten or {}
        gerechnet = [s.z.get("rechenstrom", s.z["strom"]) / self.kw for s in self.st]
        verkauft = [max(0.0, h - self.mig_st[i]) for i, h in enumerate(gerechnet)]
        total_verkauft = sum(verkauft) or 1.0
        standorte, ergebnis, investition = [], 0, 0
        gruppen = {}
        for i, s in enumerate(self.st):
            ueber = dict(kosten.get(s.name, {}))
            if anteil_fest_gebucht is not None:
                ueber["anteil_fest_gebucht"] = anteil_fest_gebucht
            if "rechenstrom" in s.z:
                ueber["strom_kwh"] = s.z["strom"]
            w = rechne(s.n, verkauft[i], s.z["genutzt"], fehlmenge_server_h * verkauft[i] / total_verkauft,
                       **ueber)
            ergebnis += w["ergebnis_pro_jahr_chf"]
            investition += w["investition_chf"]
            g = gruppen.setdefault(s.typ, dict(server=0, server_h=0.0, bedarf=0.0, genutzt=0.0, abgefuehrt=0.0,
                                               backup=0.0, ergebnis=0, standorte=0))
            for k, v in (("server", s.n), ("server_h", gerechnet[i]), ("bedarf", s.z["bedarf"]),
                         ("genutzt", s.z["genutzt"]), ("abgefuehrt", s.z["abgefuehrt"]), ("backup", s.z["backup"]),
                         ("ergebnis", w["ergebnis_pro_jahr_chf"]), ("standorte", 1)):
                g[k] += v
            standorte.append({"name": s.name, "typ": s.typ, "server": s.n,
                              "deckungsgrad": round(s.z["genutzt"] / s.z["bedarf"], 4) if s.z["bedarf"] else None,
                              "auslastung": round(gerechnet[i] / (s.n * len(s.profil)), 4),
                              "abgefuehrt_kwh": round(s.z["abgefuehrt"]),
                              "ergebnis_pro_jahr_chf": w["ergebnis_pro_jahr_chf"]})
        stunden = len(self.profil)
        pz = self.pool.z
        ergebnis_bilanz = {
            "szenario": self.szenario, "regel_ueberschuss": self.regel, "standorte_anzahl": len(self.st),
            "server": self.n_alle,
            "gruppen": {k: {"standorte": g["standorte"], "server": g["server"],
                            "deckungsgrad": round(g["genutzt"] / g["bedarf"], 4) if g["bedarf"] else None,
                            "auslastung": round(g["server_h"] / (g["server"] * stunden), 4),
                            "server_h": round(g["server_h"]), "waerme_genutzt_kwh": round(g["genutzt"]),
                            "waerme_abgefuehrt_kwh": round(g["abgefuehrt"]), "backup_kwh": round(g["backup"]),
                            "ergebnis_pro_jahr_chf": g["ergebnis"]} for k, g in gruppen.items()},
            "auslastung": round(sum(gerechnet) / (self.n_alle * stunden), 4),
            "server_h_verkauft": round(sum(verkauft)),
            "waerme_abgefuehrt_kwh": round(sum(s.z["abgefuehrt"] for s in self.st)),
            "jobs_mit_frist": pz["mit_frist"], "jobs_fertig": pz["fertig"],
            "verpasste_fristen_anteil": round(pz["verpasst"] / pz["mit_frist"], 4) if pz["mit_frist"] else 0,
            "jobs_abgegeben": pz["abgegeben"], "abgegeben_server_h": round(pz["abgegeben_kwh"], 1),
            "migrationen": pz["migrationen"], "migration_kwh": round(pz["migration_kwh"], 1),
            "dh_investition_chf": investition, "dh_ergebnis_pro_jahr_chf": ergebnis,
            "ergebnis_pro_investiertem_franken": round(ergebnis / investition, 4) if investition else None,
            "ankuenfte": self.pool.raten, "standorte": standorte,
        }
        if all("rechenstrom" in s.z for s in self.st):
            for typ, gruppe in ergebnis_bilanz["gruppen"].items():
                zustaende = [s.z for s in self.st if s.typ == typ]
                gruppe.update({k: round(sum(z[k] for z in zustaende), 2) for k in
                               ("strom", "rechenstrom", "leerlaufstrom", "standbystrom", "startstrom",
                                "serverstarts", "server_h_aus")})
            ergebnis_bilanz.update(strom_kwh=round(sum(s.z["strom"] for s in self.st), 2),
                                  jobs_frist_verpasst=pz["verpasst"])
        return ergebnis_bilanz

    def bilanz_wie_haus(self):
        """Nur für einen Standort: Bilanz exakt im Format von `jahr.simuliere` (Regressionstest 1)."""
        assert len(self.st) == 1
        s = self.st[0]
        return haus_bilanz(s.n, self.szenario, self.regel, self.bilanz_standort(0), self.pool.raten)


def flotte_aus(standorte, szenario="spot", bei_ueberschuss="rechnen", **kw):
    for s in standorte:
        if not isinstance(s, Haus):
            raise TypeError("Standorte sind jahr.Haus-Objekte")
    return Flotte(standorte, szenario, bei_ueberschuss, **kw)
