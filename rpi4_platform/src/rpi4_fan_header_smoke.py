"""Module: rpi4_platform
Smoke-test dedicated fan header via hwmon PWM controls when available.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse CLI options for fan header smoke test.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Dedicated fan header PWM smoke test via hwmon.")
    parser.add_argument("--step-seconds", type=float, default=2.0, help="Hold time per PWM step.")
    parser.add_argument(
        "--levels",
        type=int,
        nargs="+",
        default=[64, 128, 192, 255],
        help="PWM levels in range 0..255.",
    )
    return parser.parse_args()


def discover_fan_hwmon() -> Path | None:
    """Find hwmon directory that exposes pwm1/fan1_input controls.

    Returns:
        Path to hwmon directory if found, else None.
    """
    for hwmon_dir in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        pwm_path = hwmon_dir / "pwm1"
        if pwm_path.exists():
            return hwmon_dir
    return None


def read_text(path: Path) -> str:
    """Read a sysfs file as stripped text."""
    return path.read_text(encoding="utf-8").strip()


def write_text(path: Path, value: str) -> None:
    """Write a value into a sysfs file."""
    path.write_text(value, encoding="utf-8")


def run_smoke(hwmon_dir: Path, levels: list[int], step_seconds: float) -> None:
    """Run manual PWM sweep using hwmon interface.

    Args:
        hwmon_dir: hwmon path containing pwm1 nodes.
        levels: PWM levels (0..255).
        step_seconds: Time per step.
    """
    pwm1_path = hwmon_dir / "pwm1"
    pwm1_enable_path = hwmon_dir / "pwm1_enable"
    fan_input_path = hwmon_dir / "fan1_input"

    original_enable = read_text(pwm1_enable_path) if pwm1_enable_path.exists() else "2"
    original_pwm = read_text(pwm1_path)

    print(f"fan_header_hwmon: path={hwmon_dir}")
    print(f"fan_header_initial: pwm1_enable={original_enable} pwm1={original_pwm}")

    try:
        if pwm1_enable_path.exists():
            # 1 is manual mode on standard Linux pwm-fan hwmon drivers.
            write_text(pwm1_enable_path, "1")
        for level in levels:
            safe_level = max(0, min(255, level))
            write_text(pwm1_path, str(safe_level))
            fan_rpm = read_text(fan_input_path) if fan_input_path.exists() else "n/a"
            print(f"fan_header_step: pwm1={safe_level} fan1_input={fan_rpm}")
            time.sleep(max(0.0, step_seconds))
    finally:
        write_text(pwm1_path, original_pwm)
        if pwm1_enable_path.exists():
            write_text(pwm1_enable_path, original_enable)
        print("fan_header_smoke: complete, original settings restored")


def main() -> None:
    """Run dedicated fan-header smoke test entrypoint."""
    args = parse_args()

    hwmon_dir = discover_fan_hwmon()
    if hwmon_dir is None:
        raise RuntimeError("no_hwmon_pwm1_found; dedicated fan header control path not detected")

    try:
        run_smoke(hwmon_dir, args.levels, args.step_seconds)
    except PermissionError as error:
        raise PermissionError("permission denied; rerun with sudo for hwmon writes") from error
    except Exception as error:
        print(f"fan_header_smoke_error: {error}")
        raise


if __name__ == "__main__":
    main()
