#!/usr/bin/env python3
"""
Fast smoke test wrapper: bus + init + basic motion reads.
"""

from __future__ import annotations

import argparse
import sys

from of_diagnostics import run_comm, run_preflight
from of_sensor import default_config_path, led_breathe, open_sensor, resolve_settings, sensor_probe, set_led


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAA5100 smoke test")
    p.add_argument("--config", default=default_config_path())
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None)
    p.add_argument("--rotation", type=int, default=None, choices=[0, 90, 180, 270])
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--samples", type=int, default=8)
    p.add_argument("--skip-led-check", action="store_true")
    p.add_argument("--led-up-s", type=float, default=1.0)
    p.add_argument("--led-down-s", type=float, default=1.0)
    p.add_argument("--led-steps", type=int, default=20)
    p.add_argument("--led-final-percent", type=float, default=10.0)
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
    probe = sensor_probe(sensor)
    if probe:
        print("sensor probe: " + ", ".join(f"{k}={v}" for k, v in sorted(probe.items())))
    if not args.skip_led_check:
        print(
            f"smoke led breathe cycle: up={args.led_up_s:.2f}s down={args.led_down_s:.2f}s "
            f"steps={args.led_steps}"
        )
        ok, src = led_breathe(sensor, up_seconds=args.led_up_s, down_seconds=args.led_down_s, steps=args.led_steps)
        print(f"smoke led path: {src}")
        if not ok:
            print("smoke led check: unavailable")
    rc = run_comm(sensor, args.samples)
    ok, src = set_led(sensor, True, args.led_final_percent)
    if ok:
        print(f"smoke done: LED left at {args.led_final_percent:.1f}% via {src}")
    else:
        print(f"smoke done: unable to set final LED level ({src})")
    return rc


if __name__ == "__main__":
    sys.exit(main())
