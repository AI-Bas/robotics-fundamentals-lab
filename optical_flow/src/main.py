#!/usr/bin/env python3
"""
Top-level task router for optical_flow utilities.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def _run(script_name: str, extra_args: list[str]) -> int:
    here = os.path.dirname(__file__)
    script = os.path.join(here, script_name)
    cmd = [sys.executable, script, *extra_args]
    return subprocess.call(cmd)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Optical flow tool router")
    p.add_argument(
        "task",
        choices=[
            "smoke",
            "first-test",
            "diagnostics",
            "stream-log",
        "log-tests",
            "export-ros2-profile",
        ],
    )
    p.add_argument("extra", nargs=argparse.REMAINDER, help="Arguments passed to task script")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    mapping = {
        "smoke": "sensor_smoke.py",
        "first-test": "paa5100_first_test.py",
        "diagnostics": "paa5100_diagnostics.py",
        "stream-log": "log_motion.py",
        "log-tests": "log_tests.py",
        "export-ros2-profile": "export_ros2_profile.py",
    }
    return _run(mapping[args.task], args.extra)


if __name__ == "__main__":
    sys.exit(main())
