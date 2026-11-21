"""Echter Rechenjob: virtuelles Screening (Docking) mit AutoDock Vina, pausierbar und mit Checkpoints.

Schlüssel-Schloss-Prinzip: Für jedes Molekül (Schlüssel) sucht Vina die beste Lage in der Bindetasche des
Proteins (Schloss) und schätzt die Bindungsenergie. Je negativer, desto besser passt der Schlüssel.

- Schloss: Abl-Kinase, PDB 1IEP (Ziel bei chronischer myeloischer Leukämie), daten/docking/1iep_receptor.pdbqt
- Schlüssel: 28 Moleküle in daten/docking/liganden/ (Kinasehemmer, Medikamente, Alltagsmoleküle),
  vorbereitet aus daten/docking/molekuele.csv mit RDKit und Meeko
- Erwartung: Imatinib (Glivec), das echte Medikament für dieses Protein, bindet am stärksten.
- Checkpoint nach jedem Molekül (stand.json, atomar geschrieben). Gleiche Schnittstelle wie embedding_job.py:
  «naechster» = Zahl fertiger Moleküle.
- Pause: SIGSTOP/SIGCONT an die Prozessgruppe (live.py). SIGTERM: laufendes Molekül fertig, Checkpoint, Ende.

Vina wird so gefunden: Python-Paket «vina» (pip install vina, Linux/Windows) oder Programm «vina»
(Option --vina, Umgebungsvariable DIGITALHEAT_VINA, tools/vina oder im PATH; Mac-Download siehe daten/docking/README.md).

Aufruf:
  python3 src/jobs/docking_job.py --arbeitsordner messungen/docking_job
"""
import argparse
import csv
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATEN = ROOT / "daten" / "docking"
REZEPTOR = DATEN / "1iep_receptor.pdbqt"
ZENTRUM = (15.190, 53.903, 16.917)  # Bindetasche von 1IEP (AutoDock-Vina-Beispiel, 1iep_receptor.box.txt)
GROESSE = (20.0, 20.0, 20.0)

aufhoeren = False


def _sigterm(signum, frame):
    global aufhoeren
    aufhoeren = True  # laufendes Molekül fertig rechnen, dann Checkpoint und Ende


def molekuele():
    with (DATEN / "molekuele.csv").open(encoding="utf-8") as f:
        return [(z["name"], z["gruppe"]) for z in csv.DictReader(f)]


def vina_programm(option):
    for kandidat in (option, os.environ.get("DIGITALHEAT_VINA"), ROOT / "tools" / "vina", shutil.which("vina")):
        if kandidat and Path(kandidat).is_file() and os.access(kandidat, os.X_OK):
            return str(kandidat)
    return None


class PythonVina:
    """Vina als Python-Paket: rechnet im selben Prozess, SIGSTOP hält es direkt an."""
    name = "Python-Paket vina"

    def __init__(self, cpu, erschoepfend, seed):
        from vina import Vina
        self.v = Vina(sf_name="vina", cpu=cpu, seed=seed, verbosity=0)
        self.v.set_receptor(str(REZEPTOR))
        self.v.compute_vina_maps(center=list(ZENTRUM), box_size=list(GROESSE))
        self.erschoepfend = erschoepfend

    def docken(self, ligand, ausgabe):
        self.v.set_ligand_from_file(str(ligand))
        self.v.dock(exhaustiveness=self.erschoepfend, n_poses=1)
        self.v.write_poses(str(ausgabe), n_poses=1, overwrite=True)
        return float(self.v.energies(n_poses=1)[0][0])


