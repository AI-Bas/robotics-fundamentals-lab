# HMI Dashboard Module

Development area for local Raspberry Pi touchscreen HMI and mirrored browser access over Ethernet/Wi-Fi.

## Goals

- run the same HMI on local HDMI display and remote browser
- switch page layout by task context (configuration, calibration, run mode, modular I/O toolkit)
- keep module integration and system behavior linked to `docs/` source-of-truth
- provide a simple Python-first UI stack for quick iteration

## Runtime Model

- local display mode: full-screen browser on Raspberry Pi HDMI touchscreen
- remote clone mode: browser clients connect to HMI server on LAN
- single app process serves both local and remote users

## Starter Paths

- `src/app.py` Streamlit application entrypoint
- `src/components/` reusable layout and section components
- `config/layout_profiles.yaml` task/page layout profile mapping
- `tests/` UI logic and config-loading tests

## Quick Start

```bash
cd hmi_dashboard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run src/app.py --server.address 0.0.0.0 --server.port 8501
```

Open:

- local Pi touchscreen browser: `http://127.0.0.1:8501`
- remote browser clients: `http://<pi-ip>:8501`

## Documentation

- Module-local hardware/source references: `hmi_dashboard_documentation/hmi-dashboard-documentation.md`
- Architecture source of truth: `../docs/modules/hmi-dashboard.md`
