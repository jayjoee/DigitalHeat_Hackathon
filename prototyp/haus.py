"""Haus (Laptop A): findet das Schwimmbad im WLAN und startet die Demo. Standard: Docking (virtuelles Screening).

  python3 prototyp/haus.py                 # Docking
  python3 prototyp/haus.py --job blister   # Blisterprüfung
"""
from zwei_laptops import main

if __name__ == "__main__":
    main("haus")
