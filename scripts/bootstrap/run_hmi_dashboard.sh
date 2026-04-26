#!/usr/bin/env bash
set -euo pipefail

#
# Start HMI dashboard for local touchscreen and remote browser access.
#
# Usage:
#   ./scripts/bootstrap/run_hmi_dashboard.sh
#   HMI_PORT=8501 ./scripts/bootstrap/run_hmi_dashboard.sh
#

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HMI_PORT="${HMI_PORT:-8501}"
HMI_HOST="${HMI_HOST:-0.0.0.0}"

cd "$REPO_ROOT/hmi_dashboard"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

exec streamlit run src/app.py --server.address "$HMI_HOST" --server.port "$HMI_PORT"
