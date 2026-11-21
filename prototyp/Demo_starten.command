#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 digitalheat.py demo --open
printf '\nDemo beendet. Zum Schliessen Enter drücken.\n'
read -r answer
