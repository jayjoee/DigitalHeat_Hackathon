#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
if [ -x .venv-ml/bin/python ]; then
 .venv-ml/bin/python start/ml_start.py --open
else
 python3 start/ml_start.py --open
fi
printf "\nZum Schliessen Enter drücken.\n"
read -r answer
