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
    read_register,
    resolve_settings,
    sensor_probe,
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
        choices=["info", "led", "motion", "probe", "burst", "frame", "register-read"],
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
    return p.parse_known_args()


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

