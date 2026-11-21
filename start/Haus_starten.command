#!/bin/bash
# Doppelklicken. Blister-Demo auf zwei Laptops: Haus.
cd "$(dirname "$0")/.."
python3 prototyp/haus.py
echo
read -n 1 -s -r -p "Taste drücken zum Schliessen"
