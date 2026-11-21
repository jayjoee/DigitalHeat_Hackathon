#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 demo_start.py --open
printf '\nZum Schliessen Enter drücken.\n'
read -r answer
