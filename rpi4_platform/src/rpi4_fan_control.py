"""Module: rpi4_platform
Control PWM fan duty for Raspberry Pi heatsink fan header/GPIO path.
"""

from __future__ import annotations

import argparse
import time

from gpiozero import PWMOutputDevice

FALLBACK_PWM_FREQUENCIES_HZ = [25_000, 10_000, 5_000, 1_000, 250, 100]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for fan PWM control.

    Returns:
        Parsed arguments including gpio pin, duty, and hold duration.
    """
    parser = argparse.ArgumentParser(description="Set PWM fan duty cycle.")
    parser.add_argument("--gpio-pin", type=int, default=18, help="PWM-capable GPIO pin number.")
    parser.add_argument(
        "--duty-percent",
        type=float,
        default=60.0,
        help="Fan duty cycle in percent (0-100).",
    )
    parser.add_argument(
        "--hold-seconds",
        type=float,
        default=5.0,
        help="How long to hold the requested duty before exiting.",
    )
    return parser.parse_args()


def clamp_percent(duty_percent: float) -> float:
    """Clamp a fan duty cycle to a valid percent range.

    Args:
        duty_percent: Requested duty cycle percent.

    Returns:
        Clamped percent between 0 and 100.
    """
    return max(0.0, min(100.0, duty_percent))


def create_fan_pwm_device(gpio_pin: int) -> tuple[PWMOutputDevice, int]:
    """Create a PWM device using the first supported frequency.

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
            # Some gpiozero backends reject high frequencies on specific boards/pins.
            last_error = error
            continue
    raise RuntimeError(f"no_supported_pwm_frequency_for_gpio_{gpio_pin}: {last_error}") from last_error


def set_fan_duty(gpio_pin: int, duty_percent: float, hold_seconds: float) -> None:
    """Apply fan PWM duty for a fixed duration.

    Args:
        gpio_pin: PWM-capable GPIO pin.
        duty_percent: Requested duty percent.
        hold_seconds: Duration to hold duty.
    """
    duty_percent = clamp_percent(duty_percent)
    duty_ratio = duty_percent / 100.0

    fan_pwm, frequency_hz = create_fan_pwm_device(gpio_pin)
    try:
        fan_pwm.value = duty_ratio
        print(
            "fan_pwm: "
            f"gpio={gpio_pin} frequency_hz={frequency_hz} duty_percent={duty_percent:.1f} hold_s={hold_seconds:.1f}"
        )
        time.sleep(max(0.0, hold_seconds))
    finally:
        fan_pwm.off()
        fan_pwm.close()
        print("fan_pwm: output disabled")


def main() -> None:
    """Run fan PWM command entrypoint."""
    args = parse_args()
    try:
        set_fan_duty(args.gpio_pin, args.duty_percent, args.hold_seconds)
    except Exception as error:  # pragma: no cover - hardware path
        # Typical issues: non-Pi host, missing permissions, or unsupported pin routing.
        print(f"fan_pwm_error: {error}")
        raise


if __name__ == "__main__":
    main()
