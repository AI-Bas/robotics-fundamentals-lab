#!/usr/bin/env bash
set -euo pipefail

#
# Install and enable HMI dashboard systemd service.
#
# Usage:
#   ./rpi4_platform/src/rpi4_install_hmi_service.sh --dry-run
#   ./rpi4_platform/src/rpi4_install_hmi_service.sh --apply
#

MODE="${1:---dry-run}"
if [[ "$MODE" != "--dry-run" && "$MODE" != "--apply" ]]; then
  echo "usage: $0 [--dry-run|--apply]"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_UNIT="$REPO_ROOT/rpi4_platform/config/systemd/hmi-dashboard.service"
TARGET_UNIT="/etc/systemd/system/hmi-dashboard.service"

echo "[hmi-service] mode: $MODE"
echo "[hmi-service] source: $SOURCE_UNIT"
echo "[hmi-service] target: $TARGET_UNIT"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "sudo cp \"$SOURCE_UNIT\" \"$TARGET_UNIT\""
  echo "sudo systemctl daemon-reload"
  echo "sudo systemctl enable hmi-dashboard.service"
  echo "sudo systemctl restart hmi-dashboard.service"
  echo "sudo systemctl status hmi-dashboard.service --no-pager"
  exit 0
fi

sudo cp "$SOURCE_UNIT" "$TARGET_UNIT"
sudo systemctl daemon-reload
sudo systemctl enable hmi-dashboard.service
sudo systemctl restart hmi-dashboard.service
sudo systemctl status hmi-dashboard.service --no-pager || true
