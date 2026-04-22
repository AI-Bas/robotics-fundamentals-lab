# Modular I/O Module Plan

## Scope and Goal

Build a new `modular_io` module using the Maker Pi extension board as an auxiliary, hot-iterated sensor/control coprocessor.

This module starts lightweight in planning depth and will be expanded after core bring-up.

## Planned Directory

- Module directory: `modular_io/`

## Initial Objectives (Lightweight)

- establish robust USB connection between Maker Pi and Raspberry Pi
- evaluate MicroPython as default workflow, CircuitPython as fallback
- define serial protocol skeleton for data exchange
- validate basic external I/O read/write workflows

## Expected Device Roles

- ToF and ultrasonic experiments
- encoder and button based setpoint/parameter control
- small OLED status/menu rendering
- optional local indicators for subsystem health

## Integration Principles

- keep this module non-critical to motion control safety
- graceful degradation when device disconnects
- ROS2 bridge publishes states and receives UI updates/commands

## First Deliverables

- smoke script for serial link and heartbeat
- experimental script for mixed sensor/button/OLED tests
- protocol note defining message classes and timing expectations
