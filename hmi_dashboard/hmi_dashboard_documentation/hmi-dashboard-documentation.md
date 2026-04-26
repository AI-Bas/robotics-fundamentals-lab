# HMI Dashboard Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, CAD, images, setup exports, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/hmi-dashboard.md`
- Project conventions and naming: `docs/conventions.md`
- Bootstrap baseline: `docs/setup/bootstrap-and-tooling-baseline.md`

Use `docs/` as the authoritative planning source for module behavior, integration, and cross-module constraints.
Use this folder for HMI-specific assets and references.

## Hardware and Runtime Summary

The `hmi_dashboard` module provides a task-adaptive UI that runs:

- locally on Raspberry Pi HDMI touchscreen
- remotely in browser clients over Ethernet/Wi-Fi

The same app instance serves both targets and supports page layout switching by task context (configuration, calibration, run modes, and modular I/O toolkit).

## Module Components Quick Reference

- Runtime framework: Streamlit application (`src/app.py`)
- Layout engine: profile-driven section map (`config/layout_profiles.yaml`)
- Deployment modes: local touchscreen kiosk and remote browser mirror
- Integration role: operator and diagnostics surface, not control-critical runtime

## Source URLs

- Streamlit documentation: [Official docs](https://docs.streamlit.io/)
- Plotly Python documentation: [Official docs](https://plotly.com/python/)
- Architecture reference index: [Ball Rotation Architecture](../../docs/ball-rotation-architecture.md)

## Latest Status Snapshot

- Status: `doing`
- Code artifacts present: app scaffold, profile config, reusable sections, launcher script
- Architecture-level definition: `docs/modules/hmi-dashboard.md`
- Backlog tracking: `docs/project-todo.md` under ROS2 and HMI Integration

## Cross-Reference Workflow

- Start at `docs/ball-rotation-architecture.md` for UI role in system dataflow.
- Use `docs/project-todo.md` to confirm active HMI integration tasks.
- Use `docs/modules/hmi-dashboard.md` for module-level scope and contracts.
- Use this file for component quick reference and local asset locations.

## Module-Prefixed Subfolders

- `hmi_dashboard_datasheets/`
- `hmi_dashboard_schematics/`
- `hmi_dashboard_cad/`
- `hmi_dashboard_code_examples/`
- `hmi_dashboard_setup_profiles/`
- `hmi_dashboard_notes/`

`hmi-dashboard-documentation.md` remains a summary/index file only.

## Gaps To Fill Manually

- touchscreen model, resolution, and orientation settings
- kiosk launch strategy and auto-start service details
- final HMI page/state model and per-role access expectations
- integration event/telemetry contracts with ROS2 nodes
