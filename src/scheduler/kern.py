"""Scheduler-Kern: entscheidet pro Stunde, welche Jobs wie viel rechnen.

Dieselbe Funktion `entscheide` steuert
- die Jahressimulation (src/scheduler/jahr.py) und
- den echten Prozess (src/scheduler/live.py).

Regel (wärmegeführt, mit Fristen):
1. Pflicht: Jobs, die sonst ihre Frist verpassen (spätester Start erreicht), laufen immer.
   Erzeugen sie Wärme, die niemand braucht, gilt die Regel `bei_ueberschuss`:
   "rechnen" (Wärme abführen) oder "abgeben" (Job an einen anderen Standort/Cloud, kein Erlös hier).
2. Wärme: Weitere Jobs laufen, bis Wärmebedarf der Stunde plus freier Platz im Speicher gedeckt ist.
   Reihenfolge: früheste Frist zuerst (EDF).
3. Was übrig bleibt, wartet. Pausierbare Jobs (Typ A) dürfen mitten in der Arbeit anhalten.
"""
from dataclasses import dataclass, field
import math


@dataclass
class Job:
    id: int
    typ: str                 # "A" oder "B"
    ankunft_h: int
    frist_h: float           # absolute Stunde, math.inf = keine Frist (Spot)
    rest_kwh: float
    unterbrechbar: bool
    gelaufen_kwh: float = 0.0


@dataclass
class Lage:
    stunde: int
    bedarf_kwh: float        # Wärmebedarf dieser Stunde (Heizung + Warmwasser)
    speicher_kwh: float
    speicher_max_kwh: float
    n_server: int
    server_kw: float = 1.0
    eta: float = 0.8         # nutzbarer Anteil der Wärme


@dataclass
class Entscheidung:
    laeufe: list = field(default_factory=list)      # (job, kWh in dieser Stunde)
    abgegeben: list = field(default_factory=list)   # Jobs, die an einen anderen Standort gehen
    strom_kwh: float = 0.0
    ziel_strom_kwh: float = 0.0


PUFFER_H = 2  # Pflichtlauf so viele Stunden vor dem spätesten Start, damit Spitzen nicht Fristen reissen


def spaetester_start(job, server_kw=1.0, puffer_h=PUFFER_H):
    """Stunde, ab der der Job laufen muss, um die Frist sicher zu halten (ein Server pro Job)."""
    if math.isinf(job.frist_h):
        return math.inf
    noetig = math.ceil(job.rest_kwh / server_kw - 1e-9)
    puffer = min(puffer_h, job.frist_h - job.ankunft_h - noetig)  # nie vor der Ankunft
    return job.frist_h - noetig - max(0, puffer)


def entscheide(lage: Lage, warteschlange: list, bei_ueberschuss="rechnen") -> Entscheidung:
    e = Entscheidung()
    kap = lage.n_server * lage.server_kw
    # Wärme, die diese Stunde sinnvoll ist: Bedarf plus freier Speicher
    ziel_waerme = lage.bedarf_kwh + (lage.speicher_max_kwh - lage.speicher_kwh)
    e.ziel_strom_kwh = min(kap, ziel_waerme / lage.eta)

    nach_frist = sorted(warteschlange, key=lambda j: (j.frist_h, j.ankunft_h, j.id))
    pflicht = [j for j in nach_frist if spaetester_start(j, lage.server_kw) <= lage.stunde]
    frei = [j for j in nach_frist if j not in pflicht]

    def menge(job):
        # pro Job höchstens ein Server; nicht unterbrechbare Jobs nur ganz
        return min(job.rest_kwh, lage.server_kw)

    belegt = 0.0
    for j in pflicht:
        m = menge(j)
        if belegt + m > kap + 1e-9:
            break  # Kapazität reicht nicht, Frist wird verpasst
        if bei_ueberschuss == "abgeben" and belegt + m > e.ziel_strom_kwh + 1e-9 and j.gelaufen_kwh == 0:
            e.abgegeben.append(j)
            continue
        e.laeufe.append((j, m))
        belegt += m

    for j in frei:
        rest_ziel = e.ziel_strom_kwh - belegt
        if rest_ziel <= 1e-9:
            break
        m = menge(j)
        if not j.unterbrechbar:
            if m > rest_ziel + 1e-9 or belegt + m > kap + 1e-9:
                continue  # passt nicht ganz hinein, später
        else:
            m = min(m, rest_ziel, kap - belegt)
        if m <= 1e-9:
            continue
        e.laeufe.append((j, m))
        belegt += m

    e.strom_kwh = belegt
    return e
