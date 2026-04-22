# Project Conventions

## Purpose

Use this file as the authoritative reference for naming, layout, logging, and documentation patterns across the full project.

## Naming Conventions

- Python files: `snake_case.py`
- Optical flow scripts: `of_<script_name>.py`
- Power monitor scripts: `pwr_<script_name>.py`
- Camera scripts (current placeholders): `cam_<script_name>.py`
- Modular I/O scripts (current placeholders): `io_<script_name>.py`
- Variables and function names: `snake_case`
- ROS2 node/topic style in docs: `snake_case`
- Markdown filenames: `kebab-case.md`
- C++ files: `snake_case.cpp` and `snake_case.hpp`
- C++ classes/types: `PascalCase`

## Directory Conventions

Expected top-level modules:

- `optical_flow/`
- `power_monitor/`
- `vision_camera/`
- `modular_io/`
- `motor_control/`

Each module should follow a similar structure when practical:

- `src/` implementation scripts or node code
- `config/` config files and defaults
- `logs/` runtime outputs (gitignored where appropriate)
- `tests/` unit/integration tests
- `README.md` module usage and quickstart

## Script Role Conventions

- `*_smoke.py`: fastest health check and pass/fail output
- `*_experimental.py`: exploratory behavior only
- `*_calibration.py`: calibration workflows and output artifacts
- `*_log.py` or diagnostics modes: structured telemetry capture
- `*_graph.py`: post-processing and visualization
- `<module>_main.py` or routed `main`: user-facing task entrypoint

## Module Reference Header Convention

To keep scripts easy to scan, use a short module reference at the top of each script docstring:

- `Module: optical_flow`
- `Module: power_monitor`
- `Module: vision_camera`
- `Module: modular_io`
- `Module: motor_control`

Example first docstring lines:

```python
"""Module: power_monitor
Smoke test for INA219 board health.
"""
```

## Configuration Conventions

- keep default runtime params in YAML under `config/`
- allow CLI override of config defaults
- print resolved runtime parameters for traceability
- avoid hidden environment-dependent behavior

## Logging Conventions

- produce machine-readable CSV for time-series data
- produce JSON summary for key results and profile exports
- include timestamps, units, and data quality indicators
- include command/context metadata where feasible

## Documentation Conventions

Each module doc under `docs/modules/` should include:

- scope and goals
- interfaces (inputs/outputs)
- smoke-test path
- calibration path
- logging outputs
- ROS2 readiness contract
- known risks and open issues

Top-level docs under `docs/` should include:

- architecture scope and staged roadmap
- project backlog/todo and troubleshooting workflow
- operator handoff and session restart rules
- links to hardware references and external docs

## Commenting and Readability

- prefer self-explanatory code and concise function names
- add short comments only where behavior is non-obvious
- for CLI entrypoints, include compact usage examples in docstrings or README

## Validation Conventions

- every behavior change should include one validation command
- document expected and observed outcomes when behavior differs
- keep troubleshooting notes in `docs/project-todo.md`
