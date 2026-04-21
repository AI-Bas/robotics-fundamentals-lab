# Robotics Fundamentals Lab

Monorepo for small, practical robotics experiments with a Raspberry Pi, focused on:

- terminal-first workflows
- reproducible troubleshooting
- disciplined Git usage for embedded development

## Current Focus

- `optical_flow/`: PAA5100JE (via `pmw3901` Python package) over SPI

## Working Style

- Develop directly on the Pi over SSH.
- Keep this workspace organized as a monorepo of small experiments.
- Commit often locally, push at meaningful milestones.

## Suggested Monorepo Structure

- `optical_flow/`
- `imu/`
- `motor_control/`
- `common/`
- `docs/`

## Git Discipline

- default branch: `main`
- feature branches: `feat/<topic>`
- fix branches: `fix/<topic>`

Example:

- `feat/paa5100-led-probe`
- `feat/paa5100-csv-logger`
- `fix/spi-reconnect-recovery`

## Frictionless Push Workflow

Use the helper script when your environment has multiple SSH keys:

```bash
./scripts/git_push_robotics_fundamentals_lab.sh
```

Recommended clone location for consistency on fresh Pi:

```bash
git clone git@github.com:AI-Bas/robotics-fundamentals-lab.git ~/robotics-fundamentals-lab
```

The helper script auto-detects repo root from your current directory, so it is safe even if folder names differ.

Optional arguments:

```bash
./scripts/git_push_robotics_fundamentals_lab.sh ~/robotics-fundamentals-lab main
```

Manual equivalent (good to practice):

```bash
GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_github_robotics_fundamentals_lab -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new' git push origin HEAD:main
```

### Manual Git Practice Loop

Run this sequence in your regular terminal or a dedicated git terminal:

```bash
git status -sb
git diff
git add -p
git commit -m "scope: short why-focused message"
git log --oneline -5
./scripts/git_push_robotics_fundamentals_lab.sh
```

Tips:
- use `git add -p` to stage only the exact hunks you want
- keep commits small and focused (easier rollback/review)
- push at checkpoints, not every save

## Session Handoff Notes

Use tracked handoff docs so session continuity is shared and reproducible:

- `docs/session-handoff.md` for the current concise restart state
- `docs/session-handoff-template.md` for the standard handoff structure
- `docs/workflow-rules.md` for low-context working conventions

## Python venv and Dependency Versioning

Use one project venv:

```bash
cd ~/robotics-fundamentals-lab/optical_flow
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

During development:
- pin critical/runtime-sensitive packages with minimum ranges if needed
- allow less-critical tooling to float (faster iteration)

At milestone or release:
- freeze exact versions for reproducibility:

```bash
python -m pip freeze > requirements-lock.txt
```

Recommended pattern for your roadmap (ROS2 + OpenCV + AI accelerator):
- keep `requirements.txt` human-curated for intent
- maintain `requirements-lock.txt` for reproducible milestone snapshots
- refresh lock file at each stable milestone

## Remote Access and Network Diagnostics

If Pi internet works on phone hotspot but not home Wi-Fi, likely causes are router/AP policies:
- client isolation (Wi-Fi clients blocked from LAN peers)
- DHCP/DNS mismatch
- firewall or subnet separation

Quick checks on Pi:

```bash
hostname
ip -br addr
ip route
cat /etc/resolv.conf
ping -c 3 8.8.8.8
ping -c 3 github.com
```

Quick checks on controlling machine:
- confirm both devices are on same subnet when using Wi-Fi directly
- test `ssh <pi-user>@<pi-ip>` by IP first (not hostname)
- if hostname fails but IP works, fix mDNS/DNS resolution

For stable sessions:
- use `tmux` on Pi (`tmux new -s robotics`)
- reconnect with `tmux attach -t robotics`
- keep one terminal for runtime logs and one for Git/edits

