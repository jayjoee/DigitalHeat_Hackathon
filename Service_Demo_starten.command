#!/bin/zsh
set -e
service_project_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$service_project_dir"
if [[ -x .venv-ml/bin/python ]]; then
  exec .venv-ml/bin/python service_start.py --demo --open
fi
exec python3 service_start.py --demo --open
