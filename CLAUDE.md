# DigitalHeat Hackathon – eigenes Projekt

Dieser Ordner gehört **nicht** zur Bachelorarbeit. Die Regeln aus `../CLAUDE.md` (BA_v9.docx, Agents, Schreibregeln, Zitierregeln, Umfang) gelten hier nicht.

- Einstieg für Menschen: `README.md`. Case-Beschreibung: `docs/CASE.md`
- Ordner: `docs/` (CASE, PITCH, TODO; Unterordner `ergebnisse/`, `wirtschaft/`, `kunden/`, `technik/`, ), `daten/` (Referenzhaus-CSV, Wetter, Preise, Ergebnisse), `src/` (Scheduler, Router, Jobs, Bilanz), `messungen/` (gemessene Laufzeiten und Energie), `dashboard/`, `tests/`, `prototyp/` (Klick-Prototyp Pharma/Hausbesitzer), `start/` (Startskripte, Doppelklick-Dateien, `alles_neu_rechnen.py`), `requirements/`, `messwerkzeug/`, `deploy/`
- Jede Annahme mit Quelle notieren, jede Zahl reproduzierbar aus Code.
- Zahlen stehen nur in `docs/wirtschaft/KOSTEN_DH.md` und `docs/ergebnisse/ERGEBNISSE.md`; andere Dokumente verlinken darauf. Nach jeder Änderung an Annahmen: `python3 start/alles_neu_rechnen.py`.