class ProgrammVina:
    """Vina als Programm: Kindprozess in derselben Prozessgruppe, live.py pausiert die ganze Gruppe."""
    name = "Programm vina"

    def __init__(self, pfad, cpu, erschoepfend, seed):
        self.pfad, self.cpu, self.erschoepfend, self.seed = pfad, cpu, erschoepfend, seed

    def docken(self, ligand, ausgabe):
        befehl = [self.pfad, "--receptor", str(REZEPTOR), "--ligand", str(ligand), "--out", str(ausgabe),
                  "--center_x", str(ZENTRUM[0]), "--center_y", str(ZENTRUM[1]), "--center_z", str(ZENTRUM[2]),
                  "--size_x", str(GROESSE[0]), "--size_y", str(GROESSE[1]), "--size_z", str(GROESSE[2]),
                  "--exhaustiveness", str(self.erschoepfend), "--num_modes", "1", "--seed", str(self.seed)]
        if self.cpu:
            befehl += ["--cpu", str(self.cpu)]
        subprocess.run(befehl, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        m = re.search(r"REMARK VINA RESULT:\s+(-?\d+\.\d+)", Path(ausgabe).read_text())
        return float(m.group(1))


def rechner(a):
    if not a.vina:
        try:
            return PythonVina(a.cpu, a.erschoepfend, a.seed)
        except ImportError:
            pass
    pfad = vina_programm(a.vina)
    if pfad is None:
        sys.exit("AutoDock Vina fehlt: pip install vina (Linux/Windows) oder Programm nach tools/vina laden "
                 "(Mac: siehe daten/docking/README.md).")
    return ProgrammVina(pfad, a.cpu, a.erschoepfend, a.seed)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arbeitsordner", required=True)
    ap.add_argument("--anzahl", type=int, default=0, help="Moleküle insgesamt; 0 = ganze Bibliothek, mehr = wiederholen")
    ap.add_argument("--erschoepfend", type=int, default=8, help="Suchtiefe von Vina (exhaustiveness, Standard 8)")
    ap.add_argument("--cpu", type=int, default=0, help="Rechenkerne für Vina, 0 = alle")
    ap.add_argument("--seed", type=int, default=1, help="Zufallsstart, damit Läufe vergleichbar sind")
    ap.add_argument("--vina", help="Pfad zum Vina-Programm (sonst Python-Paket, tools/vina oder PATH)")
    ap.add_argument("--ready-file", help="Bereitschaft nach Initialisierung melden")
    ap.add_argument("--start-paused", action="store_true", help="Nach Initialisierung bis SIGCONT warten")
    a = ap.parse_args()

    signal.signal(signal.SIGTERM, _sigterm)
    ordner = Path(a.arbeitsordner)
    ordner.mkdir(parents=True, exist_ok=True)
    bibliothek = molekuele()
    stand_pfad = ordner / "stand.json"
    stand = json.loads(stand_pfad.read_text()) if stand_pfad.exists() else {
        "auftrag": "docking", "schloss": "Abl-Kinase (PDB 1IEP)", "anzahl": a.anzahl or len(bibliothek),
        "erschoepfend": a.erschoepfend, "seed": a.seed, "naechster": 0, "ergebnisse": [], "starts": [],
    }
    t0 = time.perf_counter()
    r = rechner(a)
    stand["starts"].append({"zeit": time.time(), "pid": os.getpid(), "ab": stand["naechster"], "vina": r.name,
                            "vorbereiten_s": round(time.perf_counter() - t0, 3),
                            "systemlast_1min": round(os.getloadavg()[0], 2)})
    print(f"[docking {os.getpid()}] start bei {stand['naechster']}/{stand['anzahl']} ({r.name})", flush=True)
    if a.ready_file:
        Path(a.ready_file).write_text(json.dumps({"pid": os.getpid(), "auftrag": "docking", "ready": True}))
    if a.start_paused:
        os.kill(os.getpid(), signal.SIGSTOP)

    posen = ordner / "posen"
    posen.mkdir(exist_ok=True)
    while stand["naechster"] < stand["anzahl"]:
        i = stand["naechster"]
        name, gruppe = bibliothek[i % len(bibliothek)]
        w0, c0 = time.perf_counter(), time.process_time()
        energie = r.docken(DATEN / "liganden" / f"{name}.pdbqt", posen / f"{i:04d}_{name}.pdbqt")
        w1, c1 = time.perf_counter(), time.process_time()
        stand["naechster"] = i + 1
        stand["ergebnisse"].append({"nr": i, "name": name, "gruppe": gruppe, "energie_kcal_mol": energie,
                                    "wand_s": round(w1 - w0, 3), "cpu_s_job": round(c1 - c0, 3),
                                    "ende_unix": time.time()})
        tmp = stand_pfad.with_suffix(".tmp")
        tmp.write_text(json.dumps(stand, indent=1, ensure_ascii=False))
        tmp.replace(stand_pfad)  # atomar: Checkpoint ist nie halb geschrieben
        print(f"[docking {os.getpid()}] {stand['naechster']}/{stand['anzahl']} {name}: {energie:.1f} kcal/mol "
              f"({w1 - w0:.1f} s)", flush=True)
        if aufhoeren:
            print(f"[docking {os.getpid()}] Checkpoint bei {stand['naechster']}, beendet", flush=True)
            sys.exit(3)  # 3 = angehalten, nicht fertig

    stand["fertig_unix"] = time.time()
    besten = sorted(stand["ergebnisse"], key=lambda e: e["energie_kcal_mol"])[:5]
    stand["rangliste_top5"] = [f"{e['name']} {e['energie_kcal_mol']:.1f}" for e in besten]
    stand_pfad.write_text(json.dumps(stand, indent=1, ensure_ascii=False))
    print(f"[docking {os.getpid()}] fertig. Beste Schlüssel: " + ", ".join(stand["rangliste_top5"]), flush=True)


if __name__ == "__main__":
    main()
