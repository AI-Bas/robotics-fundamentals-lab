# ROS2 Core Module Plan

## Scope and Goal

Build a dedicated `ros2_core` module to manage ROS2 graph architecture, launch strategy, and inter-module contracts.

This module owns integration framework behavior and keeps module-specific logic in each module folder.

## Planned Directory

- Module directory: `ros2_core/`

## Functional Areas

### A. Interface contracts

- define topic/service/action contracts for each module boundary
- define units, timestamps, rates, and fault field semantics
- define compatibility/versioning policy for contract updates

### B. Launch and composition

- create launch profiles for development, calibration, and full runtime
- support module-on/module-off composition for staged bring-up
- define startup ordering and health checks

### C. Diagnostics and fault orchestration

- aggregate module health and fault states
- publish global diagnostics summary
- maintain event timeline hooks for HMI and logging

### D. HMI backend integration

- provide clean transport path for HMI state and operator commands
- keep control-critical loops decoupled from UI transport
- define low-rate HMI feeds separate from high-rate control data

## First Deliverables

- ROS2 contract draft (topics/services/actions)
- launch profile skeleton
- integration smoke launcher for module heartbeats
- diagnostics rollup prototype
