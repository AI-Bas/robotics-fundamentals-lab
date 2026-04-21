# HMI and Remote Workflow Plan

## Goal

Run the robotics stack on a headless Raspberry Pi connected to a dedicated touchscreen, while allowing remote monitoring and development from a client machine (Windows + Cursor).

## Architecture Direction

- **Lab side (Pi runtime)**: hardware drivers, control loops, local HMI rendering, local logs.
- **Client side (remote operator/dev)**: monitoring UI, log review, tuning/config edits, deployment triggers.
- **Shared protocol**: stable API/events so both local touchscreen and remote client use the same runtime state model.

## Repository Layout Direction

Keep hardware and client responsibilities clearly separated:

- `lab/` (or keep extending current Pi-focused folders): sensor/runtime/control services.
- `hmi/`: local touchscreen front-end (can be same codebase as remote UI with a different launch profile).
- `client/`: remote monitoring/control app (desktop/web).
- `common/`: shared schemas (messages, command contracts, status DTOs).
- `docs/`: operational runbooks and deployment notes.

## Runtime Pattern

- Pi runs the authoritative runtime process.
- HMI reads runtime state over loopback/local network API.
- Remote client reads the same API over Wi-Fi/Ethernet.
- Commands are explicit (start/stop mode, calibration, test actions), authenticated, and logged.

## Cursor-Friendly Development Flow

- Keep **Pi clone** for hardware integration and smoke tests.
- Keep **Windows clone** for client/HMI feature work and review.
- Use small, scoped branches and push frequently to share state between both machines.
- Maintain repeatable scripts for:
  - Pi smoke tests
  - Pi deployment/restart
  - client build/test
  - quick remote connection checks

## Near-Term Milestones

1. Lock a minimal runtime API contract in `common/`.
2. Add a tiny local HMI status panel (sensor health, loop rate, connectivity).
3. Add remote read-only monitoring client against same API.
4. Add authenticated remote control actions for safe operations.
5. Add deployment scripts for Pi service restart + health check.
