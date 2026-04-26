#!/usr/bin/env bash
set -euo pipefail

#
# Headless board bootstrap for Raspberry Pi and similar Linux SBC targets.
#
# Usage:
#   ./scripts/bootstrap/bootstrap_rpi_headless.sh --dry-run
#   ./scripts/bootstrap/bootstrap_rpi_headless.sh --apply --profile config/platforms/rpi_debian.env
#
# Notes:
# - Default mode is dry-run for safety.
# - Profile files provide board-specific overrides.
# - Script is staged so individual steps can be reused on other boards.
#

DRY_RUN=1
PROFILE_FILE="config/platforms/rpi_debian.env"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GENERIC_PROFILE="$REPO_ROOT/config/platforms/generic_linux.env"

log() {
  printf '[board-bootstrap] %s\n' "$1"
}

run_cmd() {
  local cmd="$1"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "dry-run: $cmd"
  else
    log "run: $cmd"
    eval "$cmd"
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)
        DRY_RUN=1
        shift
        ;;
      --apply)
        DRY_RUN=0
        shift
        ;;
      --profile)
        PROFILE_FILE="$2"
        shift 2
        ;;
      *)
        log "error: unknown argument: $1"
        exit 1
        ;;
    esac
  done
}

load_profile() {
  # shellcheck disable=SC1090
  source "$GENERIC_PROFILE"
  # shellcheck disable=SC1090
  source "$REPO_ROOT/$PROFILE_FILE"
  log "loaded profile: ${PROFILE_NAME:-unknown} ($PROFILE_FILE)"
}

bootstrap_apt_base() {
  run_cmd "sudo apt-get update"
  run_cmd "sudo apt-get install -y git curl wget ca-certificates build-essential cmake pkg-config"
  run_cmd "sudo apt-get install -y python3 python3-venv python3-pip python3-dev"
}

enable_hardware_interfaces() {
  if [[ "${ENABLE_I2C:-0}" == "1" ]]; then
    run_cmd "sudo raspi-config nonint do_i2c 0"
  fi
  if [[ "${ENABLE_SPI:-0}" == "1" ]]; then
    run_cmd "sudo raspi-config nonint do_spi 0"
  fi
  if [[ "${ENABLE_UART:-0}" == "1" ]]; then
    run_cmd "sudo raspi-config nonint do_serial_hw 0"
  fi

  run_cmd "sudo usermod -aG i2c,spi,gpio \$USER"
}

configure_network_baseline() {
  if [[ -n "${WIFI_COUNTRY_CODE:-}" ]]; then
    run_cmd "sudo raspi-config nonint do_wifi_country ${WIFI_COUNTRY_CODE}"
  fi
}

bootstrap_camera_stack() {
  if [[ "${ENABLE_CSI_CAMERA:-0}" != "1" ]]; then
    return 0
  fi

  run_cmd "sudo apt-get install -y libcamera-apps rpicam-apps v4l-utils"
  # Newer Pi stacks may expose rpicam-* instead of libcamera-* binaries.
  run_cmd "command -v rpicam-hello >/dev/null 2>&1 && rpicam-hello --version || libcamera-hello --version || true"
}

bootstrap_opencv_stack() {
  if [[ "${ENABLE_OPENCV:-0}" != "1" ]]; then
    return 0
  fi

  run_cmd "sudo apt-get install -y python3-opencv libopencv-dev"
}

bootstrap_hmi_stack() {
  if [[ "${ENABLE_HMI_STACK:-0}" != "1" ]]; then
    return 0
  fi

  # Install lightweight browser + Python UI dependencies for local/remote HMI.
  run_cmd "sudo apt-get install -y chromium-browser"
  run_cmd "echo 'Run HMI launcher: $REPO_ROOT/scripts/bootstrap/run_hmi_dashboard.sh'"
}

bootstrap_ros2_stack() {
  if [[ "${ENABLE_ROS2:-0}" != "1" ]]; then
    return 0
  fi

  # ROS2 packaging differs by distro/repo setup. Avoid hard failure when repo is absent.
  local ros_pkg
  ros_pkg="ros-${ROS2_DISTRO:-jazzy}-ros-base"
  run_cmd "sudo apt-get update"
  if apt-cache show "$ros_pkg" >/dev/null 2>&1; then
    run_cmd "sudo apt-get install -y $ros_pkg"
  else
    log "skip ROS2 install: package '$ros_pkg' is not available in configured apt repositories."
    log "hint: add the official ROS2 apt repository for your distro, then rerun bootstrap."
  fi
}

bootstrap_ai_accelerator() {
  if [[ "${ENABLE_AI_ACCELERATOR:-0}" != "1" ]]; then
    return 0
  fi

  # Placeholder for board-specific AI accelerator install flow.
  run_cmd "echo 'AI accelerator setup is profile-specific; add commands in platform profile docs.'"
}

ensure_fan_auto_mode() {
  local fan_mode_script
  fan_mode_script="$REPO_ROOT/rpi4_platform/src/rpi4_fan_mode.py"
  if [[ -f "$fan_mode_script" ]]; then
    run_cmd "sudo python3 \"$fan_mode_script\" --mode auto || true"
  else
    log "fan mode script not found; skipping dedicated fan auto-mode setup."
  fi
}

print_validation_hints() {
  log "validation hints:"
  log "- interfaces: ls /dev/spidev* ; ls /dev/i2c-*"
  log "- groups: id"
  log "- camera: libcamera-hello --list-cameras"
  log "- python: python3 --version"
  log "- c++: g++ --version"
  log "- ros2: source /opt/ros/${ROS2_DISTRO:-jazzy}/setup.bash && ros2 --help"
}

main() {
  parse_args "$@"
  load_profile

  log "repo root: $REPO_ROOT"
  log "mode: $( [[ "$DRY_RUN" == "1" ]] && echo dry-run || echo apply )"

  bootstrap_apt_base
  enable_hardware_interfaces
  configure_network_baseline
  bootstrap_camera_stack
  bootstrap_opencv_stack
  bootstrap_hmi_stack
  bootstrap_ros2_stack
  bootstrap_ai_accelerator
  ensure_fan_auto_mode
  print_validation_hints

  log "headless bootstrap sequence complete"
}

main "$@"
