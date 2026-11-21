#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 start.py --powermetrics
printf "\nFertig. Zum Schliessen Enter drücken.\n"
read -r answer
