# ROS2 Core Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, diagrams, setup exports, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/ros2-core.md`
- Project conventions and naming: `docs/conventions.md`
- System architecture: `docs/ball-rotation-architecture.md`

Use `docs/` as the authoritative source for integration behavior and cross-module contracts.

## Module Components Quick Reference

- ROS2 graph contracts (topics/services/actions)
- launch orchestration and profile selection
- diagnostics rollup and event timeline integration
- boundary layer between module runtimes and HMI/backend views

## Source URLs

- ROS2 documentation: [Official docs](https://docs.ros.org/)
- Architecture reference: [Ball Rotation Platform Architecture](../../docs/ball-rotation-architecture.md)

## Latest Status Snapshot

- Status: `planned`
- Code artifacts present: scaffolding only
- Architecture-level definition: `docs/modules/ros2-core.md`
- Backlog tracking: `docs/project-todo.md` under ROS2 Core and HMI Integration

## Cross-Reference Workflow

- Read `docs/ball-rotation-architecture.md` first for global integration contracts.
- Read `docs/project-todo.md` for active integration priorities.
- Use `docs/modules/ros2-core.md` for module-level boundaries and deliverables.
- Use this file for quick reference links and local artifacts.

## Module-Prefixed Subfolders

- `ros2_core_datasheets/`
- `ros2_core_schematics/`
- `ros2_core_cad/`
- `ros2_core_code_examples/`
- `ros2_core_setup_profiles/`
- `ros2_core_notes/`

`ros2-core-documentation.md` remains a summary/index file only.
