"""Module: rpi4_platform
Capture connected-device and interface inventory into repo config files.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "rpi4_platform" / "config" / "rpi4_device_inventory.json"


def run_command(command: list[str]) -> dict[str, Any]:
    """Run command and return captured output with status metadata."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=8)
        return {
            "ok": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "command": command,
        }
    except Exception as error:
        return {
            "ok": False,
            "return_code": None,
            "stdout": "",
            "stderr": str(error),
            "command": command,
        }


def collect_serial_devices() -> list[str]:
    """Collect common serial device nodes."""
    candidates = sorted(Path("/dev").glob("ttyACM*")) + sorted(Path("/dev").glob("ttyUSB*"))
    return [str(path) for path in candidates]


def detect_maker_pi(usb_lines: list[str]) -> dict[str, Any]:
    """Detect Maker Pi RP2040 from lsusb output lines."""
    matches = [line for line in usb_lines if "2e8a:1000" in line.lower() or "maker pi rp2040" in line.lower()]
    return {"detected": len(matches) > 0, "usb_entries": matches}


def collect_inventory() -> dict[str, Any]:
    """Collect inventory snapshot for interfaces, USB, network, and modules."""
    lsusb_result = run_command(["lsusb"])
    lsblk_result = run_command(["lsblk", "-o", "NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT"])
    ip_addr_result = run_command(["ip", "-br", "addr"])
    i2c_list = sorted(str(path) for path in Path("/dev").glob("i2c-*"))
    spi_list = sorted(str(path) for path in Path("/dev").glob("spidev*"))
    serial_list = collect_serial_devices()
    usb_lines = lsusb_result.get("stdout", "").splitlines() if lsusb_result.get("stdout") else []
    maker_pi = detect_maker_pi(usb_lines)

    return {
        "last_checked_utc": datetime.now(timezone.utc).isoformat(),
        "host": {
            "hostname": run_command(["hostname"]).get("stdout", ""),
            "kernel": run_command(["uname", "-r"]).get("stdout", ""),
        },
        "interfaces": {
            "i2c_devices": i2c_list,
            "spi_devices": spi_list,
            "serial_devices": serial_list,
            "network_brief": ip_addr_result.get("stdout", ""),
        },
        "usb": {
            "lsusb_raw": usb_lines,
            "maker_pi_rp2040": maker_pi,
        },
        "storage": {
            "lsblk": lsblk_result.get("stdout", ""),
            "circuitpython_mount_candidates": ["/media/s3p", "/media", "/mnt"],
        },
        "module_links": {
            "power_monitor_i2c_present": len(i2c_list) > 0,
            "optical_flow_spi_present": len(spi_list) > 0,
            "modular_io_usb_present": maker_pi["detected"],
            "ros2_cli_present": run_command(["bash", "-lc", "command -v ros2 >/dev/null && echo yes || echo no"]).get(
                "stdout", "no"
            )
            == "yes",
        },
    }


def main() -> None:
    """Run snapshot generation and persist inventory file."""
    inventory = collect_inventory()
    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"inventory_written: {INVENTORY_PATH}")
    print(json.dumps(inventory, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
