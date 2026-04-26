#!/usr/bin/env bash
set -euo pipefail

#
# Bootstrap a consistent workspace path and local Python environments.
#
# Usage:
#   ./scripts/bootstrap/bootstrap_workspace.sh [repo_root]
#
# Behavior:
# - Resolves repository root from argument or current git context.
# - Creates canonical symlink at ~/robotics-fundamentals-lab when needed.
# - Creates module-local virtual environments where requirements exist.
#

log() {
  printf '[workspace-bootstrap] %s\n' "$1"
}

resolve_repo_root() {
  if [[ $# -ge 1 && -n "${1:-}" ]]; then
    printf '%s\n' "$1"
    return 0
  fi

  # Fallback to current git top-level; this fails fast if outside a repo.
  git rev-parse --show-toplevel
}

create_canonical_symlink() {
  local repo_root="$1"
  local canonical_path="$HOME/robotics-fundamentals-lab"

  if [[ "$repo_root" == "$canonical_path" ]]; then
    log "repo already at canonical path: $canonical_path"
    return 0
  fi

  if [[ -e "$canonical_path" && ! -L "$canonical_path" ]]; then
    log "skipping symlink; canonical path exists and is not a symlink: $canonical_path"
    return 0
  fi

  ln -sfn "$repo_root" "$canonical_path"
  log "created canonical symlink: $canonical_path -> $repo_root"
}

ensure_module_venv() {
  local repo_root="$1"
  local module_path="$2"
  local python_bin="${PYTHON_BIN:-python3}"

  if [[ ! -f "$module_path/requirements.txt" ]]; then
    return 0
  fi

  if [[ ! -d "$module_path/.venv" ]]; then
    log "creating venv for module: ${module_path#$repo_root/}"
    "$python_bin" -m venv "$module_path/.venv"
  else
    log "venv already exists for module: ${module_path#$repo_root/}"
  fi

  # Skip dependency install unless requested, to keep bootstrap fast and optional.
  if [[ "${INSTALL_REQUIREMENTS:-0}" == "1" ]]; then
    log "installing requirements for module: ${module_path#$repo_root/}"
    "$module_path/.venv/bin/python" -m pip install --upgrade pip
    "$module_path/.venv/bin/python" -m pip install -r "$module_path/requirements.txt"
  fi
}

main() {
  local repo_root
  repo_root="$(resolve_repo_root "${1:-}")"

  if [[ ! -d "$repo_root/.git" ]]; then
    log "error: not a git repository: $repo_root"
    exit 1
  fi

  log "repo root: $repo_root"
  create_canonical_symlink "$repo_root"

  local modules
  modules=(
    "optical_flow"
    "power_monitor"
    "vision_camera"
    "modular_io"
    "motor_control"
  )

  local module_dir
  for module_dir in "${modules[@]}"; do
    if [[ -d "$repo_root/$module_dir" ]]; then
      ensure_module_venv "$repo_root" "$repo_root/$module_dir"
    fi
  done

  log "workspace bootstrap complete"
}

main "$@"
