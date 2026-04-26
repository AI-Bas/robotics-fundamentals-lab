# Next Chat Handoff

## Snapshot

- Branch: `main`
- Sync: validated locally; push `main` after this handoff update
- Primary focus: clean canonical repo/network starting point
- Last validated command: `ssh -T github-robotics-fundamentals-lab`
- Blocking issue: none observed

## Current State

- **Done**
  - Canonical repo path confirmed: `~/robotics-fundamentals-lab`.
  - Alias symlinks removed: `~/robotics` and `~/robotics-fundementals-lab`.
  - Project docs consolidated (`architecture`, `project-todo`, `conventions`, module docs).
  - Stale `~/robotics/optical_flow` README reference corrected to the canonical path.
  - Pi network verified on `eth0` (`192.168.1.207`) and `wlan0` (`192.168.1.208`) in the same subnet.
- **In progress**
  - Continue module implementation from the canonical workspace.
- **Not started**
  - Hardware-level Linksys throughput/AP-mode validation, if needed.

## Validation

- Commands:
  - `git status --short --branch`
  - `ls -ld /home/s3p/robotics-fundamentals-lab /home/s3p/robotics /home/s3p/robotics-fundementals-lab`
  - `rg "~/robotics/|/home/s3p/robotics/|robotics-fundementals|fundementals"`
  - `ping -c 2 192.168.1.1 && ping -c 2 1.1.1.1 && ping -c 2 github.com`
  - `ssh -T github-robotics-fundamentals-lab`
- Observed:
  - canonical folder exists; old alias/misspelled paths do not exist
  - repo is on `main` with no uncommitted changes before this handoff refresh
  - gateway, DNS, internet, and GitHub SSH authentication succeeded
- Confidence: high for repo/path/internet checks; medium for physical router mode because that requires router UI or throughput testing

## Next Action

```bash
cd ~/robotics-fundamentals-lab
git status -sb
cd optical_flow
source .venv/bin/activate
```

## Risks / Assumptions

- Current Pi routes prefer `eth0` over `wlan0`; keep that if Ethernet should be primary.
- Linksys E1200 appears not to create a separate subnet for the Pi, but AP/bridge mode should be confirmed in its admin UI.

## Process Rules

- Use concise handoff format from `docs/session-handoff-template.md`.
- Follow general workflow standards in `docs/workflow-rules.md`.
- Track medium/long-term work in `docs/project-todo.md`.
- Follow system targets in `docs/ball-rotation-architecture.md`.
- Follow naming and structure from `docs/conventions.md`.

