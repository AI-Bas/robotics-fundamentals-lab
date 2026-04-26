# Raspberry Pi 4 Platform Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, CAD, images, setup exports, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/rpi4-platform.md`
- Project conventions and naming: `docs/conventions.md`
- Bootstrap baseline: `docs/setup/bootstrap-and-tooling-baseline.md`

Use `docs/` as the authoritative planning source for system behavior, integration, and cross-module constraints.
Use this folder for module-level external assets and quick references.

## Hardware Summary

The `rpi4_platform` module captures board-specific setup and lifecycle management for Raspberry Pi 4 (8 GB) used as the primary headless compute node:

- OS and package baseline management
- interface enablement (I2C, SPI, UART, CSI camera)
- runtime stack provisioning (Python/C++, ROS2, OpenCV)
- network and HMI hosting setup baseline
- integration profile support for optional AI accelerators

## Module Components Quick Reference

- Main compute board: Raspberry Pi 4 (8 GB)
- Platform interfaces: I2C, SPI, UART, CSI camera, USB, Ethernet/Wi-Fi
- Cooling control target: PWM heatsink fan on dedicated fan header/GPIO path
- Accelerator path: Hailo AI accelerator HAT over PCIe (optional profile)

## Source URLs

- Raspberry Pi documentation portal: [Official documentation](https://www.raspberrypi.com/documentation/)
- Raspberry Pi AI HAT+ docs: [Official documentation](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html)
- Architecture reference index: [Ball Rotation Architecture - Hardware and Vendor Reference Index](../../docs/ball-rotation-architecture.md)

## Latest Status Snapshot

- Status: `doing`
- Code artifacts present: platform bootstrap scripts plus RPi-specific utility scripts
- Architecture-level definition: `docs/modules/rpi4-platform.md`
- Backlog tracking: `docs/project-todo.md` (platform orchestration items)
- Observed hardware note: system reports `BCM2712` in live status logs; verify whether deployed board is Pi 5-class platform while this module naming is currently `rpi4_platform`.
- Current fan mode target: set dedicated fan header to `auto` during bootstrap (`pwm1_enable=2`).

## Cross-Reference Workflow

- Start with `docs/ball-rotation-architecture.md` for system role and constraints.
- Confirm current execution priority in `docs/project-todo.md`.
- Use `docs/modules/rpi4-platform.md` for board-level responsibilities.
- Keep cross-platform setup in `scripts/bootstrap/` and board-specific helpers in `rpi4_platform/src/`.

## Module-Prefixed Subfolders

- `rpi4_platform_datasheets/`
- `rpi4_platform_schematics/`
- `rpi4_platform_cad/` (mounting and enclosure references)
- `rpi4_platform_code_examples/` (bootstrap and platform scripts)
- `rpi4_platform_setup_profiles/` (profile exports and environment baselines)
- `rpi4_platform_notes/` (field notes, troubleshooting, known-good states)

`rpi4-platform-documentation.md` remains a summary/index file only.

## Gaps To Fill Manually

- exact Pi OS image and kernel baseline for your deployment
- chosen network policy (Wi-Fi country, hostnames, static DHCP/IP)
- camera and AI accelerator hardware revision specifics
- final bring-up checklist with observed vs expected validation outputs
- dedicated fan header control reference and validated runtime policy (auto/manual, thresholds, expected RPM)
