"""Find an existing FastEmbed environment without changing it."""
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
candidates=[os.environ.get('DIGITALHEAT_PYTHON'),ROOT/'.venv/bin/python',
            ROOT.parent/'.venv/bin/python',ROOT.parent/'.venv-ml/bin/python',
            Path.home()/'Desktop/Smithers/DigitalHeat_Hackathon/.venv/bin/python',sys.executable]
for candidate in candidates:
    if not candidate or not Path(candidate).exists():continue
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    check=subprocess.run([str(candidate),'-c',"import importlib.util; raise SystemExit(0 if importlib.util.find_spec('fastembed') else 1)"],env=env,capture_output=True)
    if check.returncode==0:
        raise SystemExit(subprocess.call([str(candidate),str(ROOT/'messung.py'),*sys.argv[1:]],cwd=ROOT,env=env))
print('FastEmbed ist noch nicht eingerichtet. Bitte die Einrichtung in README.md ausführen.')
raise SystemExit(1)
