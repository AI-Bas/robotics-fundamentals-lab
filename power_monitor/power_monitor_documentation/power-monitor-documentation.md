# Power Monitor Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, CAD, images, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/power-monitor.md`
- Project conventions and naming: `docs/conventions.md`

`docs/` remains authoritative for module architecture, system integration, and cross-module decisions.
This folder is for module-specific source artifacts and quick navigation.

## Hardware Summary

The `power_monitor` module uses a Waveshare 4-channel INA219 board to provide independent electrical telemetry and ROS2 safety signals:

- per-channel voltage/current/power telemetry
- shunt-aware scaling and calibration workflow
- polling-rate and I2C stability characterization
- threshold-based fault outputs for safety supervision

## Module Components Quick Reference

- Sensor board: Waveshare Current/Power Monitor HAT (INA219, 4-channel)
- Interface: I2C on Raspberry Pi
- Core outputs: channel voltage/current/power + threshold fault recommendations
- Integration role: electrical safety telemetry for motion supervision

## Source URLs

- Waveshare wiki: [Current/Power Monitor HAT](https://www.waveshare.com/wiki/Current/Power_Monitor_HAT)
- Architecture reference index: [Ball Rotation Architecture - Hardware and Vendor Reference Index](../../docs/ball-rotation-architecture.md)

## Latest Status Snapshot

- Status: `planned`
- Code artifacts present: `src/pwr_smoke.py`, `src/pwr_experimental.py`
- Architecture-level definition: `docs/modules/power-monitor.md`
- Backlog tracking: `docs/project-todo.md` under Power Monitor

## Cross-Reference Workflow

- Read `docs/ball-rotation-architecture.md` for safety and escalation context.
- Read `docs/project-todo.md` for active module sequencing and status.
- Use `docs/modules/power-monitor.md` for implementation and calibration plan.
- Use this file for rapid source lookup and artifact folder navigation.

## Module-Prefixed Subfolders

- `power_monitor_datasheets/` (INA219 and board-level docs)
- `power_monitor_schematics/` (board schematic and wiring harness notes)
- `power_monitor_cad/` (mounting and enclosure references)
- `power_monitor_code_examples/` (vendor examples and validated adaptation snippets)
- `power_monitor_calibration/` (multimeter references, offset/gain records, acceptance criteria)
- `power_monitor_notes/`

`power-monitor-documentation.md` remains a summary/index file only.

## Gaps To Fill Manually

- exact Waveshare board revision docs and any variant-specific behavior
- final shunt values per channel and converted scaling constants
- calibration evidence files tied to date/load conditions
- fault threshold setpoints and dwell timings selected for deployment
