# Project TODO Snapshot (2026-04-23)

Source at snapshot time: `docs/project-todo.md`  
Purpose: preserve migration checkpoint of the active backlog.

## Snapshot

### Module Switchboard

- Optical flow: `docs/modules/optical-flow.md`
- Power monitor: `docs/modules/power-monitor.md`
- Camera and AI: `docs/modules/camera-ai.md`
- Modular I/O: `docs/modules/modular-io.md`
- Motor control: `docs/modules/motor-control.md`
- ROS2 and HMI integration: `docs/modules/ros2-hmi-integration.md`
- Shared conventions: `docs/conventions.md`

### Status Legend

- `todo`: not started
- `doing`: active now
- `blocked`: waiting on hardware/info
- `done`: completed and validated

### Today Focus

- Active module: `optical_flow`
- Current objective: finish optical-flow polish and lock interfaces before building new modules.
- Exit criteria:
  - `of_main.py` usage and argument flow documented.
  - `of_experimental.py` redundancy decisions documented.
  - LDR LUT experiment pipeline drafted and ready for Maker Pi ADC wiring.

### Backlog By Module

#### Optical Flow (Priority 1)

- `doing` Add primary CLI usage guidance for `of_main.py` including SSH run examples.
- `todo` Review `of_experimental.py` and keep only truly experimental entrypoints.
- `todo` Define LDR feedback experiment script and data format for LUT generation.
- `todo` Define Neopixel ring integration strategy for calibration lighting control.
- `todo` Consolidate naming, comments, and argument consistency across all `of_*` scripts.
- `todo` Define ROS2-ready optical flow outputs and parameter profile contract.

#### Power Monitor (Priority 2)

- `todo` Create `power_monitor/` module structure and starter docs.
- `todo` Define INA219 4-channel smoke test and baseline polling checks.
- `todo` Define shunt replacement scaling update method and register conversion notes.
- `todo` Define multimeter-referenced calibration protocol and acceptance limits.
- `todo` Define polling bandwidth optimization and I2C bus protection strategy.
- `todo` Define logging and graph outputs and ROS2 mapping for safety events.

#### Camera and AI (Priority 3)

- `todo` Create `vision_camera/` module structure and starter docs.
- `todo` Define local and SSH camera feed bring-up path.
- `todo` Define low-rate browser/HMI feed path separate from high-rate processing.
- `todo` Document AI HAT setup assumptions and validation checkpoints.
- `todo` Draft first object/ball seam tracking experiment outputs.

#### Modular I/O (Priority 4)

- `todo` Create `modular_io/` module structure and starter docs.
- `todo` Define USB serial protocol shape for Maker Pi to Pi data exchange.
- `todo` Define MicroPython/CircuitPython evaluation criteria and default choice.
- `todo` Define first ToF/ultrasonic and buttons/encoder/OLED smoke tests.
- `todo` Define ROS2 bridge requirements for modular sensor/control data.

#### Motor Control (Priority 5)

- `todo` Expand `motor_control/` docs and C++-first implementation plan.
- `todo` Define communication fallback matrix (packet serial, USB bench-only, alternatives).
- `todo` Define smoke tests and telemetry baseline for encoder and driver status.
- `todo` Define calibration and bandwidth optimization plan for high-rate feedback.
- `todo` Define safety-state handling: estop, overvoltage, faults, brownout recovery.
- `todo` Define runtime parameter tuning surface (PID, setpoints, limits).

#### ROS2 and HMI Integration (Priority 6)

- `todo` Define node boundaries and topic/service contracts across modules.
- `todo` Define profile and preset management strategy.
- `todo` Define local touchscreen HMI and remote mirrored browser deployment flow.
- `todo` Define centralized observability: logging, trend plots, event timeline.
- `todo` Define integration smoke test for full-platform startup and degraded modes.
