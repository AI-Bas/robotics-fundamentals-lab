# Vision Camera Documentation

This summary file describes the module-specific documentation container.

Detailed files of varying types (PDF, CAD, images, code examples, and notes) belong in the module-prefixed subfolders in this same directory.

## Source Of Truth

- Architecture and module plan: `docs/modules/camera-ai.md`
- Project conventions and naming: `docs/conventions.md`

Use `docs/` for authoritative architecture decisions about module behavior, system integration, and cross-module connections.
Use this folder for module-level external files and source links.

## Hardware Summary

The `vision_camera` module focuses on Raspberry Pi camera bring-up and AI-assisted perception experiments:

- local and remote camera stream bring-up
- low-rate HMI/browser preview stream plus control-oriented feature stream
- OpenCV experiments for soccer ball feature/seam tracking
- optional lighting control for repeatable visual calibration conditions

## Module Components Quick Reference

- Camera path: Raspberry Pi CSI camera (global-shutter target in architecture plan)
- Accelerator path: Raspberry Pi AI HAT+ (optional, profile-driven)
- Processing stack: OpenCV and model/runtime experiments
- Integration role: control-grade feature output + low-rate HMI preview feed

## Source URLs

- Raspberry Pi AI HAT+ docs: [Official documentation](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html)
- Architecture reference index: [Ball Rotation Architecture - Hardware and Vendor Reference Index](../../docs/ball-rotation-architecture.md)

## Latest Status Snapshot

- Status: `planned`
- Code artifacts present: `src/cam_smoke.py`, `src/cam_experimental.py`
- Architecture-level definition: `docs/modules/camera-ai.md`
- Backlog tracking: `docs/project-todo.md` under Camera and AI

## Cross-Reference Workflow

- Read `docs/ball-rotation-architecture.md` for dataflow and integration placement.
- Check `docs/project-todo.md` for current priority and blocked items.
- Use `docs/modules/camera-ai.md` for module-specific objectives.
- Use this file for component/source quick lookup and local files.

## Module-Prefixed Subfolders

- `vision_camera_datasheets/` (camera sensor and board docs, AI accelerator docs)
- `vision_camera_schematics/` (camera interface and power/wiring references)
- `vision_camera_cad/` (camera mount and alignment parts)
- `vision_camera_code_examples/` (vendor sample pipelines, camera utility examples)
- `vision_camera_calibration/` (intrinsics/extrinsics, lens and lighting notes)
- `vision_camera_notes/`

`vision-camera-documentation.md` remains a summary/index file only.

## Gaps To Fill Manually

- exact camera module model/revision references used in this build
- AI HAT+ hardware/software reference links matched to your version
- lens parameters, mounting geometry, and calibration datasets
- network and streaming constraints for your target ROS2/HMI deployment
