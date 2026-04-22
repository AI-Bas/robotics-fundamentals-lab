# Motor Control Module Plan

## Scope and Goal

Expand `motor_control` into a C++-first, ROS2-ready motor interface with high-bandwidth feedback handling and robust safety behavior.

Primary hardware context:

- two RoboClaw 2x15A controllers
- multiple brushed DC motors with encoder feedback
- custom breakout and external safety wiring

## Planned Directory

- Module directory: `motor_control/`

## Functional Areas (Detailed)

### A. Communication reliability path

- prioritize packet-serial operational path
- keep USB for configuration/bench fallback workflows
- define fallback matrix and troubleshooting runbook

### B. C++ interface layer

- implement deterministic command and telemetry loop
- replace deprecated/inconsistent Python control path
- define clean API boundaries for ROS2 node integration

### C. Telemetry and control surface

- stream encoder counts, position, velocity, acceleration
- stream driver status and error flags
- support runtime parameter updates (PID, setpoints, limits)

### D. Safety and error handling

- estop state handling and software recovery behavior
- overvoltage and back-EMF event diagnostics
- brownout/comms-loss fallback behavior
- command watchdog and safe output shutdown

### E. Calibration and optimization

- smoke test for command/readback path
- calibration routine for encoder scaling and response checks
- bandwidth optimization and loop-rate validation
- logging and graphing for tuning and troubleshooting

## ROS2 Readiness Contract

- command interfaces for enable, disable, setpoint, and mode
- state topics with timestamps and quality/fault flags
- diagnostics channel for fault escalation and event history

## First Deliverables

- communication smoke test utility
- telemetry logger and graph tool
- C++ node skeleton with command + state roundtrip
