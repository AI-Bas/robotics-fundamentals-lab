#!/usr/bin/env python3
"""
Plot diagnostics and calibration trends from optical-flow logs.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime

import matplotlib.pyplot as plt


def _latest_files(log_dir: str, prefix: str, suffix: str) -> list[str]:
    items = [
        os.path.join(log_dir, n)
        for n in os.listdir(log_dir)
        if n.startswith(prefix) and n.endswith(suffix)
    ]
    return sorted(items, key=os.path.getmtime)


def _read_csv(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_rate_sweep(log_dir: str, out_dir: str) -> str | None:
    files = _latest_files(log_dir, "paa5100_rate_sweep_", ".csv")
    if not files:
        return None
    rows = _read_csv(files[-1])
    hz = [float(r["target_hz"]) for r in rows]
    mean_hz = [float(r["mean_achieved_hz"]) for r in rows]
    score = [float(r.get("balanced_score", 0.0)) for r in rows]
    stable = [int(r["stable"]) for r in rows]

    plt.figure(figsize=(9, 4.5))
    plt.plot(hz, mean_hz, marker="o", label="Mean achieved Hz")
    plt.plot(hz, score, marker="x", label="Balanced score")
    plt.scatter(hz, stable, marker="s", label="Stable (0/1)")
    plt.xlabel("Target Hz")
    plt.ylabel("Metric")
    plt.title("Rate Sweep: Achieved Rate and Stability Score")
    plt.grid(True, alpha=0.3)
    plt.legend()
    out = os.path.join(out_dir, "rate_sweep_trends.png")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def plot_stream_quality(log_dir: str, out_dir: str) -> str | None:
    files = _latest_files(log_dir, "paa5100_stream_", ".csv")
    if not files:
        return None
    rows = _read_csv(files[-1])
    idx = list(range(len(rows)))
    hz = [float(r["inst_hz"]) for r in rows]
    speed = [float(r["speed_counts_s"]) for r in rows]
    quality = [r["quality_flag"] for r in rows]
    q_map = {"nominal": 0, "timing_lag": 1, "low_signal": 2, "sensor_error": 3}
    qv = [q_map.get(q, 4) for q in quality]

    plt.figure(figsize=(10, 5))
    ax1 = plt.gca()
    ax1.plot(idx, hz, label="inst_hz")
    ax1.plot(idx, speed, label="speed_counts_s")
    ax1.set_xlabel("Sample")
    ax1.set_ylabel("Hz / counts/s")
    ax2 = ax1.twinx()
    ax2.plot(idx, qv, color="red", alpha=0.4, label="quality_flag")
    ax2.set_ylabel("Quality code")
    ax1.grid(True, alpha=0.3)
    plt.title("Stream Signal Integrity")
    out = os.path.join(out_dir, "stream_integrity.png")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def plot_calibration(log_dir: str, out_dir: str) -> str | None:
    files = _latest_files(log_dir, "paa5100_calibration_", ".csv")
    if not files:
        return None
    rows = _read_csv(files[-1])
    b = [float(r["brightness_percent"]) for r in rows]
    score = [float(r["score"]) for r in rows]
    hz = [float(r["mean_hz"]) for r in rows]
    err = [float(r["error_rate"]) for r in rows]

    plt.figure(figsize=(9, 4.5))
    plt.plot(b, score, marker="o", label="score")
    plt.plot(b, hz, marker="x", label="mean_hz")
    plt.plot(b, err, marker="s", label="error_rate")
    plt.xlabel("Brightness %")
    plt.title("Calibration Trends vs Brightness")
    plt.grid(True, alpha=0.3)
    plt.legend()
    out = os.path.join(out_dir, "calibration_trends.png")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Graph optical-flow diagnostics and calibration trends")
    p.add_argument("--log-dir", default="logs")
    p.add_argument("--out-dir", default="logs/plots")
    p.add_argument("--encoder-csv", default="", help="Optional encoder feedback CSV for future comparison integration")
    args = p.parse_args()

    _ensure(args.out_dir)
    outputs = [
        plot_rate_sweep(args.log_dir, args.out_dir),
        plot_stream_quality(args.log_dir, args.out_dir),
        plot_calibration(args.log_dir, args.out_dir),
    ]
    made = [o for o in outputs if o]
    summary = {
        "kind": "paa5100_graph_summary",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "log_dir": args.log_dir,
        "out_dir": args.out_dir,
        "plots": made,
        "encoder_csv": args.encoder_csv,
        "encoder_integration_ready": bool(args.encoder_csv),
    }
    summary_path = os.path.join(args.out_dir, "graph_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    print(f"plots generated: {len(made)}")
    print(f"summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
