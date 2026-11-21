"""Day-ahead-Zusage: Wie viele Server-Stunden kann DigitalHeat einen Tag im Voraus verbindlich verkaufen?

Ablauf pro Zieltag D (Ansatz A, Design-Doc docs/technik/waerme-router-basel.md, Baustein 5):
1. Entscheid um 12 Uhr Ortszeit Basel am Vortag D−1 (R3-16: in UTC umgerechnet, 11 bzw. 10 UTC).
2. Prognoseprofil: Open-Meteo «Previous Runs», Modell ECMWF IFS 0,25°. Pro Zielstunde T wird
   `previous_day1` nur verwendet, wenn der Lauf (spätestens T − 24 h) plus Veröffentlichungsverzug vor
   dem Entscheid lag, sonst `previous_day2` (Lauf spätestens T − 48 h). Daraus Heizbedarf nach Case-Formel.
3. Trockenlauf (R3-2): Kopie des echten Zustands um 12 Uhr D−1 (Speicher, Jobs), Rest von D−1 und der
   ganze Tag D mit dem Prognoseprofil, unbegrenzt Typ A (Szenario «spot») = Prognose der Server-h für D.
4. Zugesagt = Sicherheitsfaktor × Prognose. Geliefert = wärmegeführte Server-h derselben Anlage im echten
   Lauf (Szenario «spot», also verfügbare Kapazität). Fehlmenge = max(0, verkauft − geliefert).
5. Sicherheitsfaktor: grösster Wert, bei dem höchstens 5 % der Tage eine Fehlmenge haben. Für 2024 liefert
   Open-Meteo keine Previous Runs (geprüft 21.11.2026), darum Rückfall: kalibriert auf Januar–Juni 2025,
   ausgewertet auf Juli–Dezember 2025. Achtung Saisonverschiebung: kalibriert vor allem in der Heizsaison.

Definitionen (R3-3):
  zusagbarer Anteil = Σ zugesagt ÷ Σ geliefert (Server-h des Szenarios «spot», ganzes Jahr)
  verkauft_d        = s × zugesagt_d mit s = min(1, Nachfrage-Annahme × Σ geliefert ÷ Σ zugesagt)
  fest gebucht      = Σ min(verkauft_d, geliefert_d) ÷ Σ geliefert   → `anteil_fest_gebucht` in rechne()
  Fehlmenge         = Σ max(0, verkauft_d − geliefert_d)             → `fehlmenge_server_h` in rechne()

Anwendung: Einzelhaus mit `jahr.Haus` (R3-12). Die Flotte (router.Flotte) hat dieselbe Schnittstelle
(`schritt`, `kopie(prognose=True)`, `profil`) und nutzt dieselbe Funktion.

Aufruf: python3 src/scheduler/zusage.py            # Referenzhaus 8 Server
"""
import json
import sys
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.scheduler import annahmen as A  # noqa: E402

ROOT = A.ROOT
BASEL = ZoneInfo("Europe/Zurich")
AUS = ROOT / "daten" / "ergebnisse"


# --- Prognosedaten -----------------------------------------------------------------------------------

def _utc(lokal):
    """'2025-03-07T13:00' (Ortszeit Basel) → aware UTC-datetime."""
    return datetime.fromisoformat(lokal).replace(tzinfo=BASEL).astimezone(timezone.utc)


def entscheid_utc(zieltag):
    """Entscheidzeitpunkt für Zieltag 'JJJJ-MM-TT': 12 Uhr Ortszeit am Vortag, in UTC."""
    vortag = (datetime.fromisoformat(zieltag) - timedelta(days=1)).date()
    lokal = datetime(vortag.year, vortag.month, vortag.day, A.wert("entscheid_uhr_lokal"), tzinfo=BASEL)
    return lokal.astimezone(timezone.utc)


def quelle_pro_stunde(zeit_lokal):
    """Welcher Prognosewert für diese Zielstunde zum Entscheid vorlag, mit abgeleiteter spätester Laufzeit.

    Gibt (feld, spaetester_lauf_utc). `previous_dayN` = Wert, der N × 24 h vor der Zielstunde vorhergesagt
    wurde (open-meteo.com/en/docs/previous-runs-api). Konservativ: Lauf = Zielstunde − N × 24 h
    (spätestmöglich), verfügbar nach `prognose_verzug_h`.
    """
    t = _utc(zeit_lokal)
    entscheid = entscheid_utc(zeit_lokal[:10])
    verzug = timedelta(hours=A.wert("prognose_verzug_h"))
    for n in (1, 2):
        lauf = t - timedelta(hours=24 * n)
        if lauf + verzug <= entscheid:
            return f"temperature_2m_previous_day{n}", lauf
    raise ValueError(f"Keine Prognose vor dem Entscheid für {zeit_lokal}")


