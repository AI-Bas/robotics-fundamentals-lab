# Modular I/O Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, CAD, images, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/modular-io.md`
- Project conventions and naming: `docs/conventions.md`

Use `docs/` as the authoritative design/planning source for module behavior, system integration, and cross-module connections.
Use this folder for module-specific external artifacts and quick navigation.

## Hardware Summary

The `modular_io` module uses the Maker Pi RP2040 board as a USB-connected coprocessor for fast, non-safety-critical I/O experiments and expansion workflows:

- serial/USB heartbeat and message exchange with Raspberry Pi host
- rapid prototyping with MicroPython (primary) and CircuitPython (fallback)
- external sensors and controls (for example ToF, ultrasonic, buttons, encoder, OLED)
- ROS2 bridge path for state publishing and command/UI integration

## Module Components Quick Reference

- Main board: Maker Pi RP2040 as USB serial coprocessor
- Interfaces: USB serial to host, Grove-style expansion I/O on board
- Typical attached peripherals: ToF, ultrasonic, encoder, buttons, OLED
- Integration role: auxiliary/non-critical I/O path

## Vendor Sources (Maker Pi RP2040)

- Datasheet: [Maker Pi RP2040 Datasheet](https://docs.google.com/document/d/1DJASwxgbattM37V4AIlJVR4pxukq0up25LppA8-z_AY/edit?tab=t.0)
- Schematic: [Maker Pi RP2040 Schematic (PDF)](https://drive.google.com/file/d/1Zp8GYO8x7ThObB1G8RIZx2YdqrXtdUc0/view)
- CircuitPython setup/download page: [CircuitPython board page](https://circuitpython.org/board/cytron_maker_pi_rp2040/)
- Manufacturer repository: [CytronTechnologies/MAKER-PI-RP2040](https://github.com/CytronTechnologies/MAKER-PI-RP2040)
- Product page and hardware resources: [Cytron product page](https://www.cytron.io/p-maker-pi-rp2040-simplifying-robotics-with-raspberry-pi-rp2040)

## Latest Status Snapshot

- Status: `planned`
- Code artifacts present: `src/io_smoke.py`, `src/io_experimental.py`
- Architecture-level definition: `docs/modules/modular-io.md`
- Backlog tracking: `docs/project-todo.md` under Modular I/O

## Cross-Reference Workflow

- For system behavior and inter-module integration, read `docs/ball-rotation-architecture.md` first.
- For current priorities and status, read `docs/project-todo.md`.
- For module implementation plan, read `docs/modules/modular-io.md`.
- Use this file as a quick external-reference index, then check local subfolders for latest vendor files.

## Module-Prefixed Subfolders

Place files inside these subfolders:

- `modular_io_datasheets/`
- `modular_io_schematics/`
- `modular_io_cad/`
- `modular_io_code_examples/`
- `modular_io_notes/`

`modular-io-documentation.md` remains a summary/index file only.

## Gaps To Fill Manually

- board revision used in this project (if different revisions exist)
- exact pin assignments and connector mapping for your current robot harness
- chosen firmware baseline (MicroPython/CircuitPython version and date)
- local copies/checksums of critical source documents for offline work
