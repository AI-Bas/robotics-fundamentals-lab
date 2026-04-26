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
- Documentation folders: `<module_name>_documentation`
- Nested documentation folders: `<module_name>_<topic>`
- Module documentation summary markdown: `<module-name>-documentation.md`

## Directory Conventions

Expected top-level modules:

- `optical_flow/`
- `power_monitor/`
- `vision_camera/`
- `modular_io/`
- `motor_control/`
- `rpi4_platform/`
- `hmi_dashboard/`
- `ros2_core/`

Each module should follow a similar structure when practical:

- `src/` implementation scripts or node code
- `config/` config files and defaults
- `logs/` runtime outputs (gitignored where appropriate)
- `tests/` unit/integration tests
- `README.md` module usage and quickstart
- `<module_name>_documentation/` module-local external artifacts and source links (not architecture source of truth)

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
- `Module: hmi_dashboard`
- `Module: ros2_core`

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

Module-local documentation folder rules:

- each module keeps local source files under `<module_name>_documentation/`
- each module summary file is `<module-name>-documentation.md`
- summary markdown is an index/overview only
- summary markdown should include:
  - module components quick reference
  - source URL quick links
  - latest status snapshot
- detailed files of varying types (PDF/CAD/images/examples/notes) go into module-prefixed subfolders
- system architecture, module behavior, and inter-module integration remain source-of-truth in `docs/`

## Commenting and Readability

- prefer self-explanatory code and concise function names
- add short comments only where behavior is non-obvious
- for CLI entrypoints, include compact usage examples in docstrings or README
- prefer explicit, readable names over overly short acronyms
- keep functions small and reusable with one clear responsibility

## Function Docstring And Type Conventions

Python:

- every function should include a short docstring
- docstring should briefly state purpose, inputs, and outputs
- add explicit type hints for parameters and return types where practical
- use `Optional[...]`, `dict[str, ...]`, and typed tuples/dataclasses where they improve debugging clarity

C++:

- public APIs and non-trivial functions should have concise Doxygen-style comments
- include parameter and return intent where not obvious
- prefer explicit types and avoid ambiguous implicit conversions in critical code paths

Docstring goal:

- improve hover/completion hints in the IDE
- make function contracts visible without opening implementation details

## Error Handling And Troubleshooting Conventions

- use `try`/`except` around hardware I/O, parsing, and external dependency calls where failure is expected
- include concise comments explaining likely failure causes and recovery intent
- avoid broad exception swallowing; log or surface actionable error context
- prefer specific exception classes over generic `Exception` when possible
- keep troubleshooting notes synchronized with `docs/project-todo.md` when new recurring failure modes appear

## Tooling Baseline (Python And C++)

Current repository baseline:

- no repository-level VS Code/Cursor settings were found under `.vscode/`
- no repository-level `pyproject.toml`, `mypy.ini`, `CMakeLists.txt`, `.clang-tidy`, or `.clang-format` were found

Recommended editor tooling:

- Python: Pylance + Pyright diagnostics, Ruff, and MyPy (strictness can be phased in)
- C++: `clangd` or Microsoft C/C++ extension, plus `clang-tidy` for static analysis
- formatting: Black (Python) and `clang-format` (C++)

## Validation Conventions

- every behavior change should include one validation command
- document expected and observed outcomes when behavior differs
- keep troubleshooting notes in `docs/project-todo.md`
