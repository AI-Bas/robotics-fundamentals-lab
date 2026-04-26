# HMI Dashboard Module Plan

## Scope and Goal

Create a flexible operator HMI that can run on local Raspberry Pi touchscreen and be mirrored to remote browsers over LAN/Wi-Fi.

The HMI should switch layout and controls by task context while keeping integration contracts with module backends explicit.

## Planned Directory

- Module directory: `hmi_dashboard/`

## Functional Areas

### A. Dual-target UI serving

- single app process serves local and remote clients
- local mode optimized for touch interaction
- remote mode optimized for monitoring and support workflows

### B. Task-driven layout profiles

- configuration profile for system and module setup
- calibration profile for guided procedures and live graphs
- run-mode profile for operation control and health status
- modular I/O profile for low-level I/O diagnostics/actions

### C. Data and integration boundaries

- subscribe to module state snapshots and diagnostics feeds
- issue bounded user actions to backend services
- keep core logic in backend modules, not in UI layer

### D. Deployment and startup

- support manual launch for development
- support auto-start kiosk mode for field operation
- keep network access configuration explicit and documented

## ROS2 and Backend Contract

- define transport path for command and telemetry exchange
- define field schema for status, warnings, and calibration progress
- separate control-critical paths from HMI-only paths

## First Deliverables

- Streamlit scaffold with profile-driven sections
- placeholder interactive charts and controls
- configuration profile loader with safe fallback behavior
- deployment note for local + remote access pattern
