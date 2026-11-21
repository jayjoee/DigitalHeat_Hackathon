"""Leerlauf und Abschalten im Basler Referenzhaus vergleichen.

Aufruf: python3 -m src.scheduler.serverbetrieb --ausgabe daten/ergebnisse/serverbetrieb.json
"""
import argparse
from dataclasses import asdict, dataclass, replace
import json
import math
from pathlib import Path

from src.scheduler import annahmen as A
from src.scheduler.jahr import Haus, profil_laden
from src.scheduler.kern import Lage, entscheide, spaetester_start

LEERLAUF_WERTE = (100, 230, 350)


@dataclass(frozen=True)
class Leistungsprofil:
    leerlauf_watt: float
    standby_watt: float = 10.0
    start_minuten: float = 5.0
    nachlauf_h: int = 1
    speicher_ein: float = 0.35
    speicher_aus: float = 0.85

    def __post_init__(self):
        if not 0 <= self.standby_watt <= self.leerlauf_watt < A.wert("server_kw") * 1000:
            raise ValueError("Es gilt 0 ≤ Standby ≤ Leerlauf < Volllast (in Watt).")
        if not 0 <= self.start_minuten < 60:
            raise ValueError("Die Startzeit muss zwischen 0 und unter 60 Minuten liegen.")
        if self.nachlauf_h < 0 or not 0 <= self.speicher_ein < self.speicher_aus <= 1:
            raise ValueError("Nachlauf und Speicherschwellen sind ungültig.")


@dataclass(frozen=True)
class Betriebsstunde:
    lage: Lage
    laden: bool
    letzte_anforderung: tuple[int, ...]
    starts: int
    startstrom: float
    standbystrom: float
    leerlaufanteil: float


