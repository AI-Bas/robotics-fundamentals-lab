#!/usr/bin/env bash
set -euo pipefail

#
# Mount Maker Pi RP2040 CIRCUITPY storage and expose it in workspace.
#
# Usage:
#   ./rpi4_platform/src/rpi4_mount_circuitpy.sh --dry-run
#   ./rpi4_platform/src/rpi4_mount_circuitpy.sh --apply
#

MODE="${1:---dry-run}"
if [[ "$MODE" != "--dry-run" && "$MODE" != "--apply" ]]; then
  echo "usage: $0 [--dry-run|--apply]"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MOUNT_DIR="/mnt/circuitpy"
WORKSPACE_LINK="$REPO_ROOT/mounts/circuitpy"
MOUNT_OPTS="uid=$(id -u),gid=$(id -g),umask=0022"

detect_circuitpy_device() {
  lsblk -rno PATH,LABEL | awk '$2=="CIRCUITPY" {print $1; exit}'
}

DEVICE_PATH="$(detect_circuitpy_device || true)"
if [[ -z "$DEVICE_PATH" ]]; then
  echo "[circuitpy-mount] error: CIRCUITPY device not detected via lsblk."
  exit 1
fi

echo "[circuitpy-mount] device: $DEVICE_PATH"
echo "[circuitpy-mount] mount: $MOUNT_DIR"
echo "[circuitpy-mount] workspace link: $WORKSPACE_LINK"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "sudo mkdir -p \"$MOUNT_DIR\""
  echo "sudo umount \"$MOUNT_DIR\" 2>/dev/null || true"
  echo "sudo mount -o \"$MOUNT_OPTS\" \"$DEVICE_PATH\" \"$MOUNT_DIR\""
  echo "mkdir -p \"$REPO_ROOT/mounts\""
  echo "ln -sfn \"$MOUNT_DIR\" \"$WORKSPACE_LINK\""
  exit 0
fi

sudo mkdir -p "$MOUNT_DIR"
sudo umount "$MOUNT_DIR" 2>/dev/null || true
sudo mount -o "$MOUNT_OPTS" "$DEVICE_PATH" "$MOUNT_DIR"

mkdir -p "$REPO_ROOT/mounts"
ln -sfn "$MOUNT_DIR" "$WORKSPACE_LINK"

echo "[circuitpy-mount] mounted and linked."
ls -la "$MOUNT_DIR"
