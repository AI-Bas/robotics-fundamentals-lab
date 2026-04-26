# Cursor Extensions Reference

## Purpose

Track recommended extensions for a consistent robotics workflow across:

- local desktop Cursor
- remote SSH workspace Cursor

Install language/runtime extensions in both contexts when prompted.

## Core Recommendations

- Python: `ms-python.python`
- Pylance: `ms-python.vscode-pylance`
- Ruff: `charliermarsh.ruff`
- C/C++: `ms-vscode.cpptools`
- clangd: `llvm-vs-code-extensions.vscode-clangd`
- Docker: `ms-azuretools.vscode-docker`

## Optional Project-Relevant Extensions

- GitLens: `eamodio.gitlens`
- GitHub Pull Requests: `github.vscode-pull-request-github`
- GitHub Actions: `github.vscode-github-actions`
- Rainbow CSV: `mechatroner.rainbow-csv`
- ROS tooling (if stable in your environment): install after base extensions and SSH host are stable

## Install Notes

- If an extension is gray/frozen in remote mode, restart Cursor and reconnect SSH first.
- Install extension once locally (UI side) and once on remote host (language service side) when prompted.
- Keep a minimal stable baseline; add optional extensions incrementally.

## Known Limitation

CircuitPython files mounted from `CIRCUITPY` may show import errors in host-side Python analysis because those modules exist on-device, not in host interpreter paths.
