# Power Monitor Module Plan

## Scope and Goal

Build a new `power_monitor` module for development and experimentation with the Waveshare 4-channel INA219 board.

Primary role:

- provide independent voltage/current/power safety telemetry
- support calibration after shunt replacement
- provide ROS2-ready safety outputs for motor supervision

## Planned Directory and Naming

- Module directory: `power_monitor/`
- Python script prefix: `pwr_<script_name>.py`

## Functional Areas (Detailed)

### A. Bring-up and smoke test

- verify I2C visibility and device responses
- implement channel-by-channel read checks
- output clear pass/fail summary with error hints

### B. Shunt replacement and scaling

- document original shunt assumptions and new shunt targets
- define conversion updates for current and power calculations
- define register-to-unit conversion constants and formulas per channel

### C. Calibration protocol

- use multimeter reference for voltage/current validation
- capture offset and gain corrections per channel
- define acceptance bounds and repeatability criteria

### D. Polling and bandwidth optimization

- test stable polling rates across one-to-four channels
- evaluate bus contention and retry/error behavior
- define recommended production poll rates and safety margins

### E. Logging and graphing

- structured CSV/JSON logs with timestamps and channel IDs
- graph scripts for trend analysis and threshold validation
- event markers for threshold crossings and sustained faults

### F. SMBus decision record

- evaluate SMBus usage path versus current Python approach
- record clear decision rationale (adopt or reject)
- include criteria: stability, maintainability, and control-loop suitability

## ROS2 Readiness Contract

- publish channel telemetry with units and quality flags
- publish fault-state recommendations:
  - overcurrent persistent
  - undervoltage persistent
  - sensor read failure
- define configurable thresholds and dwell times

## First Deliverables

- `pwr_smoke.py` for board/channel health
- `pwr_experimental.py` for exploratory reads and timing tests
- `pwr_calibration.py` for reference matching workflow
- `pwr_log.py` and `pwr_graph.py` for diagnostics outputs
