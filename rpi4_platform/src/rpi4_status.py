"""Module: rpi4_platform
Collect Raspberry Pi platform status for interfaces, thermals, and connectivity.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for platform status collection.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Collect RPi platform status snapshot.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--summary-only", action="store_true", help="Print concise summary only.")
    return parser.parse_args()


def run_command(command: list[str]) -> dict[str, Any]:
    """Run a command and capture output without failing hard.

    Args:
        command: Command list suitable for subprocess.

    Returns:
        Dict containing command output and success state.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=6)
        return {
            "ok": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as error:
        # Failures are expected when commands are missing or unsupported on current host.
        return {"ok": False, "return_code": None, "stdout": "", "stderr": str(error)}


def read_cpu_temperature_c() -> float | None:
    """Read CPU temperature in Celsius from thermal zone.

    Returns:
        Temperature in Celsius if available, else None.
    """
    thermal_path = Path("/sys/class/thermal/thermal_zone0/temp")
    if not thermal_path.exists():
        return None

    try:
        milli_c = float(thermal_path.read_text(encoding="utf-8").strip())
        return milli_c / 1000.0
    except Exception:
        return None


def collect_interface_status() -> dict[str, Any]:
    """Collect basic interface status for I2C/SPI/UART and USB devices.

    Returns:
        Interface status dictionary.
    """
    i2c_devices = sorted(glob.glob("/dev/i2c-*"))
    spi_devices = sorted(glob.glob("/dev/spidev*"))
    uart_devices = sorted(glob.glob("/dev/ttyAMA*") + glob.glob("/dev/ttyS*") + glob.glob("/dev/ttyUSB*"))
    return {
        "i2c_devices": i2c_devices,
        "spi_devices": spi_devices,
        "uart_devices": uart_devices,
        "usb_lsusb": run_command(["lsusb"]),
    }


def collect_network_status() -> dict[str, Any]:
    """Collect Ethernet/Wi-Fi and addressing status.

    Returns:
        Network status dictionary.
    """
    return {
        "ip_br_addr": run_command(["ip", "-br", "addr"]),
        "ip_br_link": run_command(["ip", "-br", "link"]),
        "ip_route": run_command(["ip", "route"]),
        "wlan_iwconfig": run_command(["iwconfig"]),
    }


def collect_hailo_status() -> dict[str, Any]:
    """Collect Hailo accelerator presence and basic status hints.

    Returns:
        Hailo-related status dictionary.
    """
    hailo_dev_nodes = sorted(glob.glob("/dev/hailo*"))
    lspci_info = run_command(["lspci"]) if shutil.which("lspci") else {"ok": False, "stderr": "lspci_missing"}
    lsusb_info = run_command(["lsusb"])
    return {
        "hailo_dev_nodes": hailo_dev_nodes,
        "lspci": lspci_info,
        "lsusb": lsusb_info,
    }


def collect_fan_status() -> dict[str, Any]:
    """Collect fan-control backend hints and runtime values.

    Returns:
        Fan status dictionary.
    """
    fan_hwmon_entries: list[dict[str, Any]] = []
    for hwmon_dir in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        name_path = hwmon_dir / "name"
        pwm_path = hwmon_dir / "pwm1"
        fan_input_path = hwmon_dir / "fan1_input"
        if not (pwm_path.exists() or fan_input_path.exists()):
            continue
        fan_hwmon_entries.append(
            {
                "path": str(hwmon_dir),
                "name": name_path.read_text(encoding="utf-8").strip() if name_path.exists() else "unknown",
                "pwm1": pwm_path.read_text(encoding="utf-8").strip() if pwm_path.exists() else None,
                "fan1_input": fan_input_path.read_text(encoding="utf-8").strip() if fan_input_path.exists() else None,
                "pwm1_enable": (
                    (hwmon_dir / "pwm1_enable").read_text(encoding="utf-8").strip()
                    if (hwmon_dir / "pwm1_enable").exists()
                    else None
                ),
            }
        )
    return {
        "fan_hwmon_entries": fan_hwmon_entries,
        "has_dedicated_fan_hwmon": len(fan_hwmon_entries) > 0,
    }


def collect_system_status() -> dict[str, Any]:
    """Collect high-level system status summary.

    Returns:
        System status dictionary.
    """
    cpu_temp_c = read_cpu_temperature_c()
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": os.uname().nodename,
        "kernel": os.uname().release,
        "cpu_temp_c": cpu_temp_c,
        "vcgencmd_temp": run_command(["vcgencmd", "measure_temp"]) if shutil.which("vcgencmd") else None,
        "vcgencmd_throttled": run_command(["vcgencmd", "get_throttled"]) if shutil.which("vcgencmd") else None,
    }


def build_summary(status: dict[str, Any]) -> dict[str, Any]:
    """Build a concise, human-readable health summary from full status.

    Args:
        status: Full status payload from collectors.

    Returns:
        Summary dictionary with key indicators and pass/warn flags.
    """
    system = status.get("system", {})
    interfaces = status.get("interfaces", {})
    network = status.get("network", {})
    hailo = status.get("hailo", {})
    fan = status.get("fan", {})

    cpu_temp_c = system.get("cpu_temp_c")
    cpu_temp_ok = isinstance(cpu_temp_c, (int, float)) and cpu_temp_c < 75.0

    i2c_ok = len(interfaces.get("i2c_devices", [])) > 0
    spi_ok = len(interfaces.get("spi_devices", [])) > 0
    ethernet_up = "eth0" in (network.get("ip_br_addr", {}).get("stdout", ""))
    wifi_up = "wlan0" in (network.get("ip_br_addr", {}).get("stdout", ""))
    hailo_detected = "Hailo" in (hailo.get("lspci", {}).get("stdout", ""))
    dedicated_fan_hwmon_detected = bool(fan.get("has_dedicated_fan_hwmon", False))

    return {
        "key_metrics": {
            "hostname": system.get("hostname"),
            "kernel": system.get("kernel"),
            "cpu_temp_c": cpu_temp_c,
            "vcgencmd_temp": (system.get("vcgencmd_temp") or {}).get("stdout", ""),
            "throttled": (system.get("vcgencmd_throttled") or {}).get("stdout", ""),
            "i2c_count": len(interfaces.get("i2c_devices", [])),
            "spi_count": len(interfaces.get("spi_devices", [])),
            "uart_count": len(interfaces.get("uart_devices", [])),
            "dedicated_fan_hwmon_detected": dedicated_fan_hwmon_detected,
        },
        "checks": {
            "cpu_temp_ok_below_75c": cpu_temp_ok,
            "i2c_detected": i2c_ok,
            "spi_detected": spi_ok,
            "ethernet_present": ethernet_up,
            "wifi_present": wifi_up,
            "hailo_seen_on_pcie": hailo_detected,
            "dedicated_fan_hwmon_detected": dedicated_fan_hwmon_detected,
        },
        "overall_status": "ok" if all([cpu_temp_ok, i2c_ok, spi_ok, ethernet_up, wifi_up]) else "warn",
    }


def main() -> None:
    """Run platform status collection entrypoint."""
    args = parse_args()
    status = {
        "system": collect_system_status(),
        "interfaces": collect_interface_status(),
        "network": collect_network_status(),
        "hailo": collect_hailo_status(),
        "fan": collect_fan_status(),
    }
    summary = build_summary(status)
    if args.summary_only:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    if args.pretty:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print(json.dumps(status, separators=(",", ":"), sort_keys=True))

    print("\n=== status_summary ===")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
