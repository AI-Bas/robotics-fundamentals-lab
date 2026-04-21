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
import os
import subprocess
import sys


def _run(script_name: str, args: list[str]) -> int:
    here = os.path.dirname(__file__)
    script = os.path.join(here, script_name)
    return subprocess.call([sys.executable, script, *args])


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(description="Experimental reference wrapper for optical-flow tests")
    p.add_argument(
        "--mode",
        choices=["info", "led", "motion"],
        default="info",
        help="info->smoke, led->diagnostics led, motion->stream logger",
    )
    return p.parse_known_args()


def main() -> int:
    args, extra = parse_args()
    if args.mode == "info":
        return _run("of_sensor_smoke.py", extra)
    if args.mode == "led":
        return _run("of_diagnostics.py", ["--mode", "led", *extra])
    return _run("of_log_motion.py", extra)


if __name__ == "__main__":
    raise SystemExit(main())

