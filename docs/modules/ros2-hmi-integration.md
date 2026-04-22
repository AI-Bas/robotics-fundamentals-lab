# ROS2 and HMI Integration Plan

## Scope and Goal

Define final system integration where all module outputs are orchestrated through ROS2 and exposed through local and remote HMI paths.

## Integration Objectives

- stable node boundaries and interface contracts
- profile-based runtime parameter management
- local touchscreen HMI for direct operation
- mirrored remote browser access
- unified observability for status, faults, and trends

## Planned Node Groups

- `motion_supervisor_node`
- `motor_control_node`
- `optical_flow_node`
- `power_monitor_node`
- `vision_pipeline_node`
- `makerpi_bridge_node`
- `hmi_backend_node`
- `diagnostics_node`

## Dataflow Principles

- keep high-rate control feedback paths compact and low-latency
- expose low-rate human-facing streams separately for HMI
- use explicit fault-state channels rather than implicit error parsing

## HMI Responsibilities

- control and mode switching
- safety state visualization
- live telemetry summaries
- troubleshooting event timeline and log access
- profile selection and parameter visibility

## Integration Smoke Test

- start all nodes with a baseline profile
- verify heartbeat and diagnostics rollup
- verify one command round-trip through supervisor and motor module
- verify sensor telemetry arrival for optical flow and power monitor
- verify low-rate camera feed visible in HMI
- verify degraded-mode behavior when one non-critical module is dropped
