#!/bin/bash
# Double-click to start the house screen for the docking demo.
cd "$(dirname "$0")/.."
python3 prototyp/haus.py
echo
read -n 1 -s -r -p "Press any key to close"
