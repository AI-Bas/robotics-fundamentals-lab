#!/usr/bin/env python3
"""
Fast smoke test wrapper: bus + init + basic motion reads.
"""

from __future__ import annotations

import argparse
import sys
import time

from paa5100_diagnostics import _sensor_probe, run_comm, run_preflight
from sensor import DEFAULT_LED_LEVEL, led_setter, default_config_path, open_sensor, resolve_settings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAA5100 smoke test")
    p.add_argument("--config", default=default_config_path())
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None)
    p.add_argument("--rotation", type=int, default=None, choices=[0, 90, 180, 270])
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--samples", type=int, default=8)
    p.add_argument("--skip-led-check", action="store_true")
    p.add_argument("--led-level", type=int, default=DEFAULT_LED_LEVEL)
    p.add_argument("--led-blinks", type=int, default=2)
    p.add_argument("--led-period", type=float, default=0.35)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    settings = resolve_settings(
        config_path=args.config,
        spi_port_override=args.spi_port,
        spi_cs_override=args.spi_cs,
        rotation_override=args.rotation,
        no_auto_cs=args.no_auto_cs,
    )
    rc = run_preflight(settings.cfg, settings.spi_port, settings.spi_cs)
    if rc != 0:
        return rc
    sensor = open_sensor(settings.spi_port, settings.spi_cs, settings.rotation, settings.auto_cs)
    probe = _sensor_probe(sensor)
    if probe:
        print("sensor probe: " + ", ".join(f"{k}={v}" for k, v in sorted(probe.items())))
    if not args.skip_led_check:
        set_led, source = led_setter(sensor)
        print(f"smoke led path: {source}")
        if set_led is None:
            print("smoke led check: unavailable")
        else:
            for i in range(max(1, args.led_blinks)):
                set_led(True, args.led_level)
                print(f"smoke led blink {i + 1}/{args.led_blinks}: ON (level={args.led_level})")
                time.sleep(args.led_period)
                set_led(False, args.led_level)
                print(f"smoke led blink {i + 1}/{args.led_blinks}: OFF")
                time.sleep(args.led_period)
    return run_comm(sensor, args.samples)


if __name__ == "__main__":
    sys.exit(main())
