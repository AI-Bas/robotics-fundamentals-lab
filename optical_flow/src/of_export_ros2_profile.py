#!/usr/bin/env python3
"""
Build ROS2-ready parameter YAML from diagnostics JSON summaries.

This does not run ROS2 directly; it converts measured diagnostics into
config values that a future C++ ROS2 node can consume.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import Any

import yaml


def _latest_file(log_dir: str, prefix: str, suffix: str) -> str | None:
    candidates = [
        os.path.join(log_dir, name)
        for name in os.listdir(log_dir)
        if name.startswith(prefix) and name.endswith(suffix)
    ]
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def _read_json(path: str | None) -> dict[str, Any]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def _recommended_poll_hz(sweep: dict[str, Any], bench: dict[str, Any], safety: float) -> float:
    stable = float(sweep.get("highest_stable_hz", 0.0) or 0.0)
    p95 = float(bench.get("p95_hz", 0.0) or 0.0)
    base = stable if stable > 0 else p95
    if base <= 0:
        return 10.0
    return max(5.0, base * safety)


def main() -> int:
    p = argparse.ArgumentParser(description="Export ROS2 parameter profile from diagnostics summaries")
    p.add_argument("--log-dir", default="logs")
    p.add_argument("--output", default="config/ros2_optical_flow_profile.yaml")
    p.add_argument("--node-name", default="optical_flow_node")
    p.add_argument("--safety-factor", type=float, default=0.7, help="Applied to measured stable poll rate")
    args = p.parse_args()

    sweep_path = _latest_file(args.log_dir, "paa5100_rate_sweep_summary_", ".json")
    bench_path = _latest_file(args.log_dir, "paa5100_benchmark_summary_", ".json")
    stream_path = _latest_file(args.log_dir, "paa5100_stream_summary_", ".json")
    comm_path = _latest_file(args.log_dir, "paa5100_comm_summary_", ".json")
    calib_path = _latest_file(args.log_dir, "paa5100_calibration_", ".json")

    sweep = _read_json(sweep_path)
    bench = _read_json(bench_path)
    stream = _read_json(stream_path)
    comm = _read_json(comm_path)
    calib = _read_json(calib_path)

    poll_hz = _recommended_poll_hz(sweep, bench, args.safety_factor)
    unreliable_error_rate = max(
        float(sweep.get("max_error_rate", 0.01) or 0.01),
        float(stream.get("error_rate", 0.01) or 0.01),
    )
    unreliable_jitter = max(
        float(sweep.get("max_jitter_ratio", 0.4) or 0.4),
        float(stream.get("jitter_ratio_to_target_dt", 0.4) or 0.4),
    )

    profile = {
        args.node_name: {
            "ros__parameters": {
                "sensor_model": "PAA5100JE",
                "poll_hz": round(poll_hz, 2),
                "quality": {
                    "max_error_rate": round(unreliable_error_rate, 4),
                    "max_jitter_ratio": round(unreliable_jitter, 4),
                    "require_nonzero_motion": False,
                },
                "calibration": {
                    "counts_to_mps_scale": float(calib.get("counts_to_mps_scale", 0.0) or 0.0),
                    "brightness_percent_optimal": float(calib.get("best_brightness_percent", 100.0) or 100.0),
                    "scale_source": calib_path or "unset",
                    "notes": "Run of_calibration.py with reference velocity for final scale.",
                },
                "diagnostics_source_files": {
                    "comm_summary": comm_path or "",
                    "benchmark_summary": bench_path or "",
                    "rate_sweep_summary": sweep_path or "",
                    "stream_summary": stream_path or "",
                    "calibration_summary": calib_path or "",
                },
                "generated_at": datetime.now().isoformat(timespec="seconds"),
            }
        }
    }

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        yaml.safe_dump(profile, f, sort_keys=False)

    print(f"wrote: {args.output}")
    print(f"recommended poll_hz: {profile[args.node_name]['ros__parameters']['poll_hz']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
