#!/bin/bash
# Doppelklicken. Blister-Demo auf zwei Laptops: Schwimmbad.
cd "$(dirname "$0")/.."
python3 prototyp/schwimmbad.py
echo
read -n 1 -s -r -p "Press any key to close"
