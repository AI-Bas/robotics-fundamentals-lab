# Next Chat Handoff (Current Workflow)

## Current State (Relevant)

- Main branch has local commits ahead of remote and includes:
  - `of_experimental.py` (experimental wrapper and advanced experiments)
  - `of_graph.py` (plotting trends from logs)
  - centralized advanced sensor helpers in `of_sensor.py`
  - minimal `pytest` scaffold in `optical_flow/tests/`
- Deprecated `of_first_test.py` has been removed.
- Target runtime remains ROS2 C++ later; Python is for diagnostics/calibration/prototyping now.
- Dedicated diagnostics `hb-tune` mode is intentionally deferred (tracked as future feature).

## Git + SSH Workflow (Cursor Machine)

- Remote uses SSH alias:
  - `origin = git@github-robotics:AI-Bas/robotics-fundamentals-lab.git`
- Alias config exists in `~/.ssh/config` and authentication works.
- Quick verification commands:

```bash
ssh -T git@github-robotics
git -C ~/robotics remote -v
git -C ~/robotics status -sb
```

- If push fails, check:
  1. internet connectivity on this machine
  2. `~/.ssh/config` still contains `Host github-robotics`
  3. correct key path and permissions (`chmod 600 ~/.ssh/id_*`)

## Pi Networking Note (Ethernet via PC Wi-Fi Sharing)

- This workflow is valid and should work consistently.
- Stable startup habits:
  - keep one persistent terminal multiplexer session on Pi (`tmux`)
  - avoid reconnecting from scratch each time
  - run code from repo on Pi only for hardware tests; do heavy edits from Cursor machine

## Session Start Commands (Pi)

```bash
cd ~/robotics/optical_flow
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python src/of_sensor_smoke.py --samples 10
```

## Core Run Commands

```bash
# experimental capability checks
python src/of_experimental.py --mode probe
python src/of_experimental.py --mode burst --samples 20 --sample-period 0.03
python src/of_experimental.py --mode frame --samples 5

# diagnostics / logs
python src/of_diagnostics.py --mode stream-log --stream-seconds 60 --stream-target-hz 30 --log-dir logs
python src/of_diagnostics.py --mode rate-sweep --sweep-start-hz 10 --sweep-stop-hz 140 --sweep-step-hz 10 --sweep-hold-s 2 --log-dir logs

# graph analysis
python src/of_graph.py --log-dir logs --out-dir logs/plots
```

## Next Priorities

1. Capture reference-surface datasets (constant known velocity and varied lighting).
2. Compare sweep/stream stability versus LED brightness and polling rate.
3. Calibrate `counts_to_mps_scale` and update ROS2 profile export inputs.
4. Add ROS2-phase `hb-tune` mode once runtime integration starts.

