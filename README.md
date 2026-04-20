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