class HausMitServerbetrieb(Haus):
    def __init__(self, n_server, szenario, profil, leistung, *, abschalten, bei_ueberschuss="rechnen", **haus_optionen):
        super().__init__(n_server, szenario, bei_ueberschuss, profil, **haus_optionen)
        self.leistung = leistung
        self.abschalten = abschalten
        self.laden = False
        self.eingeschaltet = 0 if abschalten else n_server
        self.letzte_anforderung = (-leistung.nachlauf_h - 1,) * n_server
        self.z.update(rechenstrom=0.0, leerlaufstrom=0.0, standbystrom=0.0, startstrom=0.0,
                      serverstarts=0, server_h_aus=0)

    def waermeziel(self, lage):
        """Wärmeziel und Ladephase aus dem Speicherzustand am Stundenanfang."""
        if self.typ == "bad" and lage.bedarf_kwh <= 0:
            return 0.0, False
        if not self.abschalten:
            return lage.bedarf_kwh + self.smax - self.s, self.laden
        waermeziel = max(0.0, lage.bedarf_kwh - self.s)
        laden = self.laden
        if self.s <= self.smax * self.leistung.speicher_ein:
            laden = True
        elif self.s >= self.smax * self.leistung.speicher_aus:
            laden = False
        if laden:
            waermeziel = lage.bedarf_kwh + self.smax - self.s
        return waermeziel, laden

    def _serverbedarf(self, lage, jobs, waermeziel, laden):
        """Aktiviere Kapazität für das Wärmeziel und bekannte Pflichtjobs."""
        heizlast = waermeziel
        if laden:
            heizlast = min(waermeziel, max(lage.bedarf_kwh, self.eta * lage.server_kw))
        heizserver = math.ceil(heizlast / (self.eta * lage.server_kw)) if jobs else 0
        if self.regel == "abgeben" and heizserver:
            # Bei knapper Nachfrage höchstens so viel Kapazität starten, wie die Warteschlange nutzen kann.
            kapazitaeten = self._kapazitaeten(lage, min(heizserver, self.n))
            kapazitaet_gesamt = sum(kapazitaeten)
            arbeit = 0.0
            for j in jobs:
                arbeit += min(j.rest_kwh, lage.server_kw)
                if arbeit >= kapazitaet_gesamt:
                    break
            for i, kapazitaet in enumerate(kapazitaeten, 1):
                arbeit -= kapazitaet
                if arbeit <= 1e-9:
                    heizserver = i
                    break
        if heizserver >= self.n:
            return min(heizserver, self.n)

        pflicht = [j for j in jobs if spaetester_start(j, lage.server_kw) <= lage.stunde
                   and (self.regel != "abgeben" or waermeziel > 1e-9 or j.gelaufen_kwh > 0)]
        if not pflicht:
            return heizserver
        rechenlage = replace(lage, server_kapazitaeten_kwh=self._kapazitaeten(lage, self.n), rechenziel_kwh=0.0)
        plan = entscheide(rechenlage, pflicht)
        pflichtserver = self._belegte_server(plan)
        if len(plan.laeufe) < len(pflicht) and self.eingeschaltet < self.n:
            # Ein unteilbarer Job kann zu lang für die Startstunde sein.
            # Trotzdem Server einschalten, damit er in der nächsten Stunde bereit ist.
            bereit = replace(rechenlage, server_kapazitaeten_kwh=(lage.server_kw,) * self.n)
            pflichtserver = max(pflichtserver, self._belegte_server(entscheide(bereit, pflicht)))
        return max(heizserver, pflichtserver)

    @staticmethod
    def _belegte_server(entscheidung):
        return max((i for i, kwh in enumerate(entscheidung.server_belegt_kwh, 1) if kwh > 1e-9), default=0)

    def _kapazitaeten(self, lage, anzahl):
        warm = min(anzahl, self.eingeschaltet)
        kalt = anzahl - warm
        return (lage.server_kw,) * warm + (lage.server_kw * (1 - self.leistung.start_minuten / 60),) * kalt

    def betrieb_planen(self, lage, jobs):
        """Plane die Stunde ohne den Standortzustand zu verändern."""
        anzahl = self.n
        waermeziel, laden = self.waermeziel(lage)
        letzte = self.letzte_anforderung
        if self.abschalten:
            h = lage.stunde
            benoetigt = self._serverbedarf(lage, jobs, waermeziel, laden)
            letzte = (h,) * benoetigt + letzte[benoetigt:]
            anzahl = sum(h - zuletzt <= self.leistung.nachlauf_h for zuletzt in letzte)
            if self.typ == "bad" and lage.bedarf_kwh <= 0:
                anzahl = 0

        kapazitaeten = self._kapazitaeten(lage, anzahl)
        starts = max(0, anzahl - self.eingeschaltet)
        startstrom = starts * self.leistung.start_minuten / 60 * lage.server_kw
        standbystrom = (self.n - anzahl) * self.leistung.standby_watt / 1000
        leerlaufanteil = self.leistung.leerlauf_watt / (1000 * lage.server_kw)
        kapazitaet = sum(kapazitaeten)
        grundlast = startstrom + kapazitaet * leerlaufanteil
        # Rechnen ersetzt Leerlaufzeit. Standby-Strom liefert keine Wärme an den Wassertank.
        rechenziel = max(0.0, (waermeziel / self.eta - grundlast) / (1 - leerlaufanteil))
        plan = replace(lage, server_kapazitaeten_kwh=kapazitaeten, rechenziel_kwh=rechenziel)
        return Betriebsstunde(plan, laden, letzte, starts, startstrom, standbystrom, leerlaufanteil)

    def betrieb_verbuchen(self, h, e, betrieb):
        anzahl = len(betrieb.lage.server_kapazitaeten_kwh)
        kapazitaet = sum(betrieb.lage.server_kapazitaeten_kwh)
        startstrom, standbystrom = betrieb.startstrom, betrieb.standbystrom
        leerlaufstrom = max(0.0, kapazitaet - e.strom_kwh) * betrieb.leerlaufanteil
        zusatzwaerme = self.eta * (leerlaufstrom + startstrom)
        zustandsstrom = leerlaufstrom + startstrom + standbystrom

        self.eingeschaltet = anzahl
        self.laden = betrieb.laden
        self.letzte_anforderung = betrieb.letzte_anforderung
        self.z["rechenstrom"] += e.strom_kwh
        self.z["leerlaufstrom"] += leerlaufstrom
        self.z["standbystrom"] += standbystrom
        self.z["startstrom"] += startstrom
        self.z["serverstarts"] += betrieb.starts
        self.z["server_h_aus"] += self.n - anzahl
        zeile = self.verbuchen(h, e, zusatzstrom_kwh=zustandsstrom, zusatzwaerme_kwh=zusatzwaerme)
        return {**zeile, "server_eingeschaltet": anzahl, "server_standby": self.n - anzahl,
                "server_starts": betrieb.starts}

    def betrieb_entscheiden(self, betrieb, jobs):
        lage = betrieb.lage
        e = entscheide(lage, jobs, self.regel)
        if self.regel == "abgeben" and lage.rechenziel_kwh <= 1e-9:
            # Ein abgeschalteter Standort kann keine neuen Pflichtaufträge übernehmen.
            e.abgegeben = [j for j in jobs if j.gelaufen_kwh == 0
                           and spaetester_start(j, lage.server_kw) <= lage.stunde]
        return e

    def schritt(self, h):
        self.vorbereiten(h)
        betrieb = self.betrieb_planen(self.lage(h), self.q)
        e = self.betrieb_entscheiden(betrieb, self.q)
        self.fristen(h, e)
        return self.betrieb_verbuchen(h, e, betrieb)


