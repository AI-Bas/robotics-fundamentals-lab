#!/usr/bin/env python3
"""
Fast smoke test wrapper: bus + init + basic motion reads.
"""

from __future__ import annotations

import argparse
import sys
import time

from of_diagnostics import run_comm, run_preflight
from of_sensor import (
    default_config_path,
    led_ramp_linear_levels,
    percent_to_led_level_magic,
    open_sensor,
    resolve_settings,
    sensor_probe,
    set_led,
    set_led_level,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAA5100 smoke test")
    p.add_argument("--config", default=default_config_path())
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None)
    p.add_argument("--rotation", type=int, default=None, choices=[0, 90, 180, 270])
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--samples", type=int, default=8)
    p.add_argument("--skip-led-check", action="store_true")
    p.add_argument("--led-up-s", type=float, default=2.0)
    p.add_argument("--led-down-s", type=float, default=2.0)
    p.add_argument("--led-level-step", type=int, default=1)
    p.add_argument("--led-min-level", type=int, default=80)
    p.add_argument("--led-max-level", type=int, default=212)
    p.add_argument("--led-ramp-cycles", type=int, default=2)
    p.add_argument("--led-blink-count", type=int, default=2)
    p.add_argument("--led-blink-period-s", type=float, default=0.30)
    p.add_argument("--led-show-reference-levels", action="store_true")
    p.add_argument("--led-reference-hold-s", type=float, default=1.0)
    p.add_argument("--led-between-off-s", type=float, default=1.0)
    p.add_argument("--led-final-percent", type=float, default=20.0)
    p.add_argument("--led-final-magic-low", action="store_true", default=True)
    return p.parse_args()


def _run_binary_blink(sensor, count: int, period_s: float, label: str) -> tuple[bool, str]:
    src = "unknown"
    for i in range(max(1, count)):
        ok, src = set_led(sensor, True, 100)
        if not ok:
            print(f"smoke led {label}: FAIL on ON step {i + 1}/{count} ({src})")
            return ok, src
        print(f"smoke led {label}: ON  {i + 1}/{count} (100%)")
        time.sleep(max(0.0, period_s))
        ok, src = set_led(sensor, False, 0)
        if not ok:
            print(f"smoke led {label}: FAIL on OFF step {i + 1}/{count} ({src})")
            return ok, src
        print(f"smoke led {label}: OFF {i + 1}/{count}")
        time.sleep(max(0.0, period_s))
    return True, src


def _run_reference_level_cycle(sensor, hold_s: float) -> tuple[bool, str]:
    # Community-observed "magic" LED brightness values for PAA5100.
    levels = [("LOW/OFF", 0x00), ("MEDIUM", 0x1C), ("HIGH", 0xD5)]
    src = "unknown"
    for label, level in levels:
        pct = (level / 0xD5) * 100.0
        ok, src = set_led(sensor, True, pct)
        if not ok:
            print(f"smoke led ref-levels: FAIL on {label} ({src})")
            return ok, src
        print(f"smoke led ref-levels: {label} level=0x{level:02X} (~{pct:.1f}%)")
        time.sleep(max(0.0, hold_s))
    return True, src


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
    print("status: preflight PASS, sensor open PASS")
    if not args.skip_led_check:
        print(
            f"smoke led pre-blink: count={args.led_blink_count} period={args.led_blink_period_s:.2f}s"
        )
        ok, src = _run_binary_blink(sensor, args.led_blink_count, args.led_blink_period_s, "pre")
        if not ok:
            print("hint: LED control path unavailable or register writes blocked by package build.")
            return 2
        for cycle in range(max(1, args.led_ramp_cycles)):
            print(
                f"smoke led ramp cycle {cycle + 1}/{args.led_ramp_cycles}: "
                f"up={args.led_up_s:.2f}s down={args.led_down_s:.2f}s "
                f"level_step={args.led_level_step} range={args.led_min_level}..{args.led_max_level}"
            )
            ok, src = led_ramp_linear_levels(
                sensor,
                up_seconds=args.led_up_s,
                down_seconds=args.led_down_s,
                level_step=args.led_level_step,
                min_level=args.led_min_level,
                max_level=args.led_max_level,
                end_off=False,
            )
            print(f"smoke led path: {src}")
            if not ok:
                print("smoke led check: unavailable")
                print("hint: if brightness looks binary, ensure private _write path is available in pmw3901 build.")
                return 2
        if args.led_show_reference_levels:
            ok, src = _run_reference_level_cycle(sensor, args.led_reference_hold_s)
            if not ok:
                print("hint: LED reference level cycle failed; check SPI stability and sensor power.")
                return 2
        ok, src = set_led(sensor, False, 0)
        if ok:
            print(f"smoke led settle: OFF for {args.led_between_off_s:.2f}s")
            time.sleep(max(0.0, args.led_between_off_s))
        else:
            print(f"smoke led settle: unable to force OFF ({src})")
    rc = run_comm(sensor, args.samples)
    if rc == 0:
        print("status: communication PASS (all samples successful)")
    else:
        print("status: communication WARN/FAIL")
        print("hint: verify wiring, SPI node selection, surface texture, and sensor height.")
    if args.led_final_magic_low:
        raw = percent_to_led_level_magic(50.0)  # maps to 0x1C by design
        ok, src = set_led_level(sensor, True, raw)
        if ok:
            print(f"smoke done: LED left at MAGIC LOW raw=0x{raw:02X} via {src}")
        else:
            print(f"smoke done: unable to set final MAGIC LOW ({src})")
        return rc
    ok, src = set_led(sensor, True, args.led_final_percent)
    if ok:
        print(f"smoke done: LED left at {args.led_final_percent:.1f}% via {src}")
    else:
        print(f"smoke done: unable to set final LED level ({src})")
        print("hint: fallback path may only support binary LED control in this driver build.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
