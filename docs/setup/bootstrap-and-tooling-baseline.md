# Bootstrap And Tooling Baseline

## Purpose

Define an optional, repeatable setup flow for:

- SSH-first development on headless boards
- consistent Cursor/IDE behavior after cloning
- staged hardware/software bootstrap for Raspberry Pi
- future migration path to other SBC targets

This baseline is intentionally optional. Contributors can skip it and still work normally.

## Why This Automates Well

The baseline automates setup in three layers:

1. workspace bootstrap
   - clone, canonical path symlink, and shell helper setup
2. developer tooling bootstrap
   - editor extensions/settings recommendations and static-analysis defaults
3. board bootstrap
   - staged package install + interface enablement + runtime stack provisioning

Each layer is scriptable and idempotent where practical.

## Canonical Path And Clone Behavior

Git clone target directory is not guaranteed unless explicitly provided.

Example:

```bash
git clone git@github.com:AI-Bas/robotics-fundamentals-lab.git
```

The directory name usually becomes `robotics-fundamentals-lab`, but it can differ if:

- you pass a custom target name
- you clone into an existing folder then rename it

Most plug-and-play pattern:

```bash
git clone git@github.com:AI-Bas/robotics-fundamentals-lab.git ~/robotics-fundamentals-lab
```

Additionally, this repository provides a workspace bootstrap script that can create a stable symlink at `~/robotics-fundamentals-lab` even when your real path differs.

## Files Added For Baseline

- `scripts/bootstrap/bootstrap_workspace.sh`
- `scripts/bootstrap/bootstrap_rpi_headless.sh`
- `rpi4_platform/src/rpi4_setup_local.sh`
- `rpi4_platform/src/rpi4_install_hmi_service.sh`
- `rpi4_platform/src/rpi4_mount_circuitpy.sh`
- `robotics-fundamentals-lab.code-workspace`
- `docs/setup/cursor-extensions-reference.md`
- `config/platforms/generic_linux.env`
- `config/platforms/rpi_debian.env`
- `.vscode/extensions.json`
- `.vscode/settings.json`

## Board-Agnostic Design

Bootstrap scripts support profile files under `config/platforms/`:

- use shared defaults in `generic_linux.env`
- layer board-specific values in `rpi_debian.env`
- add new profiles later (for example `jetson_ubuntu.env`, `rock5_debian.env`)

This keeps module code mostly stable while platform bring-up stays configurable.

## Recommended SSH-First Workflow

1. SSH into target board
2. clone repository
3. run workspace bootstrap script
4. run board bootstrap script in `--dry-run` first
5. run board bootstrap script in `--apply`
6. validate interfaces and runtime with module smoke tests
7. run board-specific checks (for example `rpi4_platform/src/rpi4_status.py`)

## Workspace Persistence (One-Click Open)

Use the repository workspace file to reopen both:

- project repository
- mounted Maker Pi CIRCUITPY storage

Workflow:

1. mount/link CIRCUITPY:

```bash
./rpi4_platform/src/rpi4_mount_circuitpy.sh --apply
```

1. open `robotics-fundamentals-lab.code-workspace`

This keeps CircuitPython files editable from the same workspace after SSH reconnects.

## Tooling Baseline Details

### Python

- Pyright/Pylance: fast type analysis and rich hover/autocomplete
- MyPy: configurable type-check gate for CI and explicit strictness control
- Ruff: fast linting + many rule families in one tool

### C++

- clangd: robust indexing, diagnostics, symbol nav, and completion
- clang-tidy: static analysis for bug-prone patterns and style
- clang-format: deterministic formatting

### Recommended Strategy

- use Pyright/Pylance for immediate editor feedback
- use MyPy for intentional strict gates in scripts/CI
- use Ruff for linting and import/style consistency
- use clangd + clang-tidy for C++ diagnostics/refactors

## Pros And Cons

### Pyright/Pylance

Pros:

- very fast, great editor integration
- strong inference in partial typing codebases

Cons:

- some behavior differs from MyPy type semantics
- strictness tuning happens mainly in pyright config

### MyPy

Pros:

- mature and widely adopted for Python type gates
- fine-grained strictness and per-module policy

Cons:

- slower than Pyright on large trees
- can require more annotations to satisfy strict mode

### Ruff

Pros:

- very fast all-in-one linter
- can replace several Python lint tools

Cons:

- rule set is broad; needs deliberate rule selection

### clangd

Pros:

- excellent C++ language server performance
- great completion/navigation if compile commands are available

Cons:

- quality depends on accurate `compile_commands.json`

### clang-tidy

Pros:

- catches subtle C++ issues beyond compiler warnings
- configurable checks for safety/maintainability

Cons:

- noisy if check set is too broad initially

## Notes On Function Docstrings And Hints

Yes: concise docstrings + type hints improve hover signatures and autocomplete hints.

No extra plugin is strictly required if language tooling is installed. Better results come from:

- Python extension + Pylance/Pyright
- C++ extension with clangd

## Next Consistency Phase

Once baseline is accepted:

1. add minimal static-analysis configs (`pyrightconfig.json`, `mypy.ini`, `ruff.toml`, `.clang-tidy`)
2. run checks module-by-module
3. polish existing code to match conventions
4. add CI checks for changed files only
