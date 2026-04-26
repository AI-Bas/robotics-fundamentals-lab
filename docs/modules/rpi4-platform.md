# Raspberry Pi 4 Platform Module Plan

## Scope and Goal

Establish a stable, repeatable platform layer for Raspberry Pi 4 (8 GB) bring-up and ongoing runtime management.

This module focuses on board-level provisioning and integration boundaries so functional modules can remain portable.

## Planned Directory

- Module directory: `rpi4_platform/`

## Functional Areas

### A. Base system provisioning

- define Pi OS baseline and package sets by role (dev, runtime, headless)
- maintain deterministic bootstrap sequence for fresh boards
- track software versions and update policy

### B. Interface bring-up

- enable and validate I2C, SPI, UART, and CSI interfaces
- provide validation scripts and expected outputs
- capture known failure signatures and recovery steps
- include dedicated fan-header control validation path distinct from GPIO PWM fallback

### C. Runtime stack

- Python runtime and virtual environment conventions
- C++ toolchain baseline
- ROS2 baseline package set and environment activation pattern
- OpenCV baseline package set and camera validation checks

### D. Network and HMI baseline

- SSH-first workflow and reliability checks
- hostname and network configuration policy
- lightweight HMI hosting path for calibration and diagnostics views

### E. Optional accelerator integration

- define profile-driven setup hooks for AI accelerator hardware
- keep accelerator logic optional and isolated from core bring-up

## ROS2 and Module Integration Contract

- expose board capabilities as explicit config/profile values
- keep module scripts free of hard-coded board assumptions
- support profile layering for future SBC replacements

## First Deliverables

- board bootstrap script with dry-run and apply modes
- profile files for generic Linux and Raspberry Pi defaults
- board validation checklist and smoke commands
- template path for additional SBC profiles
- dedicated fan-header smoke/monitor script and policy notes
