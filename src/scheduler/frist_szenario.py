"""Was eine lange Frist bringt: Docking-Kampagnen statt Aufträgen mit 24 Stunden Frist.

Ein virtuelles Screening (src/jobs/docking_job.py) ist wie Typ A lang und pausierbar, hat aber eine Frist von
Wochen bis Monaten (Screening-Kampagne, docs/kunden/PHARMA_SICHT.md). Je länger die Frist, desto eher kann
der Scheduler die Arbeit auf kalte Tage schieben. Gerechnet im Szenario «Nur Jobs mit Frist» (Alibaba-Trace),
Referenzhaus mit 8 Servern, Case-Modell; nur die Frist von Typ A ändert sich.

Aufruf: python3 src/scheduler/frist_szenario.py      # schreibt daten/ergebnisse/frist_szenario.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.scheduler import annahmen as A  # noqa: E402
from src.scheduler.jahr import profil_laden, simuliere  # noqa: E402

FRISTEN_H = (24, 168, 720, 2160)  # 1 Tag (Grundannahme), 1 Woche, 30 Tage, 90 Tage
AUS = A.ROOT / "daten" / "ergebnisse" / "frist_szenario.json"


def main():
    profil = profil_laden()
    alt = A.ANNAHMEN["job_a_frist_h"]
    zeilen = []
    try:
        for frist in FRISTEN_H:
            A.ANNAHMEN["job_a_frist_h"] = (frist, alt[1])
            for regel in ("rechnen", "abgeben"):
                r = simuliere(8, "alibaba", regel, profil=profil)
                zeilen.append({k: r[k] for k in ("deckungsgrad", "waerme_abgefuehrt_kwh", "abgegeben_server_h",
                                                 "verpasste_fristen_anteil", "auslastung", "dh_ergebnis_pro_jahr_chf")}
                              | {"frist_typ_a_h": frist, "regel_ueberschuss": regel})
                z = zeilen[-1]
                print(f"Frist {frist:5d} h  {regel:8s} Deckung {z['deckungsgrad']:.1%}  abgeführt "
                      f"{z['waerme_abgefuehrt_kwh']:6,} kWh  abgegeben {z['abgegeben_server_h']:7,.0f} h  "
                      f"Ergebnis {z['dh_ergebnis_pro_jahr_chf']:8,} CHF", flush=True)
    finally:
        A.ANNAHMEN["job_a_frist_h"] = alt
    AUS.write_text(json.dumps({"erzeugt": "python3 src/scheduler/frist_szenario.py",
                               "szenario": "alibaba, 8 Server, Case-Modell", "ergebnisse": zeilen},
                              indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(AUS.relative_to(A.ROOT))


if __name__ == "__main__":
    main()