def prognose_laden(modell=None):
    modell = modell or A.wert("prognose_modell")
    d = json.loads((ROOT / "daten" / "roh" / "openmeteo_prognose" / f"basel_2025_{modell}.json").read_text())
    return d["hourly"]


def prognose_profil(profil, modell=None):
    """Profil wie `jahr.profil_laden()`, aber Heizbedarf aus der Prognose, die zum Entscheid vorlag.

    Case-Formel wie src/referenzprofil.py: Heizbedarf = max(0, 10 kW × (20 − T) / 25,6) an Heiztagen
    (Tagesmittel < 12 °C), Warmwasser unverändert (planbar, 12 kWh/Tag).
    """
    from src import referenzprofil as R
    h = prognose_laden(modell)
    if h["time"] != [p["zeit"] for p in profil]:
        raise ValueError("Zeitachsen von Prognose und Profil stimmen nicht überein")
    temps = [h[quelle_pro_stunde(z)[0]][i] for i, z in enumerate(h["time"])]
    pro_tag = OrderedDict()
    for z, t in zip(h["time"], temps):
        pro_tag.setdefault(z[:10], []).append(t)
    heiztag = {tag: sum(v) / len(v) < R.HEIZGRENZE_C for tag, v in pro_tag.items()}
    neu = []
    for p, t in zip(profil, temps):
        heiz = max(0.0, R.AUSLEGUNG_KW * (R.INNEN_C - t) / R.KONSTANTE) if heiztag[p["zeit"][:10]] else 0.0
        neu.append({**p, "temp": t, "heizung": heiz})
    return neu


# --- Zusage ------------------------------------------------------------------------------------------

def tage_und_stunden(profil):
    tage = OrderedDict()
    for i, p in enumerate(profil):
        tage.setdefault(p["zeit"][:10], []).append(i)
    return tage


def tageswerte(anlage, prognose):
    """Läuft das Jahr echt durch und rechnet vor jedem Tag den Trockenlauf.

    `anlage` braucht `profil`, `schritt(h)` → dict mit 'server_laufend' (Summe über Standorte) und
    `kopie(profil)` (Haus) bzw. `kopie(prognose)` (Flotte, Liste von Profilen). Gibt pro Tag
    {'tag', 'prognose_server_h', 'geliefert_server_h'} zurück. Der erste Tag hat keine Zusage.
    """
    tage = tage_und_stunden(anlage.profil)
    namen = list(tage)
    start_12 = {}
    for i, tag in enumerate(namen[1:], start=1):
        vortag = namen[i - 1]
        start_12[tag] = next(h for h in tage[vortag] if anlage.profil[h]["zeit"].endswith(
            f"T{A.wert('entscheid_uhr_lokal'):02d}:00"))
    geliefert = {t: 0.0 for t in namen}
    progn = {t: 0.0 for t in namen}
    entscheid_bei = {}
    for tag, h12 in start_12.items():
        entscheid_bei.setdefault(h12, []).append(tag)
    for h in range(len(anlage.profil)):
        for tag in entscheid_bei.get(h, []):
            probe = anlage.kopie(prognose)
            for hh in range(h, tage[tag][-1] + 1):
                z = probe.schritt(hh)
                if hh in tage[tag]:
                    progn[tag] += z.get("server_h_lieferbar", z["server_laufend"])
        z = anlage.schritt(h)
        geliefert[anlage.profil[h]["zeit"][:10]] += z.get("server_h_lieferbar", z["server_laufend"])
    return [{"tag": t, "prognose_server_h": round(progn[t], 3) if t in start_12 else 0.0,
             "geliefert_server_h": round(geliefert[t], 3), "mit_zusage": t in start_12} for t in namen]


def fehltage_anteil(tage, faktor, toleranz=0.01):
    mit = [t for t in tage if t["mit_zusage"]]
    if not mit:
        return 0.0
    return sum(faktor * t["prognose_server_h"] - t["geliefert_server_h"] > toleranz for t in mit) / len(mit)


def kalibrieren(tage, max_fehltage=None):
    """Grösster Sicherheitsfaktor (Schritt 0,01), bei dem höchstens `max_fehltage` der Tage zu kurz sind."""
    max_fehltage = A.wert("zusage_max_fehltage") if max_fehltage is None else max_fehltage
    best = 0.0
    for k in range(0, 151):
        f = k / 100
        if fehltage_anteil(tage, f) <= max_fehltage + 1e-12:
            best = f
    return best


