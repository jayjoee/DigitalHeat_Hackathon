#!/bin/bash
# Fragt nur nach dem GitHub-Token und speichert ihn im macOS-Schlüsselbund für dieses Repository.
cd "$(dirname "$0")/.."
echo
echo "Token hier einfügen (Cmd + V), dann Enter. Beim Einfügen erscheint nichts:"
read -rs TOKEN
echo
TOKEN="$(printf '%s' "$TOKEN" | tr -d '[:space:]')"
if [ -z "$TOKEN" ]; then echo "Kein Token eingefügt, nochmals starten."; exit 1; fi
case "$TOKEN" in
  github_pat_*) echo "Hinweis: Das ist ein Fine-grained-Token. Für ein fremdes Repository braucht es meist einen klassischen (ghp_…)." ;;
  ghp_*) ;;
  *) echo "Hinweis: Der Text beginnt nicht mit ghp_ – ist es wirklich der Token?" ;;
esac
printf 'protocol=https\nhost=github.com\nusername=jayjoee\npassword=%s\n\n' "$TOKEN" | git credential approve
unset TOKEN
if GIT_TERMINAL_PROMPT=0 git ls-remote origin >/dev/null 2>&1; then
  echo "OK: Anmeldung gespeichert, Zugriff auf das Repository klappt."
else
  printf 'protocol=https\nhost=github.com\nusername=jayjoee\n\n' | git credential reject
  echo "Fehler: GitHub lehnt den Token ab oder er hat keinen Zugriff auf Skinny-King/holyhackers. Nichts gespeichert."
fi
