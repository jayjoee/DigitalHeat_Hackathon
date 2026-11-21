"""Rollierende Wärmeplanung mit dem archivierten ECMWF-Profil und Alibaba-Tagesmuster."""
import math

from src.scheduler import annahmen as A
from src.scheduler.kern import spaetester_start


class Vorausschau:
    def __init__(self, prognose, raten, nachfrage_server):
        self.prognose = prognose
        form = A.stundenprofil()
        arbeit_tag = sum((raten[f"jobs_{typ}_pro_tag"] or 0) * A.wert(f"job_{typ}_kwh")
                         for typ in ("a", "b"))
        self.last_pro_server = [arbeit_tag * anteil / max(1, nachfrage_server) for anteil in form]

    def zurueckhalten(self, h, standorte, jobs, kw):
        """Frische A-Jobs auf prognostizierte zusammenhängende Wärmeslots verschieben.

        Freie Slots werden innerhalb der Entscheidung nur einmal vergeben. Die Planung
        wird stündlich neu gerechnet. Pflichtlauf und laufende Jobs behalten Vorrang.
        """
        ende = min(h + 25, len(self.prognose))
        lagen = [s.lage(h) for s in standorte]
        if any(l.bedarf_kwh > l.speicher_kwh + 1e-9 for l in lagen):
            return set()  # der aktuelle Bedarf hat Vorrang
        heute = max(min(s.n * kw, (l.bedarf_kwh + s.smax - s.s) / s.eta)
                    for s, l in zip(standorte, lagen))
        frei = []
        for s in standorte:
            kapazitaet = []
            for t in range(h + 1, ende):
                p = self.prognose[t] if s.typ == "haus" else s.profil[t]
                erwartet = self.last_pro_server[t % 24] * s.n if s.typ == "haus" else 0
                kapazitaet.append(max(0, min(s.n * kw, (p["heizung"] + p["ww"]) / s.eta) - erwartet))
            frei.append(kapazitaet)

        warten = set()
        for job in jobs:
            if not job.unterbrechbar or job.gelaufen_kwh or math.isinf(job.frist_h):
                continue
            dauer = math.ceil(job.rest_kwh / kw - 1e-9)
            arbeit = [min(kw, job.rest_kwh - i * kw) for i in range(dauer)]
            if arbeit[0] <= heute + 1e-9:
                continue  # ein voller erster Abschnitt passt bereits heute
            # Der reservierte Lauf soll vor der bisherigen Pflichtphase enden.
            grenze = min(ende, spaetester_start(job, kw)) - h - 1
            for slots in frei:
                start = next((i for i in range(grenze - dauer + 1)
                              if all(slots[i + j] + 1e-9 >= m for j, m in enumerate(arbeit))), None)
                if start is not None:
                    for j, m in enumerate(arbeit):
                        slots[start + j] -= m
                    warten.add(job.id)
                    break
        return warten
