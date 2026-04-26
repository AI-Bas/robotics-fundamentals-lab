# Raspberry Pi 4 Platform Module

Development area for board/platform-specific setup, runtime provisioning, and integration notes for Raspberry Pi 4 (8 GB).

## Goals

- keep board bring-up deterministic and repeatable
- track OS/runtime baseline and package dependencies
- manage hardware interface configuration (I2C/SPI/UART/CSI/network)
- provide reusable bootstrap helpers for module deployment
- keep board-specific assumptions isolated from module logic

## Starter Paths

- `src/` platform helper scripts
- `config/` board/runtime profile files
- `logs/` bootstrap and validation logs
- `tests/` setup validation checks

## Starter Scripts

- `src/rpi4_setup_local.sh` board-specific setup wrapper around shared bootstrap
- `src/rpi4_status.py` platform health snapshot (temp, network, interfaces, USB, Hailo hints)
- `src/rpi4_fan_mode.py` inspect/set dedicated fan header mode (`auto`/`manual`)
- `src/rpi4_fan_control.py` set PWM fan duty for a fixed duration
- `src/rpi4_fan_smoke.py` quick fan PWM sweep test
- `src/rpi4_fan_header_smoke.py` dedicated 4-pin fan header smoke via hwmon
- `src/rpi4_cleanup_optional_desktop.sh` optional purge of non-project desktop apps for headless use
- `src/rpi4_install_hmi_service.sh` install/enable HMI systemd service
- `src/rpi4_inventory_snapshot.py` capture connected-device/interface inventory into config

## Quick Start

```bash
# dry-run setup plan
./rpi4_platform/src/rpi4_setup_local.sh --dry-run

# apply setup
./rpi4_platform/src/rpi4_setup_local.sh --apply

# platform status snapshot
python3 rpi4_platform/src/rpi4_status.py --pretty

# fan mode check (auto/manual)
sudo python3 rpi4_platform/src/rpi4_fan_mode.py --mode show

# fan PWM smoke (default GPIO18)
python3 rpi4_platform/src/rpi4_fan_smoke.py --gpio-pin 18 --step-seconds 2

# dedicated fan header smoke (requires sudo for hwmon writes)
sudo python3 rpi4_platform/src/rpi4_fan_header_smoke.py --step-seconds 2

# inventory snapshot (writes rpi4_platform/config/rpi4_device_inventory.json)
python3 rpi4_platform/src/rpi4_inventory_snapshot.py

# optional headless cleanup preview then apply
./rpi4_platform/src/rpi4_cleanup_optional_desktop.sh --dry-run
./rpi4_platform/src/rpi4_cleanup_optional_desktop.sh --apply

# optional HMI autostart service setup
./rpi4_platform/src/rpi4_install_hmi_service.sh --dry-run
./rpi4_platform/src/rpi4_install_hmi_service.sh --apply
```

Note:

- If your board reports `BCM2712` and exposes dedicated fan hwmon entries, use `rpi4_fan_header_smoke.py` as the primary fan test.
- `rpi4_fan_smoke.py` is for GPIO PWM fan wiring and may not affect dedicated fan-header control.
- Headless mode still allows local HDMI + keyboard terminal access unless you explicitly configure kiosk-only autologin behavior.
- Maker Pi RP2040 CircuitPython workflow is available when the `CIRCUITPY` mass-storage volume is mounted (for example `/mnt/circuitpy`).

## Documentation

- Module-local hardware/source references: `rpi4_platform_documentation/rpi4-platform-documentation.md`
- Architecture source of truth: `../docs/modules/rpi4-platform.md`
