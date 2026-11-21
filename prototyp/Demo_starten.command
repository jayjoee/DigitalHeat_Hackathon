#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 digitalheat.py demo --open
printf '\nDemo ended. Press Enter to close.\n'
read -r answer
