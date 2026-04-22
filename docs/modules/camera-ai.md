# Camera and AI Module Plan

## Scope and Goal

Build a new `vision_camera` module for Raspberry Pi global shutter camera bring-up, remote viewing, and AI-assisted vision experiments.

This module starts lightweight in planning depth and will be expanded after initial bring-up.

## Planned Directory

- Module directory: `vision_camera/`

## Initial Objectives (Lightweight)

- establish local video feed access on the Pi
- establish remote access over SSH workflow
- define browser/HMI low-rate feed pathway
- verify AI HAT+ software stack assumptions and setup checkpoints

## Vision Experiment Targets

- detect and track soccer ball in camera frame
- extract seam/features for rotation cues
- estimate translation and rotational motion indicators
- output feature stream suitable for ROS2 feedback use

## Lighting and Robustness

- include optional Neopixel ring usage for scene illumination control
- document calibration presets for low/high ambient conditions

## ROS2 Output Split

- control-oriented stream: compact feature outputs at higher rate
- HMI-oriented stream: low-resolution/low-fps feed for browser display

## First Deliverables

- smoke script for camera feed and basic frame capture
- experimental vision script for ball/feature detection
- logging scaffold for frame metadata and detected features
