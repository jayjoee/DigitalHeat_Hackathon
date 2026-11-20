#!/bin/bash
# Startet das Dashboard auf http://localhost:8765 (nötig, damit die Live-Anzeige live.json lesen kann)
cd "$(dirname "$0")" && echo "Dashboard: http://localhost:8765" && python3 -m http.server 8765 --bind 127.0.0.1
