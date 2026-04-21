#!/usr/bin/env python3
"""
Experimental reference wrapper.

This script intentionally delegates to dedicated tools:
- smoke / basic health -> of_sensor_smoke.py
- detailed diagnostics -> of_diagnostics.py
- streaming logs -> of_log_motion.py
- benchmark/sweep logs -> of_log_tests.py
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

from of_sensor import (
    default_config_path,
    frame_capture_snapshot,
    motion_burst_snapshot,
    open_sensor,
    percent_to_led_level_linear_raw,
    percent_to_led_level_magic,
    percent_to_led_level,
    read_register,
    resolve_settings,
    sensor_probe,
    set_led,
    set_led_level,
    supports_raw_register_access,
)


def _run(script_name: str, args: list[str]) -> int:
    here = os.path.dirname(__file__)
    script = os.path.join(here, script_name)
    return subprocess.call([sys.executable, script, *args])


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(description="Experimental reference wrapper for optical-flow tests")
    p.add_argument(
        "--mode",
        choices=["info", "led", "motion", "probe", "burst", "frame", "register-read", "led-tune", "led-sweep"],
        default="info",
        help="Delegate basic modes and expose advanced sensor experiments",
    )
    p.add_argument("--config", default=default_config_path())
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None)
    p.add_argument("--rotation", type=int, default=None)
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--samples", type=int, default=8, help="Samples for burst/frame experiments")
    p.add_argument("--sample-period", type=float, default=0.05, help="Delay between snapshots")
    p.add_argument("--register", type=lambda s: int(s, 0), default=0x00, help="Register for register-read mode")
    p.add_argument("--sweep-hold-s", type=float, default=0.6, help="Hold duration per LED sweep step")
    return p.parse_known_args()


def _read_led_register(sensor) -> int | None:
    if not supports_raw_register_access(sensor):
        return None
    write_fn = getattr(sensor, "_write", None)
    if not callable(write_fn):
        return None
    try:
        write_fn(0x7F, 0x14)
        value = read_register(sensor, 0x6F)
        write_fn(0x7F, 0x00)
        return int(value)
    except Exception:
        return None


def _run_led_sweep(sensor, hold_s: float) -> int:
    # Include both human percentages and known magic raw levels.
    sweep = [
        ("pct", 0), ("pct", 2), ("pct", 5), ("pct", 10), ("pct", 15), ("pct", 20),
        ("pct", 25), ("pct", 30), ("pct", 40), ("pct", 50), ("pct", 60), ("pct", 70),
        ("pct", 80), ("pct", 90), ("pct", 100),
        ("raw", 0x00), ("raw", 0x1C), ("raw", 0xD5),
    ]
    print("LED sweep start (Ctrl+C to stop)")
    for kind, value in sweep:
        if kind == "pct":
            ok, src = set_led(sensor, True, value)
            mapped_default = percent_to_led_level(value)
            mapped_linear = percent_to_led_level_linear_raw(value)
            mapped_magic = percent_to_led_level_magic(value)
            readback = _read_led_register(sensor)
            print(
                f"set percent={value:>5.1f}% -> mapped_default={mapped_default:>3d} "
                f"mapped_linear={mapped_linear:>3d} mapped_magic={mapped_magic:>3d} "
                f"readback={readback} via {src} ({'ok' if ok else 'fail'})"
            )
        else:
            ok, src = set_led_level(sensor, True, value)
            readback = _read_led_register(sensor)
            print(f"set raw_level=0x{value:02X} ({value:>3d}) readback={readback} via {src} ({'ok' if ok else 'fail'})")
        time.sleep(max(0.0, hold_s))
    set_led(sensor, False, 0)
    print("LED sweep done; LED forced OFF.")
    return 0


def _run_led_tune(sensor) -> int:
    print(
        "LED tune mode: type a percent (default mapping), "
        "'linear <0-100>', 'magic <0-100>', 'raw <0-213>', 'off', 'status', or 'q'."
    )
    while True:
        try:
            text = input("led> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        lower = text.lower()
        if lower in {"q", "quit", "exit"}:
            break
        if lower == "off":
            ok, src = set_led(sensor, False, 0)
            rb = _read_led_register(sensor)
            print(f"off -> {'ok' if ok else 'fail'} via {src}; readback={rb}")
            continue
        if lower == "status":
            rb = _read_led_register(sensor)
            print(f"status: led_register_0x6F={rb}")
            continue
        if lower.startswith("raw "):
            try:
                raw = int(lower.split(None, 1)[1], 0)
            except ValueError:
                print("invalid raw value. use: raw 28")
                continue
            ok, src = set_led_level(sensor, True, raw)
            rb = _read_led_register(sensor)
            print(f"raw={raw} -> {'ok' if ok else 'fail'} via {src}; readback={rb}")
            continue
        if lower.startswith("linear "):
            try:
                pct_lin = float(lower.split(None, 1)[1])
            except ValueError:
                print("invalid linear value. use: linear 42")
                continue
            mapped_linear = percent_to_led_level_linear_raw(pct_lin)
            ok, src = set_led_level(sensor, True, mapped_linear)
            rb = _read_led_register(sensor)
            print(
                f"linear_percent={pct_lin:.2f}% -> raw_level={mapped_linear} "
                f"-> {'ok' if ok else 'fail'} via {src}; readback={rb}"
            )
            continue
        if lower.startswith("magic "):
            try:
                pct_magic = float(lower.split(None, 1)[1])
            except ValueError:
                print("invalid magic value. use: magic 42")
                continue
            mapped_magic = percent_to_led_level_magic(pct_magic)
            ok, src = set_led_level(sensor, True, mapped_magic)
            rb = _read_led_register(sensor)
            print(
                f"magic_percent={pct_magic:.2f}% -> raw_level={mapped_magic} "
                f"-> {'ok' if ok else 'fail'} via {src}; readback={rb}"
            )
            continue
        try:
            pct = float(text)
        except ValueError:
            print("invalid input. enter 0..100, 'raw N', 'off', 'status', or 'q'.")
            continue
        mapped = percent_to_led_level(pct)
        ok, src = set_led(sensor, True, pct)
        rb = _read_led_register(sensor)
        print(
            f"percent={pct:.2f}% -> mapped_default_level={mapped} "
            f"(linear_raw={percent_to_led_level_linear_raw(pct)}, magic={percent_to_led_level_magic(pct)}) "
            f"-> {'ok' if ok else 'fail'} via {src}; readback={rb}"
        )
    set_led(sensor, False, 0)
    print("LED tune ended; LED forced OFF.")
    return 0


def main() -> int:
    args, extra = parse_args()
    if args.mode == "info":
        return _run("of_sensor_smoke.py", extra)
    if args.mode == "led":
        return _run("of_diagnostics.py", ["--mode", "led", *extra])
    if args.mode == "motion":
        return _run("of_log_motion.py", extra)

    settings = resolve_settings(
        config_path=args.config,
        spi_port_override=args.spi_port,
        spi_cs_override=args.spi_cs,
        rotation_override=args.rotation,
        no_auto_cs=args.no_auto_cs,
    )
    sensor = open_sensor(settings.spi_port, settings.spi_cs, settings.rotation, settings.auto_cs)
    try:
        if args.mode == "probe":
            print(json.dumps(sensor_probe(sensor), indent=2))
            return 0
        if args.mode == "register-read":
            if not supports_raw_register_access(sensor):
                print("Raw register access unavailable in this pmw3901 build")
                return 2
            value = read_register(sensor, args.register)
            print(json.dumps({"register": hex(args.register), "value": value}, indent=2))
            return 0
        if args.mode == "led-sweep":
            return _run_led_sweep(sensor, args.sweep_hold_s)
        if args.mode == "led-tune":
            return _run_led_tune(sensor)
        if args.mode == "burst":
            rows = []
            for _ in range(max(1, args.samples)):
                rows.append(motion_burst_snapshot(sensor))
                time.sleep(max(0.0, args.sample_period))
            print(json.dumps(rows, indent=2))
            return 0
        if args.mode == "frame":
            rows = []
            for _ in range(max(1, args.samples)):
                rows.append(frame_capture_snapshot(sensor))
                time.sleep(max(0.0, args.sample_period))
            print(json.dumps(rows, indent=2))
            return 0
    finally:
        close_fn = getattr(sensor, "close", None)
        if callable(close_fn):
            close_fn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

