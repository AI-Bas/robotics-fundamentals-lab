#!/usr/bin/env bash
set -euo pipefail

#
# Install Python dev tools in a dedicated virtual environment (PEP 668 safe).
#
# Usage:
#   ./scripts/bootstrap/bootstrap_dev_tools.sh
#

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_VENV="$REPO_ROOT/.dev-tools-venv"

if ! dpkg -s python3-full >/dev/null 2>&1; then
  echo "[dev-tools] installing python3-full (required for ensurepip on some Pi OS images)"
  sudo apt-get update
  sudo apt-get install -y python3-full
fi

if [[ ! -d "$TOOLS_VENV" ]]; then
  python3 -m venv "$TOOLS_VENV"
fi

source "$TOOLS_VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install pyright ruff mypy
deactivate

echo "[dev-tools] installed in $TOOLS_VENV"
echo "[dev-tools] use with:"
echo "  source \"$TOOLS_VENV/bin/activate\""
echo "  pyright --version && ruff --version && mypy --version"
