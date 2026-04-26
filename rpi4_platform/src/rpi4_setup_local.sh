#!/usr/bin/env bash
set -euo pipefail

#
# Raspberry Pi 4 specific setup helper.
# Wraps shared bootstrap and adds RPi-specific package/install checks.
#
# Usage:
#   ./rpi4_platform/src/rpi4_setup_local.sh --dry-run
#   ./rpi4_platform/src/rpi4_setup_local.sh --apply
#

MODE="--dry-run"
if [[ "${1:-}" == "--apply" ]]; then
  MODE="--apply"
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "[rpi4-setup] mode: $MODE"
echo "[rpi4-setup] repo: $REPO_ROOT"

"$REPO_ROOT/scripts/bootstrap/bootstrap_rpi_headless.sh" "$MODE" --profile config/platforms/rpi_debian.env

if [[ "$MODE" == "--dry-run" ]]; then
  echo "[rpi4-setup] dry-run complete."
  exit 0
fi

echo "[rpi4-setup] installing rpi4_platform python requirements"
if [[ ! -d "$REPO_ROOT/rpi4_platform/.venv" ]]; then
  python3 -m venv "$REPO_ROOT/rpi4_platform/.venv"
fi
source "$REPO_ROOT/rpi4_platform/.venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r "$REPO_ROOT/rpi4_platform/requirements.txt"
deactivate

echo "[rpi4-setup] setting dedicated fan mode to auto when hwmon is available"
sudo python3 "$REPO_ROOT/rpi4_platform/src/rpi4_fan_mode.py" --mode auto || true

echo "[rpi4-setup] validating status collection script"
python3 "$REPO_ROOT/rpi4_platform/src/rpi4_status.py" --pretty || true

echo "[rpi4-setup] complete"
