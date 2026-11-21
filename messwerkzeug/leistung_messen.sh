#!/bin/bash
# Misst die CPU-Leistung mit powermetrics, während der Embedding-Job läuft.
# Im macOS-Terminal ausführen (fragt einmal nach dem Mac-Passwort):
#   bash ~/Desktop/Smithers/DigitalHeat_Hackathon/src/leistung_messen.sh
set -e
cd "$(dirname "$0")/.."
TS=$(date +%Y-%m-%d_%H%M)
LOG=messungen/powermetrics_$TS.txt
LAUF=messungen/embedding_pm_$TS

echo "Mac-Passwort für powermetrics (beim Tippen erscheint nichts):"
sudo -v
[ -e "$LAUF" ] && { echo "$LAUF existiert schon, eine Minute warten"; exit 1; }
sudo powermetrics --samplers cpu_power -i 1000 -n 150 > "$LOG" &
PM=$!
sleep 5   # 5 s Leerlauf als Vergleich
.venv/bin/python src/jobs/embedding_job.py --arbeitsordner "$LAUF" --anzahl 7600 | grep -E "start bei|fertig"
echo "Job fertig, warte auf Ende der Messung …"
sudo kill -INT $PM 2>/dev/null || true
wait $PM 2>/dev/null || true
.venv/bin/python src/energie.py --lauf "$LAUF" --powermetrics "$LOG"
