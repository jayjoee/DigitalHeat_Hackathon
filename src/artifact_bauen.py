"""Baut aus dashboard/index.html eine eigenständige Seite zum Veröffentlichen.

- Daten (dashboard/daten.js) direkt eingebettet
- Live-Panel zeigt den aufgezeichneten Flottenlauf aus dem Repo (Wechsel Haus → Sportbad).
  Die lokale, nicht eingecheckte dashboard/live.json nur mit --lokal, damit der Build reproduzierbar bleibt.
- Ohne doctype/html/head/body (die Veröffentlichung legt sie selbst an), mit charset für das direkte Öffnen

Aufruf: python3 src/artifact_bauen.py  -> dashboard/artifact/index.html
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "dashboard"


def main():
    html = (D / "index.html").read_text()
    daten = (D / "daten.js").read_text().strip()
    aufzeichnung = ROOT / "daten" / "ergebnisse" / "live_flotte_2025-05-25.json"
    if "--lokal" in sys.argv[1:]:
        aufzeichnung = D / "live.json"
    live = json.loads(aufzeichnung.read_text())
    live["aktiv"] = False
    live.pop("jetzt", None)

    kopf = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
    kopf = re.sub(r'<meta charset="utf-8">\s*', "", kopf)
    kopf = re.sub(r'<meta name="viewport"[^>]*>\s*', "", kopf)
    kopf = kopf.replace("<title>Computing that heats</title>",
                        '<title>Computing that heats</title>\n<meta name="claude:viewport-fit-sides" content="cover">')
    rumpf = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
    rumpf = rumpf.replace('<script src="daten.js"></script>',
                          "<script>\n" + daten + "\nwindow.LIVE_AUFZEICHNUNG = " +
                          json.dumps(live, ensure_ascii=False) + ";\n</script>")
    aus = D / "artifact" / "index.html"
    aus.parent.mkdir(exist_ok=True)
    aus.write_text('<meta charset="utf-8">\n' + kopf.strip() + "\n" + rumpf.strip() + "\n")
    print(f"{aus.relative_to(ROOT)}: {aus.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
