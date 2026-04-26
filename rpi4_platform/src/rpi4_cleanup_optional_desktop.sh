#!/usr/bin/env bash
set -euo pipefail

#
# Optional cleanup for headless robotics deployments.
# Removes desktop/VPN/editor packages not required for this project.
#
# Usage:
#   ./rpi4_platform/src/rpi4_cleanup_optional_desktop.sh --dry-run
#   ./rpi4_platform/src/rpi4_cleanup_optional_desktop.sh --apply
#

MODE="${1:---dry-run}"
if [[ "$MODE" != "--dry-run" && "$MODE" != "--apply" ]]; then
  echo "usage: $0 [--dry-run|--apply]"
  exit 1
fi

PKGS=(
  code
  firefox
  rpi-firefox-mods
  geany
  geany-common
  mu-editor
  thonny
  nordvpn-release
  lxde
  lxde-common
  lxde-core
  lxde-icon-theme
  openbox-lxde-session
  raspberrypi-ui-mods
)

echo "[cleanup] mode: $MODE"
echo "[cleanup] candidate packages:"
printf '  - %s\n' "${PKGS[@]}"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "[cleanup] dry-run command preview:"
  echo "sudo apt-get purge -y ${PKGS[*]}"
  echo "sudo apt-get autoremove -y"
  echo "sudo apt-get clean"
  echo "df -h /"
  exit 0
fi

sudo apt-get purge -y "${PKGS[@]}" || true
sudo apt-get autoremove -y
sudo apt-get clean
df -h /
