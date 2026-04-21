#!/usr/bin/env python3
"""
Continuous stream logger wrapper.
"""

from __future__ import annotations

import argparse
import sys

from paa5100_diagnostics import run_preflight, run_stream_log
from sensor import DEFAULT_LED_LEVEL, default_config_path, open_sensor, resolve_settings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAA5100 continuous stream logger")
    p.add_argument("--config", default=default_config_path())
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None)
    p.add_argument("--rotation", type=int, default=None, choices=[0, 90, 180, 270])
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--seconds", type=float, default=60.0)
    p.add_argument("--target-hz", type=float, default=30.0)
    p.add_argument("--log-dir", default="logs")
    p.add_argument("--stream-led-on", action="store_true")
    p.add_argument("--stream-led-level", type=int, default=DEFAULT_LED_LEVEL)
    p.add_argument("--max-error-rate", type=float, default=0.01)
    p.add_argument("--max-jitter-ratio", type=float, default=0.40)
    p.add_argument("--min-speed-counts-s", type=float, default=0.0)
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
    return run_stream_log(
        sensor,
        args.log_dir,
        args.seconds,
        args.target_hz,
        args.max_error_rate,
        args.max_jitter_ratio,
        args.min_speed_counts_s,
        args.stream_led_on,
        args.stream_led_level,
        args.include_mem,
    )


if __name__ == "__main__":
    sys.exit(main())
