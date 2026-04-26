# ROS2 Core Module

Development area for ROS2 graph architecture, launch orchestration, and module integration contracts.

## Goals

- define stable ROS2 topic/service/action contracts across modules
- centralize launch profiles and runtime composition rules
- manage diagnostics aggregation and fault-state rollup paths
- support staged integration from module smoke tests to full-system startup

## Starter Paths

- `src/` ROS2 helper scripts and orchestration utilities
- `config/` launch and profile configuration files
- `logs/` runtime integration and diagnostics logs
- `tests/` contract and integration checks

## Documentation

- Module-local hardware/source references: `ros2_core_documentation/ros2-core-documentation.md`
- Architecture source of truth: `../docs/modules/ros2-core.md`
