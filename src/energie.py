"""Energie des gemessenen Embedding-Jobs und Skalierung auf den 1-kW-Referenzserver.

Energie = gemessene Rechenzeit × Leistung des Geräts.
- Standard: Annahme CPU_LEISTUNG_W (siehe messungen/MESSUNG.md, Quelle und Spanne)
- Besser: eigene Messung mit powermetrics (braucht sudo, Joël führt sie selbst aus):
    sudo powermetrics --samplers cpu_power -i 1000 -n 150 > messungen/powermetrics.txt
  während der Job läuft, dann:  python src/energie.py --powermetrics messungen/powermetrics.txt

Aufruf: .venv/bin/python src/energie.py [--lauf messungen/embedding_…] [--powermetrics datei]
"""
import argparse
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPU_LEISTUNG_W = 30.0      # Annahme M1 Pro, alle Leistungskerne ausgelastet (Spanne 20–35 W)
SERVER_KW = 1.0            # Referenzserver laut Case
JOB_TEXTE = 10_000_000     # Definition Jobtyp «Archiv-Embedding»: 10 Mio. Texte (wie src/jobtypen.py)


def leistung_aus_powermetrics(pfad, von, bis):
    """Mittlere Leistung (CPU, GPU, ANE) in den Sekunden zwischen von und bis (Unix-Zeit).

    Gibt (Watt unter Last ohne Leerlauf, Watt Last, Watt Leerlauf, Sekunden Last, Sekunden Leerlauf).
    Leerlauf = Proben ausserhalb des Jobfensters.
    """
    from datetime import datetime
    text = Path(pfad).read_text(errors="replace")
    teile = re.split(r"\*\*\* Sampled system activity \((.+?)\) \(([\d.]+)ms elapsed\) \*\*\*", text)
    last, leer = [], []
    for i in range(1, len(teile) - 2, 3):
        t = datetime.strptime(teile[i], "%a %b %d %H:%M:%S %Y %z").timestamp()
        block = teile[i + 2]
        w = sum(float(m) for m in re.findall(r"(?:CPU|GPU|ANE) Power:\s*([\d.]+)\s*mW", block)) / 1000
        # Probe t deckt die Sekunde davor ab
        (last if von + 1 <= t <= bis else leer).append(w)
    if not last:
        raise SystemExit("Keine Proben im Jobfenster, lief powermetrics während des Jobs?")
    m_last = sum(last) / len(last)
    m_leer = sum(leer) / len(leer) if leer else 0.0
    return m_last - m_leer, m_last, m_leer, len(last), len(leer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lauf", default=sorted(glob.glob(str(ROOT / "messungen/embedding_2026*")))[0])
    ap.add_argument("--powermetrics")
    a = ap.parse_args()

    s = json.loads((Path(a.lauf) / "stand.json").read_text())
    rechen_s = sum(b["wand_s"] for b in s["bloecke"])
    texte = sum(b["texte"] for b in s["bloecke"])

    if a.powermetrics:
        von = s["starts"][-1]["zeit"]
        bis = s.get("fertig_unix", s["bloecke"][-1]["ende_unix"])
        netto, brutto, leer, n_last, n_leer = leistung_aus_powermetrics(a.powermetrics, von, bis)
        watt = brutto
        quelle = (f"powermetrics CPU+GPU+ANE, Mittel über {n_last} s Job ({brutto:.1f} W); "
                  f"Leerlauf {leer:.1f} W über {n_leer} s, Mehrleistung durch den Job {netto:.1f} W")
    else:
        watt, quelle = CPU_LEISTUNG_W, "Annahme (nicht gemessen)"

    wh_pro_1000 = rechen_s * watt / texte * 1000 / 3600
    texte_pro_kwh = 1000 / wh_pro_1000 * 1000
    server_texte_pro_s = texte_pro_kwh * SERVER_KW / 3600
    job_kwh = JOB_TEXTE / texte_pro_kwh
    job_min = job_kwh / SERVER_KW * 60

    r = {
        "lauf": str(Path(a.lauf).resolve().relative_to(ROOT)),
        "texte": texte, "rechenzeit_s": round(rechen_s, 1),
        "durchsatz_laptop_texte_s": round(texte / rechen_s, 1),
        "leistung_w": round(watt, 1), "leistung_quelle": quelle,
        "energie_wh_pro_1000_texte": round(wh_pro_1000, 4),
        "texte_pro_kwh": round(texte_pro_kwh),
        "server_1kw_texte_pro_s": round(server_texte_pro_s),
        "job_archiv_embedding": {"texte": JOB_TEXTE, "kwh": round(job_kwh, 3),
                                 "minuten_auf_1kw_server": round(job_min, 1)},
        "skalierung": "energieproportional: gleiche Texte pro kWh wie gemessen (konservativ, "
                      "GPU-Server sind für Embeddings effizienter)",
    }
    (ROOT / "messungen" / "energie.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
    print(json.dumps(r, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
