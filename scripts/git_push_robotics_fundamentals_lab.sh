#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/git_push_robotics_fundamentals_lab.sh [repo_root] [branch]
# Behavior:
#   - If repo_root is omitted and current dir is inside a git repo, use that repo.
#   - Else fallback to "$HOME/robotics-fundamentals-lab".
if [[ $# -ge 1 ]]; then
  REPO_ROOT="$1"
else
  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT="$(git rev-parse --show-toplevel)"
  else
    REPO_ROOT="$HOME/robotics-fundamentals-lab"
  fi
fi

BRANCH="${2:-main}"
KEY_PATH="${GIT_KEY_PATH:-$HOME/.ssh/id_ed25519_github_robotics_fundamentals_lab}"
SSH_CONFIG_PATH="${GIT_SSH_CONFIG:-$HOME/.ssh/config}"

if [[ ! -d "$REPO_ROOT/.git" ]]; then
  echo "error: not a git repo: $REPO_ROOT" >&2
  exit 1
fi
if [[ ! -f "$KEY_PATH" ]]; then
  echo "error: ssh key not found: $KEY_PATH" >&2
  exit 1
fi
if [[ ! -f "$SSH_CONFIG_PATH" ]]; then
  echo "error: ssh config not found: $SSH_CONFIG_PATH" >&2
  exit 1
fi

cd "$REPO_ROOT"

echo "repo:   $REPO_ROOT"
echo "branch: $BRANCH"
echo "key:    $KEY_PATH"
echo "config: $SSH_CONFIG_PATH"

GIT_SSH_COMMAND="ssh -F \"$SSH_CONFIG_PATH\" -i \"$KEY_PATH\" -o IdentitiesOnly=yes -o UserKnownHostsFile=\"$HOME/.ssh/known_hosts\" -o StrictHostKeyChecking=accept-new" \
  git push origin "HEAD:$BRANCH"
