# Power Monitor Module

Development area for the Waveshare Current/Power Monitor HAT (INA219, 4 channels).

## Goals

- smoke test the I2C board and all channels
- validate voltage/current/power conversion
- support shunt replacement and recalibration
- provide logs and graphs for troubleshooting
- prepare clean ROS2 node interfaces

## Script Naming

All scripts use:

- `pwr_<script_name>.py`

## Starter Scripts

- `src/pwr_smoke.py`
- `src/pwr_experimental.py`

## Next Steps

- implement per-channel read pipeline with structured logs
- implement multimeter calibration protocol capture
- implement polling-rate optimization and bus stability checks

## Detailed Development Plan

### 1) INA219 scaling and shunt replacement

- document original board scaling assumptions
- add configurable shunt values per channel
- implement register conversion path to output corrected SI units

### 2) Calibration protocol

- compare board outputs to multimeter references at multiple loads
- estimate per-channel offset and gain correction
- record calibration artifacts in machine-readable files

### 3) Polling and I2C stability

- benchmark single-channel and all-channel polling at increasing rates
- track read failures, retries, and bus error rates
- define recommended poll rates with safety margin

### 4) Smoke, logging, and ROS2 readiness

- smoke script validates board presence and all channels
- logging script records voltage/current/power and threshold events
- graph script visualizes trends and fault windows
- ROS2 contract includes telemetry fields, units, and fault states
