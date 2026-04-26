# Optical Flow Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, CAD, images, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/optical-flow.md`
- Project conventions and naming: `docs/conventions.md`

Use `docs/` as the authoritative planning source for module behavior, system integration, and cross-module connections.
Keep local files and quick links here.

## Hardware Summary

The `optical_flow` module is centered on the PAA5100JE optical flow sensor over SPI on Raspberry Pi, with calibration and diagnostics paths for ROS2-ready integration:

- motion delta and derived flow metrics from SPI reads
- diagnostics, benchmark, rate sweep, and logging workflow
- calibration path for counts-to-velocity scaling
- optional illumination/LED tuning experiments

## Module Components Quick Reference

- Sensor class: PAA5100JE optical flow sensor breakout
- Host interface: SPI on Raspberry Pi 4
- Supporting parts: illumination tuning path, optional external ring lighting
- Integration role: motion-related feature input for supervisor and ROS2 diagnostics

## Source URLs

- Architecture reference index: [Ball Rotation Architecture - Hardware and Vendor Reference Index](../../docs/ball-rotation-architecture.md)
- Implementation and usage source: [optical_flow README](../README.md)

## Latest Status Snapshot

- Status: `doing`
- Primary active code area: `optical_flow/src`
- Known active focus: CLI polish, experimental cleanup, LUT calibration planning
- Backlog tracking: `docs/project-todo.md` under Optical Flow

## Cross-Reference Workflow

- Start at `docs/ball-rotation-architecture.md` for integration context.
- Confirm active priorities in `docs/project-todo.md`.
- Use `docs/modules/optical-flow.md` for module behavior and readiness contracts.
- Use this file for quick component/source lookup and local artifact locations.

## Module-Prefixed Subfolders

- `optical_flow_datasheets/`
- `optical_flow_schematics/`
- `optical_flow_cad/` (sensor bracket, standoff, and alignment models)
- `optical_flow_code_examples/` (vendor/community references and validated snippets)
- `optical_flow_calibration_references/` (surface notes, height references, controlled test notes)
- `optical_flow_notes/`

`optical-flow-documentation.md` remains a summary/index file only.

## Gaps To Fill Manually

- authoritative vendor datasheet links/files for your exact PAA5100JE breakout
- board-level schematic or pinout references for the specific breakout variant
- mechanical alignment constraints and mounting tolerances used on your robot
- known-good firmware/library versions used during each calibration campaign
