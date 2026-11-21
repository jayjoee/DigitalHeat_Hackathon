"""Was der Haushalt spart: heutige Heizkosten gegenüber Gratiswärme aus den Servern.

Annahmen mit Quelle stehen unten in P (Herkunft: Kundensicht von Joël, docs/kunden/HAUSBESITZER.md).
Die Deckung kommt aus der Jahressimulation (daten/ergebnisse/kosten_dh.json, Abschaltmodell und Idealmodell).
Die Restwärme liefert der vorhandene Holzofen; das Brennholz ist nicht eingerechnet.

Aufruf: python3 src/haushalt.py        # schreibt daten/ergebnisse/haushalt.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.scheduler import annahmen as A  # noqa: E402

AUS = ROOT / "daten" / "ergebnisse" / "haushalt.json"

P = {  # Wert, Quelle
    "oel_chf_l": (1.665, "Heizöl 3'000 l, Anfang Nov. 2026 (weekend.at)"),
    "oel_kwh_l": (10.0, "Heizwert Heizöl EL, Standardwert"),
    "oel_kessel": (0.85, "Annahme: älterer Ölkessel"),
    "oel_co2_kg_l": (2.65, "gängiger Emissionsfaktor Heizöl EL"),
    "gas_rp_kwh": (11.57 + 2.333 + 0.11, "IWB Gastarife 2026, Stufe M, Arbeitspreis + CO2-Abgabe + Konzessionsabgabe, inkl. MwSt."),
    "gas_grundgebuehr_chf": (194.58, "IWB 2026, Leistungspreis, Minimum; entfällt, wenn der Gasanschluss aufgegeben wird"),
    "gas_kessel": (0.90, "Annahme: Gaskessel"),
    "gas_co2_kg_kwh": (0.198, "gängiger Emissionsfaktor Erdgas"),
    "wp_jaz": (2.5, "Case: Wärme ersetzt Wärmepumpe mit JAZ 2,5"),
}
W = {k: v[0] for k, v in P.items()}


def waermepreise_rp():
    """Was 1 kWh Wärme heute kostet, in Rappen."""
    return {"oel": 100 * W["oel_chf_l"] / (W["oel_kwh_l"] * W["oel_kessel"]),
            "gas": W["gas_rp_kwh"] / W["gas_kessel"],
            "waermepumpe": 100 * A.wert("strompreis_chf_kwh") / W["wp_jaz"]}


def haus(bedarf_kwh, deckung, waermepreis_rp=0.0):
    preise = waermepreise_rp()
    vom_server = bedarf_kwh * deckung
    spart = {k: vom_server * (p - waermepreis_rp) / 100 for k, p in preise.items()}
    spart["gas"] += W["gas_grundgebuehr_chf"]  # Holzofen statt Gaskessel: Anschluss wird aufgegeben
    heute = {k: bedarf_kwh * p / 100 for k, p in preise.items()}
    heute["gas"] += W["gas_grundgebuehr_chf"]
    return {
        "bedarf_kwh": round(bedarf_kwh), "deckung": round(deckung, 4), "vom_server_kwh": round(vom_server),
        "holzofen_kwh": round(bedarf_kwh - vom_server),
        "heute_chf": {k: round(v) for k, v in heute.items()},
        "spart_chf": {k: round(v) for k, v in spart.items()},
        "heizoel_l_heute": round(bedarf_kwh / (W["oel_kwh_l"] * W["oel_kessel"])),
        "co2_t_heute": {"oel": round(bedarf_kwh / (W["oel_kwh_l"] * W["oel_kessel"]) * W["oel_co2_kg_l"] / 1000, 1),
                        "gas": round(bedarf_kwh / W["gas_kessel"] * W["gas_co2_kg_kwh"] / 1000, 1)},
    }


def main():
    k = json.loads((ROOT / "daten" / "ergebnisse" / "kosten_dh.json").read_text(encoding="utf-8"))
    bedarf = {"referenzhaus": 31231, "efh": 17000}  # Case-Referenzhaus; Durchschnitts-EFH (Annahme, siehe HAUSBESITZER.md)
    deckung = {"referenzhaus": (k["referenzhaus"]["deckung"], k["idealmodell"]["referenzhaus"]["deckung"]),
               "efh": (k["efh_5"]["deckung"], k["idealmodell"]["efh_5"]["deckung"])}
    daten = {
        "erzeugt": "python3 src/haushalt.py",
        "annahmen": {k2: {"wert": v[0], "quelle": v[1]} for k2, v in P.items()},
        "waermepreis_heute_rp_kwh": {k2: round(v, 1) for k2, v in waermepreise_rp().items()},
        "realistisch": {h: haus(bedarf[h], deckung[h][0]) for h in bedarf},
        "idealmodell": {h: haus(bedarf[h], deckung[h][1]) for h in bedarf},
        "waermeabo_efh": {str(rp): haus(bedarf["efh"], deckung["efh"][0], rp)["spart_chf"] for rp in (0, 3, 5, 7, 10)},
    }
    AUS.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    e = daten["realistisch"]["efh"]
    print(f"EFH 17'000 kWh: spart {e['spart_chf']['oel']:,} CHF gegenüber Öl, Deckung {e['deckung']:.1%} "
          f"→ {AUS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
