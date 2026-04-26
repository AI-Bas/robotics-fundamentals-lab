"""Module: rpi4_platform
Inspect or set dedicated fan header control mode via hwmon pwm1_enable.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse CLI options for fan mode inspection or update."""
    parser = argparse.ArgumentParser(description="Inspect/set fan header control mode.")
    parser.add_argument(
        "--mode",
        choices=["show", "auto", "manual"],
        default="show",
        help="Fan mode: show current state, set auto (2), or set manual (1).",
    )
    return parser.parse_args()


def discover_fan_hwmon() -> Path:
    """Find hwmon path exposing pwm1 and pwm1_enable."""
    for hwmon_dir in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        if (hwmon_dir / "pwm1").exists() and (hwmon_dir / "pwm1_enable").exists():
            return hwmon_dir
    raise RuntimeError("no_fan_hwmon_found")


def read_text(path: Path) -> str:
    """Read a sysfs file as stripped text."""
    return path.read_text(encoding="utf-8").strip()


def write_text(path: Path, value: str) -> None:
    """Write text value to sysfs file."""
    path.write_text(value, encoding="utf-8")


def mode_label(raw_mode: str) -> str:
    """Convert pwm1_enable value to human label."""
    return {"1": "manual", "2": "auto"}.get(raw_mode, f"unknown({raw_mode})")


def main() -> None:
    """Run fan mode tool entrypoint."""
    args = parse_args()
    hwmon_dir = discover_fan_hwmon()
    enable_path = hwmon_dir / "pwm1_enable"
    pwm_path = hwmon_dir / "pwm1"
    fan_input_path = hwmon_dir / "fan1_input"

    current_mode = read_text(enable_path)
    current_pwm = read_text(pwm_path)
    current_rpm = read_text(fan_input_path) if fan_input_path.exists() else "n/a"
    print(
        f"fan_mode: path={hwmon_dir} mode={mode_label(current_mode)} "
        f"pwm1_enable={current_mode} pwm1={current_pwm} fan1_input={current_rpm}"
    )

    if args.mode == "show":
        return

    target_raw = "2" if args.mode == "auto" else "1"
    if current_mode == target_raw:
        print(f"fan_mode: already_{args.mode}")
        return

    try:
        write_text(enable_path, target_raw)
    except PermissionError as error:
        raise PermissionError("permission denied; rerun with sudo to change fan mode") from error

    updated_mode = read_text(enable_path)
    print(f"fan_mode: updated mode={mode_label(updated_mode)} pwm1_enable={updated_mode}")


if __name__ == "__main__":
    main()
