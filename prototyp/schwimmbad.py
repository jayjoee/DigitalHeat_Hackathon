"""Schwimmbad (Laptop B): zeigt einen Code und wartet auf das Haus. Standard: Docking (virtuelles Screening).

  python3 prototyp/schwimmbad.py                 # Docking
  python3 prototyp/schwimmbad.py --job blister   # Blisterprüfung
"""
from zwei_laptops import main

if __name__ == "__main__":
    main("schwimmbad")