def auswerten(tage, faktor, nachfrage=None):
    """Zusagbarer Anteil, verkaufter Anteil und Fehlmenge für ein Jahr mit gegebenem Sicherheitsfaktor."""
    nachfrage = A.wert("anteil_fest_gebucht") if nachfrage is None else nachfrage
    geliefert = sum(t["geliefert_server_h"] for t in tage)
    zugesagt = sum(faktor * t["prognose_server_h"] for t in tage if t["mit_zusage"])
    zusagbar = zugesagt / geliefert if geliefert else 0.0
    s = min(1.0, nachfrage * geliefert / zugesagt) if zugesagt else 0.0
    fest = fehl = 0.0
    fehltage = 0
    for t in tage:
        verkauft = s * faktor * t["prognose_server_h"] if t["mit_zusage"] else 0.0
        fest += min(verkauft, t["geliefert_server_h"])
        f = max(0.0, verkauft - t["geliefert_server_h"])
        fehl += f
        fehltage += f > 0.01
    return {"sicherheitsfaktor": faktor, "geliefert_server_h": round(geliefert, 1),
            "zugesagt_server_h": round(zugesagt, 1), "zusagbarer_anteil": round(zusagbar, 4),
            "nachfrage_annahme": nachfrage, "verkaufsanteil_der_zusage": round(s, 4),
            "fest_gebucht_server_h": round(fest, 1),
            "anteil_fest_gebucht": round(fest / geliefert, 4) if geliefert else 0.0,
            "fehlmenge_server_h": round(fehl, 2), "tage_mit_fehlmenge": fehltage,
            "tage_mit_zusage": sum(t["mit_zusage"] for t in tage)}


def halbjahre(tage):
    h1 = [t for t in tage if t["tag"] < "2025-07-01"]
    h2 = [t for t in tage if t["tag"] >= "2025-07-01"]
    return h1, h2


def rechne_zusage(anlage, prognose):
    """Kalibrierung (H1), Auswertung (H2) und Jahreswerte für eine Anlage (Haus oder Flotte)."""
    tage = tageswerte(anlage, prognose)
    h1, h2 = halbjahre(tage)
    f = kalibrieren(h1)
    return {
        "methode": "Kalibrierung Jan–Jun 2025, Auswertung Jul–Dez 2025 (keine Previous Runs 2024)",
        "sicherheitsfaktor": f,
        "fehltage_kalibrierung": round(fehltage_anteil(h1, f), 4),
        "fehltage_auswertung": round(fehltage_anteil(h2, f), 4),
        "jahr": auswerten(tage, f), "kalibrierung": auswerten(h1, f), "auswertung": auswerten(h2, f),
        "tage": tage,
    }, anlage


def main():
    from src.scheduler.jahr import Haus, profil_laden
    from src.wirtschaft import rechne
    profil = profil_laden()
    haus = Haus(8, "spot", "rechnen", profil)
    r, haus = rechne_zusage(haus, prognose_profil(profil))
    b = haus.bilanz()
    j = r["jahr"]
    w_alt = rechne(8, b["server_h"], b["waerme_genutzt_kwh"])
    w_neu = rechne(8, b["server_h"], b["waerme_genutzt_kwh"], anteil_fest_gebucht=j["anteil_fest_gebucht"],
                   fehlmenge_server_h=j["fehlmenge_server_h"])
    karten = A.wert("karten_pro_server")
    r["wirtschaft"] = {
        "ohne_zusage_60_prozent_chf": w_alt["ergebnis_pro_jahr_chf"],
        "mit_zusage_chf": w_neu["ergebnis_pro_jahr_chf"],
        "fehlmenge_chf_jahr1": w_neu["jahre"][0]["fehlmenge"],
        "vertragspreis_chf_server_h": round(A.wert("vertragspreis_chf_karte_h") * karten, 2),
    }
    r["annahmen"] = {k: A.als_liste()[k] for k in (
        "prognose_modell", "prognose_verzug_h", "entscheid_uhr_lokal", "zusage_max_fehltage",
        "sla_gutschrift_anteil", "anteil_fest_gebucht", "vertragspreis_chf_karte_h")}
    AUS.mkdir(parents=True, exist_ok=True)
    (AUS / "zusage_8_spot.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in r.items() if k != "tage"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