def jahreswerte(haus, strategie, leistung=None):
    for h in range(len(haus.profil)):
        haus.schritt(h)
    bilanz = haus.bilanz()
    z = haus.z
    return {
        "strategie": strategie,
        "szenario": haus.szenario,
        "server_pro_haus": haus.n,
        "leistungsprofil": asdict(leistung) if leistung is not None else None,
        "strom_kwh": round(z["strom"], 1),
        "strom_nach_zustand_kwh": {
            "rechenstrom": round(z.get("rechenstrom", z["strom"]), 1),
            **{k: round(z.get(k, 0), 1) for k in ("leerlaufstrom", "standbystrom", "startstrom")},
        },
        "serverstarts": z.get("serverstarts", 0),
        "server_h_aus": z.get("server_h_aus", 0),
        "waerme_abgefuehrt_kwh": round(z["abgefuehrt"], 1),
        "jobs_frist_verpasst": z["verpasst"],
        **{k: bilanz[k] for k in (
            "deckungsgrad", "auslastung", "server_h", "jobs_mit_frist", "verpasste_fristen_anteil",
            "stromkosten_chf", "break_even_chf_pro_server_h")},
    }


def vergleich(leerlaufwerte=LEERLAUF_WERTE, standby_watt=10, start_minuten=5):
    """Gleiche Wetter- und Auftragsdaten für alle Varianten, inklusive ursprünglichem Case."""
    profil = profil_laden()
    ergebnisse = []
    for szenario in ("spot", "alibaba"):
        ergebnisse.append(jahreswerte(Haus(8, szenario, profil=profil), "case"))
        for watt in leerlaufwerte:
            leistung = Leistungsprofil(watt, standby_watt, start_minuten)
            for abschalten in (False, True):
                haus = HausMitServerbetrieb(8, szenario, profil, leistung, abschalten=abschalten)
                strategie = "abschalten" if abschalten else "pausieren"
                ergebnisse.append(jahreswerte(haus, strategie, leistung))
    return {
        "annahmen": {
            "leerlauf": "Standard: 100/350 W als Szenariogrenzen. 230 W: H100-Leerlaufquote aus ANNAHMEN_PRUEFUNG.md auf 1 kW übertragen.",
            "standby_und_startzeit": "Szenariowerte, keine Messungen an L4-Hardware.",
            "leistung_beim_start_watt": A.wert("server_kw") * 1000,
            "waermerueckgewinnung": "Case-Wirkungsgrad für Rechnen, Leerlauf und Start. Im Standby keine nutzbare Wärme.",
        },
        "ergebnisse": ergebnisse,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--leerlauf-watt", type=float, nargs="+", default=LEERLAUF_WERTE)
    parser.add_argument("--standby-watt", type=float, default=10)
    parser.add_argument("--start-minuten", type=float, default=5)
    parser.add_argument("--ausgabe", type=Path)
    args = parser.parse_args()
    try:
        for watt in args.leerlauf_watt:
            Leistungsprofil(watt, args.standby_watt, args.start_minuten)
    except ValueError as fehler:
        parser.error(str(fehler))
    daten = json.dumps(vergleich(args.leerlauf_watt, args.standby_watt, args.start_minuten),
                       indent=2, ensure_ascii=False)
    if args.ausgabe is None:
        print(daten)
    else:
        args.ausgabe.write_text(daten + "\n", encoding="utf-8")
        print(args.ausgabe)


if __name__ == "__main__":
    main()
