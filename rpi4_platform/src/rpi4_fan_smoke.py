"""Module: rpi4_platform
Smoke-test fan PWM by sweeping a few duty levels.
"""

from __future__ import annotations

import argparse
import time

from gpiozero import PWMOutputDevice

FALLBACK_PWM_FREQUENCIES_HZ = [25_000, 10_000, 5_000, 1_000, 250, 100]


def parse_args() -> argparse.Namespace:
    """Parse CLI options for fan smoke sweep.

    Returns:
        Parsed sweep arguments.
    """
    parser = argparse.ArgumentParser(description="Fan PWM smoke sweep.")
    parser.add_argument("--gpio-pin", type=int, default=18, help="PWM-capable GPIO pin number.")
    parser.add_argument(
        "--levels-percent",
        type=float,
        nargs="+",
        default=[20.0, 40.0, 60.0, 80.0],
        help="Duty levels in percent to test.",
    )
    parser.add_argument("--step-seconds", type=float, default=2.0, help="Hold time per duty level.")
    return parser.parse_args()


def create_fan_pwm_device(gpio_pin: int) -> tuple[PWMOutputDevice, int]:
    """Create a PWM fan device using the first supported frequency.

    Args:
        gpio_pin: PWM-capable GPIO pin.

    Returns:
        Tuple of initialized PWM device and selected frequency.
    """
    last_error: Exception | None = None
    for frequency_hz in FALLBACK_PWM_FREQUENCIES_HZ:
        try:
            device = PWMOutputDevice(pin=gpio_pin, frequency=frequency_hz, initial_value=0.0)
            return device, frequency_hz
        except Exception as error:
            # Common on some backend/pin combinations where requested frequency is unsupported.
            last_error = error
            continue
    raise RuntimeError(f"no_supported_pwm_frequency_for_gpio_{gpio_pin}: {last_error}") from last_error


def sweep_fan(gpio_pin: int, levels_percent: list[float], step_seconds: float) -> None:
    """Sweep fan duty levels for quick operational check.

    Args:
        gpio_pin: PWM-capable GPIO pin.
        levels_percent: Duty cycle levels to apply.
        step_seconds: Hold duration per step.
    """
    fan_pwm, frequency_hz = create_fan_pwm_device(gpio_pin)
    print(f"fan_smoke: using_frequency_hz={frequency_hz}")
    try:
        for level_percent in levels_percent:
            safe_level = max(0.0, min(100.0, level_percent))
            fan_pwm.value = safe_level / 100.0
            print(f"fan_smoke_step: gpio={gpio_pin} duty_percent={safe_level:.1f}")
            time.sleep(max(0.0, step_seconds))
    finally:
        fan_pwm.off()
        fan_pwm.close()
        print("fan_smoke: complete, output disabled")


def main() -> None:
    """Run fan smoke-test entrypoint."""
    args = parse_args()
    try:
        sweep_fan(args.gpio_pin, args.levels_percent, args.step_seconds)
    except Exception as error:  # pragma: no cover - hardware path
        # Common causes: unsupported host, GPIO permissions, or electrical wiring mismatch.
        print(f"fan_smoke_error: {error}")
        raise


if __name__ == "__main__":
    main()
