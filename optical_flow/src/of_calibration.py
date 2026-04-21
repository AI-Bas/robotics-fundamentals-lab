#!/usr/bin/env python3
"""
Optical-flow calibration utility for brightness, timing, and velocity scale.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import time
from datetime import datetime

from of_sensor import default_config_path, open_sensor, resolve_settings, set_led


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _paths(log_dir: str, stem: str) -> tuple[str, str]:
    _ensure_dir(log_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (
        os.path.join(log_dir, f"{stem}_{ts}.csv"),
        os.path.join(log_dir, f"{stem}_{ts}.json"),
    )


def _capture_window(sensor, seconds: float, target_hz: float) -> dict:
    target_dt = 1.0 / target_hz if target_hz > 0 else 0.0
    t_end = time.perf_counter() + seconds
    next_tick = time.perf_counter()
    dts: list[float] = []
    speeds: list[float] = []
    errors = 0
    reads = 0
    t_prev = None
    while time.perf_counter() < t_end:
        now = time.perf_counter()
        if target_dt > 0 and now < next_tick:
            time.sleep(next_tick - now)
        t_loop = time.perf_counter()
        dt = (t_loop - t_prev) if t_prev is not None else 0.0
        t_prev = t_loop
        try:
            dx, dy = sensor.get_motion()
            reads += 1
            speed = math.hypot(dx, dy)
            if dt > 0:
                dts.append(dt)
                speeds.append(speed / dt)
        except Exception:
            errors += 1
        if target_dt > 0:
            next_tick += target_dt
    mean_hz = (1.0 / statistics.fmean(dts)) if dts else 0.0
    jitter = statistics.pstdev(dts) if len(dts) > 1 else 0.0
    error_rate = errors / max(1, reads + errors)
    mean_speed_counts_s = statistics.fmean(speeds) if speeds else 0.0
    return {
        "reads": reads,
        "errors": errors,
        "error_rate": error_rate,
        "mean_hz": mean_hz,
        "dt_jitter_std_s": jitter,
        "mean_speed_counts_s": mean_speed_counts_s,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Calibrate optical-flow brightness and scale")
    p.add_argument("--config", default=default_config_path())
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None)
    p.add_argument("--rotation", type=int, default=None, choices=[0, 90, 180, 270])
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--log-dir", default="logs")
    p.add_argument("--target-hz", type=float, default=20.0)
    p.add_argument("--window-s", type=float, default=3.0)
    p.add_argument("--brightness-min-pct", type=float, default=10.0)
    p.add_argument("--brightness-max-pct", type=float, default=100.0)
    p.add_argument("--brightness-step-pct", type=float, default=10.0)
    p.add_argument("--reference-velocity-mps", type=float, default=0.0, help="Known surface speed for moving calibration")
    p.add_argument("--profile-out", default="config/ros2_optical_flow_profile.yaml")
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
    sensor = open_sensor(settings.spi_port, settings.spi_cs, settings.rotation, settings.auto_cs)
    csv_path, json_path = _paths(args.log_dir, "paa5100_calibration")

    rows = []
    pct = args.brightness_min_pct
    best = None
    while pct <= args.brightness_max_pct + 1e-9:
        set_led(sensor, True, pct)
        stats = _capture_window(sensor, args.window_s, args.target_hz)
        score = (1.0 - stats["error_rate"]) * stats["mean_hz"] / (1.0 + stats["dt_jitter_std_s"])
        row = {
            "ts_iso": _now_iso(),
            "brightness_percent": round(pct, 3),
            "score": score,
            **stats,
        }
        rows.append(row)
        if best is None or row["score"] > best["score"]:
            best = row
        pct += args.brightness_step_pct
    set_led(sensor, False, 0)

    stationary = best["mean_speed_counts_s"] if best else 0.0
    moving = 0.0
    scale = 0.0
    if args.reference_velocity_mps > 0:
        set_led(sensor, True, best["brightness_percent"] if best else None)
        moving_stats = _capture_window(sensor, args.window_s, args.target_hz)
        set_led(sensor, False, 0)
        moving = moving_stats["mean_speed_counts_s"]
        delta = max(0.0, moving - stationary)
        scale = (args.reference_velocity_mps / delta) if delta > 0 else 0.0

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "ts_iso",
                "brightness_percent",
                "score",
                "reads",
                "errors",
                "error_rate",
                "mean_hz",
                "dt_jitter_std_s",
                "mean_speed_counts_s",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    summary = {
        "kind": "paa5100_calibration_summary",
        "timestamp": _now_iso(),
        "csv_path": csv_path,
        "best_brightness_percent": best["brightness_percent"] if best else 100.0,
        "stationary_speed_counts_s": stationary,
        "moving_speed_counts_s": moving,
        "reference_velocity_mps": args.reference_velocity_mps,
        "counts_to_mps_scale": scale,
        "recommended_poll_hz": args.target_hz,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    # Opportunistic profile patch if file exists.
    if os.path.exists(args.profile_out):
        try:
            import yaml

            with open(args.profile_out, "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f) or {}
            if isinstance(profile, dict) and profile:
                node_name = next(iter(profile.keys()))
                params = profile[node_name].setdefault("ros__parameters", {})
                cal = params.setdefault("calibration", {})
                cal["counts_to_mps_scale"] = round(scale, 8) if scale > 0 else 0.0
                cal["brightness_percent_optimal"] = best["brightness_percent"] if best else 100.0
                cal["calibration_summary_json"] = json_path
                with open(args.profile_out, "w", encoding="utf-8") as f:
                    yaml.safe_dump(profile, f, sort_keys=False)
        except Exception:
            pass

    print(f"calibration csv: {csv_path}")
    print(f"calibration summary: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
