# Motor Control Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, CAD, images, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/motor-control.md`
- Project conventions and naming: `docs/conventions.md`

`docs/` remains the canonical architecture and planning location for module behavior, system integration, and cross-module connections.
This folder is for module-specific external assets and references.

## Hardware Summary

The `motor_control` module targets a C++-first, ROS2-ready integration path for RoboClaw-based brushed DC motor control:

- deterministic command/telemetry loops
- packet serial preferred with fallback communication workflows
- encoder/state/fault telemetry surfaces
- safety handling for estop, brownout/comms loss, and watchdog shutdown

## Module Components Quick Reference

- Motor controllers: RoboClaw 2x15A (dual controller target in architecture docs)
- Actuation set: brushed DC motors with encoder feedback
- Communication target: packet serial primary, USB fallback for bench/service
- Integration role: control-critical actuation endpoint with strict safety behavior

## Source URLs

- RoboClaw product: [Basicmicro RoboClaw 2x15A](https://www.basicmicro.com/RoboClaw-2x15A-Motor-Controller_p_10.html)
- Maxon RE25 (`339152`): [Catalog page](https://www.maxongroup.nl/medias/sys_master/root/9398012936222/Cataloge-Page-EN-157.pdf)
- Maxon GP26B (`144027`): [Catalog page](https://www.maxongroup.com/medias/sys_master/root/8807110869022/13-382-EN.pdf)
- Maxon MR ML 500 CPT (`225778`): [Catalog page](https://www.maxongroup.co.uk/medias/sys_master/root/8883965493278/EN-21-478.pdf)
- Maxon DCX35L GB KL: [Catalog page](https://www.maxongroup.com/medias/sys_master/root/9394602868766/Cataloge-Page-EN-118.pdf)
- Maxon GPX42 4.3:1: [Catalog page](https://www.maxongroup.com/medias/sys_master/root/9406823268382/Cataloge-Page-EN-405.pdf)
- Maxon ENX16 EASY (`499359`): [Catalog page](https://www.maxongroup.com/medias/sys_master/root/8883962413086/EN-21-464-465.pdf)

## Latest Status Snapshot

- Status: `planned`
- Code artifacts present: documentation scaffolding only
- Architecture-level definition: `docs/modules/motor-control.md`
- Backlog tracking: `docs/project-todo.md` under Motor Control

## Cross-Reference Workflow

- For control-path constraints and safety policy, read `docs/ball-rotation-architecture.md`.
- For current execution priority and blockers, read `docs/project-todo.md`.
- For module-specific implementation plan, read `docs/modules/motor-control.md`.
- Use this file to locate part references and local detailed files quickly.

## Module-Prefixed Subfolders

- `motor_control_datasheets/` (RoboClaw controller docs, motor datasheets)
- `motor_control_schematics/` (wiring diagrams, power/safety interconnects)
- `motor_control_cad/` (mounting plates, enclosure parts)
- `motor_control_code_examples/` (vendor SDK/examples, protocol snippets)
- `motor_control_safety/` (fault matrix, estop behavior notes, validation evidence)
- `motor_control_notes/`

`motor-control-documentation.md` remains a summary/index file only.

## Gaps To Fill Manually

- exact RoboClaw model/revision documents and command references in use
- wiring harness and safety-chain schematic for your current robot build
- motor + encoder model datasheets and calibration constants
- packet serial baud/address matrix and fallback procedure confirmation
