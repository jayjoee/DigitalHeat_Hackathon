"""Wirtschaftlichkeit aus Sicht DigitalHeat: Gewinn pro Haus über die Lebensdauer der Hardware.

Eine Quelle für alle Zahlen in KOSTEN_DH.md, ERGEBNISSE.md und im Dashboard. Das Dashboard
rechnet dieselbe Formel in JavaScript nach (dashboard/index.html, Funktion `wirtschaft`).

Formel pro Jahr t = 1..J:
  Erlös     = Server-h × Karten × (1 − Plattform) × Verfügbarkeit
              × [fest gebucht × Vertragspreis + Rest × Spot-Preis × (1 − Preisverfall)^(t−1)]
  Wärme     = genutzte Wärme × Wärmepreis an den Haushalt
  Strom     = gesamter Stromverbrauch × Strompreis
  Fehlmenge = Fehlmenge Server-h × Karten × Vertragspreis × SLA-Gutschrift × (1 + Kostensteigerung)^(t−1)
              (Day-ahead-Zusage nicht geliefert, src/scheduler/zusage.py; Standard 0)
  Laufend   = (Ersatzteile + Einsätze + Service + Monitoring + Internet + Versicherung + Lizenz
               + Firmenanteil) × (1 + Kostensteigerung)^(t−1)
  Steuer    = max(0, Erlös + Wärme − Strom − Laufend − Fehlmenge − Abschreibung) × Steuersatz
  Cashflow  = Erlös + Wärme − Strom − Laufend − Fehlmenge − Steuer (+ Restwert im letzten Jahr)
Ergebnis pro Jahr = (−Investition + Barwert der Cashflows) × Annuitätenfaktor (Zins, J)

Aufruf: python3 src/wirtschaft.py            # Referenzhaus 8 Server, Break-even
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheduler import annahmen as A  # noqa: E402


def parameter(**ueberschreiben):
    p = {k: A.wert(k) for k in (
        "karten_pro_server", "server_preis_chf", "kuehlung_chf_pro_kw", "einbau_chf", "speicher_chf",
        "netzwerk_chf", "abschreibung_jahre", "restwert_anteil", "zins", "vertragspreis_chf_karte_h",
        "anteil_fest_gebucht", "spotpreis_chf_karte_h", "spot_preisverfall", "plattform_anteil",
        "verfuegbarkeit", "waermepreis_haushalt_chf_kwh", "gpu_preis_chf", "gpu_ausfall", "host_reparatur",
        "einsaetze_chf_pro_8_server", "service_hydraulik_chf", "kuehlservice_chf_pro_kw",
        "monitoring_chf_pro_server_monat", "internet_chf", "versicherung_anteil", "lizenz_chf",
        "firmenanteil_chf", "kostensteigerung", "gewinnsteuer", "strompreis_chf_kwh",
        "server_kw", "sla_gutschrift_anteil")}
    p.update(ueberschreiben)
    return p


def rechne(n_server, server_h, waerme_kwh, fehlmenge_server_h=0.0, *, strom_kwh=None, **ueberschreiben):
    """Gibt Kennzahlen und die Jahre einzeln zurück (alles in CHF).

    `fehlmenge_server_h`: zugesagte, aber nicht gelieferte Server-h pro Jahr (Day-ahead-Zusage).
    `strom_kwh`: Gesamtverbrauch. Ohne Angabe ergibt er sich aus Rechenstunden × Serverleistung.
    """
    p = parameter(**ueberschreiben)
    J, i = p["abschreibung_jahre"], p["zins"]
    hardware = n_server * p["server_preis_chf"]
    investition = (hardware + n_server * p["server_kw"] * p["kuehlung_chf_pro_kw"]
                   + p["einbau_chf"] + p["speicher_chf"] + p["netzwerk_chf"])
    restwert = hardware * p["restwert_anteil"]
    abschreibung = (investition - restwert) / J
    stromverbrauch = server_h * p["server_kw"] if strom_kwh is None else strom_kwh
    strom = stromverbrauch * p["strompreis_chf_kwh"]
    barwert, jahre = -investition, []
    for t in range(1, J + 1):
        preis = (p["anteil_fest_gebucht"] * p["vertragspreis_chf_karte_h"]
                 + (1 - p["anteil_fest_gebucht"]) * p["spotpreis_chf_karte_h"] * (1 - p["spot_preisverfall"]) ** (t - 1))
        erloes = (server_h * p["karten_pro_server"] * (1 - p["plattform_anteil"])
                  * p["verfuegbarkeit"] * preis)
        waerme = waerme_kwh * p["waermepreis_haushalt_chf_kwh"]
        e = (1 + p["kostensteigerung"]) ** (t - 1)
        teile = {
            "gpu_ersatz": (n_server * p["karten_pro_server"] * p["gpu_ausfall"] * p["gpu_preis_chf"]) if t > 3 else 0,
            "host_reparatur": (p["host_reparatur"] * hardware * 0.35) if t > 1 else 0,
            "einsaetze": p["einsaetze_chf_pro_8_server"] * n_server / 8,
            "service": n_server * p["server_kw"] * p["kuehlservice_chf_pro_kw"] + p["service_hydraulik_chf"],
            "monitoring": p["monitoring_chf_pro_server_monat"] * 12 * n_server,
            "internet": p["internet_chf"],
            "versicherung": hardware * p["versicherung_anteil"] * 1.05,
            "lizenz": p["lizenz_chf"],
            "firmenanteil": p["firmenanteil_chf"],
        }
        laufend = sum(teile.values()) * e
        fehlmenge = (fehlmenge_server_h * p["karten_pro_server"] * p["vertragspreis_chf_karte_h"]
                     * p["sla_gutschrift_anteil"] * e)
        vor_steuer = erloes + waerme - strom - laufend - fehlmenge - abschreibung
        steuer = max(0.0, vor_steuer) * p["gewinnsteuer"]
        cashflow = erloes + waerme - strom - laufend - fehlmenge - steuer + (restwert if t == J else 0)
        barwert += cashflow / (1 + i) ** t
        jahre.append({"jahr": t, "erloes": round(erloes), "waerme": round(waerme), "strom": round(strom),
                      "laufend": round(laufend), "fehlmenge": round(fehlmenge), "abschreibung": round(abschreibung),
                      "gewinn_vor_steuer": round(vor_steuer), "steuer": round(steuer),
                      "gewinn_nach_steuer": round(vor_steuer - steuer), "cashflow": round(cashflow)})
    annuitaet = i / (1 - (1 + i) ** -J)
    return {
        "server": n_server, "server_h": round(server_h),
        "hardware_chf": round(hardware), "investition_chf": round(investition), "restwert_chf": round(restwert),
        "ergebnis_pro_jahr_chf": round(barwert * annuitaet),
        "gewinn_nach_steuer_mittel_chf": round(sum(j["gewinn_nach_steuer"] for j in jahre) / J),
        "jahre": jahre,
    }


def break_even(n_server, server_h, waerme_kwh, fehlmenge_server_h=0.0, **ueberschreiben):
    """Vertragspreis (CHF pro Karten-Stunde), bei dem das Ergebnis genau 0 ist."""
    lo, hi = 0.0, 5.0
    for _ in range(60):
        m = (lo + hi) / 2
        if rechne(n_server, server_h, waerme_kwh, fehlmenge_server_h, vertragspreis_chf_karte_h=m,
                  **ueberschreiben)["ergebnis_pro_jahr_chf"] < 0:
            lo = m
        else:
            hi = m
    return round(hi, 4)


if __name__ == "__main__":
    import json
    r = rechne(8, 36290, 29027)
    r["break_even_chf_karte_h"] = break_even(8, 36290, 29027)
    print(json.dumps(r, indent=1, ensure_ascii=False))
