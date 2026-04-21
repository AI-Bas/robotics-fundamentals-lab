#!/usr/bin/env python3
"""
Benchmark and test logging wrapper.
"""

from __future__ import annotations

import argparse
import sys

from of_diagnostics import run_poll_benchmark_log, run_preflight, run_stable_rate_sweep
from of_sensor import default_config_path, open_sensor, resolve_settings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAA5100 benchmark and sweep logger")
    p.add_argument("--config", default=default_config_path())
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None)
    p.add_argument("--rotation", type=int, default=None, choices=[0, 90, 180, 270])
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--mode", choices=["benchmark", "sweep", "both"], default="both")
    p.add_argument("--bench-seconds", type=float, default=20.0)
    p.add_argument("--log-dir", default="logs")
    p.add_argument("--sweep-start-hz", type=float, default=5.0)
    p.add_argument("--sweep-stop-hz", type=float, default=80.0)
    p.add_argument("--sweep-step-hz", type=float, default=5.0)
    p.add_argument("--sweep-hold-s", type=float, default=3.0)
    p.add_argument("--max-error-rate", type=float, default=0.01)
    p.add_argument("--max-jitter-ratio", type=float, default=0.40)
    p.add_argument("--include-mem", action="store_true")
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

    results = []
    if args.mode in {"benchmark", "both"}:
        results.append(run_poll_benchmark_log(sensor, args.bench_seconds, args.log_dir, args.include_mem))
    if args.mode in {"sweep", "both"}:
        results.append(
            run_stable_rate_sweep(
                sensor,
                args.log_dir,
                args.sweep_start_hz,
                args.sweep_stop_hz,
                args.sweep_step_hz,
                args.sweep_hold_s,
                args.max_error_rate,
                args.max_jitter_ratio,
                args.include_mem,
            )
        )
    return 0 if all(r == 0 for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
