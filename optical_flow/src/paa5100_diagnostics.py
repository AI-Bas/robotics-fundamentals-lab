#!/usr/bin/env python3
"""
Dedicated diagnostics and benchmark utility for PAA5100JE.

Goals:
- Fast wiring and SPI sanity checks for troubleshooting loose connections.
- Basic communication checks against the sensor.
- Optional LED sanity blink.
- Poll-rate benchmark for motion-control planning.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys
import time
from datetime import datetime
from typing import Callable, Optional

import yaml
from pmw3901 import PAA5100


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


def _default_config_path() -> str:
    here = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(here, "..", "config", "sensor_config.yaml"))


def _load_config(path: str) -> dict:
    if not os.path.exists(path):
        print(f"Config not found at {path}. Using CLI defaults.")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        print(f"Failed to parse config: {exc!r}. Using CLI defaults.")
        return {}


def _cfg_int(cfg: dict, key_path: list[str], default: int) -> int:
    node = cfg
    for key in key_path:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    try:
        return int(node)
    except (TypeError, ValueError):
        return default


def _cfg_bool(cfg: dict, key_path: list[str], default: bool) -> bool:
    node = cfg
    for key in key_path:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    if isinstance(node, bool):
        return node
    if isinstance(node, str):
        value = node.strip().lower()
        if value in {"1", "true", "yes", "on", "y"}:
            return True
        if value in {"0", "false", "no", "off", "n"}:
            return False
    return default


def _print_pin_map(cfg: dict) -> None:
    pins = cfg.get("pins", {}) if isinstance(cfg, dict) else {}
    if not isinstance(pins, dict):
        print("pin map: unavailable")
        return
    fields = ["sck", "mosi", "miso", "cs", "int", "power", "ground"]
    print("pin map: " + ", ".join(f"{k}={pins.get(k, '?')}" for k in fields))


def _process_memory_kb() -> int:
    # ru_maxrss is KB on Linux; useful for long-run stability trending.
    import resource

    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _ensure_log_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _new_csv_path(log_dir: str, stem: str) -> str:
    _ensure_log_dir(log_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(log_dir, f"{stem}_{ts}.csv")


def _new_json_path(log_dir: str, stem: str) -> str:
    _ensure_log_dir(log_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(log_dir, f"{stem}_{ts}.json")


def _write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def _sensor_probe(sensor: PAA5100) -> dict:
    out: dict[str, str] = {}
    for name in ("get_id", "get_motion", "get_motion_slow", "frame_capture"):
        out[f"has_{name}"] = str(callable(getattr(sensor, name, None)))
    get_id = getattr(sensor, "get_id", None)
    if callable(get_id):
        try:
            out["sensor_id"] = str(get_id())
        except Exception as exc:  # pragma: no cover
            out["sensor_id"] = f"error:{exc!r}"
    return out


def _check_spidev_nodes(spi_port: int, spi_cs: int) -> bool:
    preferred = f"/dev/spidev{spi_port}.{spi_cs}"
    fallback = f"/dev/spidev{spi_port}.{1 - spi_cs}" if spi_cs in (0, 1) else None
    all_nodes = sorted(
        name
        for name in os.listdir("/dev")
        if name.startswith("spidev")
    )
    print(f"spidev nodes: {', '.join('/dev/' + n for n in all_nodes) if all_nodes else '(none)'}")
    print(f"preferred node: {preferred} ({'present' if os.path.exists(preferred) else 'missing'})")
    if fallback:
        print(f"alt node: {fallback} ({'present' if os.path.exists(fallback) else 'missing'})")
    return os.path.exists(preferred)


def _error_state(err: str) -> str:
    return "ok" if not err else "error"


def _motion_metrics(dx: int, dy: int, dt: float) -> tuple[float, float, float]:
    speed_counts = math.hypot(dx, dy)
    speed_counts_s = (speed_counts / dt) if dt > 0 else 0.0
    heading_deg = math.degrees(math.atan2(dy, dx)) if (dx != 0 or dy != 0) else 0.0
    return speed_counts, speed_counts_s, heading_deg


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if q <= 0:
        return sorted_values[0]
    if q >= 1:
        return sorted_values[-1]
    idx = q * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    w = idx - lo
    return sorted_values[lo] * (1 - w) + sorted_values[hi] * w


def _build_sensor(spi_port: int, spi_cs: int, rotation: int) -> PAA5100:
    sensor = PAA5100(spi_port=spi_port, spi_cs=spi_cs)
    sensor.set_rotation(rotation)
    return sensor


def open_sensor(spi_port: int, spi_cs: int, rotation: int, auto_cs: bool) -> PAA5100:
    order = [spi_cs]
    if auto_cs and spi_cs in (0, 1):
        other = 1 - spi_cs
        if other not in order:
            order.append(other)

    last: Optional[Exception] = None
    for cs in order:
        try:
            sensor = _build_sensor(spi_port, cs, rotation)
            if cs != spi_cs:
                print(f"init fallback: preferred cs={spi_cs} failed; using cs={cs}")
            else:
                print(f"init ok on spi_port={spi_port}, cs={cs}")
            return sensor
        except Exception as exc:  # pragma: no cover (hardware path)
            last = exc
            print(f"init failed on spi_port={spi_port}, cs={cs}: {exc!r}")

    assert last is not None
    raise last


def _make_led_setter(sensor: PAA5100) -> tuple[Optional[Callable[[bool, int], None]], str]:
    if hasattr(sensor, "set_led"):
        method = getattr(sensor, "set_led")
        if callable(method):
            def _setter(on: bool, level: int) -> None:
                # High-level API may only support on/off.
                method(on)
            return _setter, "set_led(bool)"
    write_fn = getattr(sensor, "_write", None)
    if callable(write_fn):
        def _setter(on: bool, level: int) -> None:
            level = max(0, min(0xD5, int(level)))
            write_fn(0x7F, 0x14)
            write_fn(0x6F, level if on else 0x00)
            write_fn(0x7F, 0x00)
        return _setter, "private _write(register, value)"
    return None, "no LED control path"


def run_preflight(cfg: dict, spi_port: int, spi_cs: int) -> int:
    print("=== Preflight ===")
    print(f"time: {_now_iso()}")
    _print_pin_map(cfg)
    has_node = _check_spidev_nodes(spi_port, spi_cs)
    if not has_node:
        print("FAIL: preferred SPI node missing. Check SPI enable and chip-select mapping.")
        return 1
    print("PASS: preferred SPI node is present.")
    return 0


def run_comm(sensor: PAA5100, samples: int) -> int:
    print("=== Communication Check ===")
    ok = 0
    failed = 0
    for i in range(samples):
        try:
            dx, dy = sensor.get_motion()
            ok += 1
            print(f"sample {i + 1}/{samples}: dx={dx:4d} dy={dy:4d}")
        except Exception as exc:  # pragma: no cover (hardware path)
            failed += 1
            print(f"sample {i + 1}/{samples}: ERROR {exc!r}")
        time.sleep(0.02)
    print(f"comm summary: ok={ok}, failed={failed}")
    return 0 if ok > 0 and failed == 0 else 1


def run_comm_log(sensor: PAA5100, samples: int, log_dir: str, include_mem: bool) -> int:
    print("=== Communication CSV Log ===")
    csv_path = _new_csv_path(log_dir, "paa5100_comm")
    print(f"log: {csv_path}")
    t_prev = time.perf_counter()
    ok = 0
    failed = 0

    mem0 = _process_memory_kb()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = [
            "ts_iso",
            "seq",
            "dt_s",
            "dx",
            "dy",
            "speed_counts",
            "speed_counts_s",
            "flow_heading_deg",
            "error_state",
            "error",
            "clock_monotonic_s",
            "clock_process_s",
        ]
        if include_mem:
            header.append("process_mem_kb")
        w.writerow(header)
        for i in range(samples):
            now = time.perf_counter()
            dt = now - t_prev if i > 0 else 0.0
            t_prev = now
            dx = 0
            dy = 0
            err = ""
            try:
                dx, dy = sensor.get_motion()
                ok += 1
            except Exception as exc:  # pragma: no cover
                failed += 1
                err = repr(exc)
            speed_counts, speed_counts_s, heading_deg = _motion_metrics(dx, dy, dt)
            row = [
                _now_iso(),
                i,
                f"{dt:.6f}",
                dx,
                dy,
                f"{speed_counts:.3f}",
                f"{speed_counts_s:.3f}",
                f"{heading_deg:.3f}",
                _error_state(err),
                err,
                f"{time.monotonic():.6f}",
                f"{time.process_time():.6f}",
            ]
            if include_mem:
                row.append(_process_memory_kb())
            w.writerow(
                row
            )
            f.flush()
            time.sleep(0.02)
    mem1 = _process_memory_kb()
    summary = {
        "kind": "paa5100_comm_log_summary",
        "timestamp": _now_iso(),
        "csv_path": csv_path,
        "samples": samples,
        "ok": ok,
        "failed": failed,
        "error_rate": failed / max(1, samples),
        "include_mem": include_mem,
        "process_mem_kb_start": mem0,
        "process_mem_kb_end": mem1,
        "process_mem_kb_delta": mem1 - mem0,
    }
    summary_path = _new_json_path(log_dir, "paa5100_comm_summary")
    _write_json(summary_path, summary)
    print(f"summary: {summary_path}")
    print(f"comm log summary: ok={ok}, failed={failed}")
    return 0 if ok > 0 and failed == 0 else 1


def run_led(sensor: PAA5100, blink_count: int, blink_period: float, led_level: int) -> int:
    print("=== LED Sanity Check ===")
    set_led, source = _make_led_setter(sensor)
    print(f"led path: {source}")
    if set_led is None:
        print("FAIL: LED control path not available in this package version.")
        return 2
    try:
        for i in range(blink_count):
            set_led(True, led_level)
            print(f"{_now_iso()} blink {i + 1}/{blink_count}: ON (level={led_level})")
            time.sleep(blink_period)
            set_led(False, led_level)
            print(f"{_now_iso()} blink {i + 1}/{blink_count}: OFF")
            time.sleep(blink_period)
    except Exception as exc:  # pragma: no cover (hardware path)
        print(f"FAIL: LED check failed: {exc!r}")
        return 1
    print("PASS: LED check completed.")
    return 0


def run_poll_benchmark(sensor: PAA5100, seconds: float) -> int:
    print("=== Poll Rate Benchmark ===")
    print(f"duration: {seconds:.2f}s")
    times: list[float] = []
    errors = 0
    reads = 0
    t_end = time.perf_counter() + seconds
    t_prev = time.perf_counter()

    while time.perf_counter() < t_end:
        try:
            sensor.get_motion()
            now = time.perf_counter()
            times.append(now - t_prev)
            t_prev = now
            reads += 1
        except Exception:  # pragma: no cover (hardware path)
            errors += 1

    if not times:
        print("FAIL: no successful reads.")
        return 1

    valid = times[1:] if len(times) > 1 else times
    mean_dt = statistics.fmean(valid)
    min_dt = min(valid)
    max_dt = max(valid)
    hz_mean = (1.0 / mean_dt) if mean_dt > 0 else 0.0
    hz_peak = (1.0 / min_dt) if min_dt > 0 else 0.0
    hz_floor = (1.0 / max_dt) if max_dt > 0 else 0.0

    print(f"reads: {reads}, errors: {errors}")
    print(f"mean_dt_s: {mean_dt:.6f}")
    print(f"min_dt_s:  {min_dt:.6f}")
    print(f"max_dt_s:  {max_dt:.6f}")
    print(f"mean_hz:   {hz_mean:.1f}")
    print(f"peak_hz:   {hz_peak:.1f}")
    print(f"floor_hz:  {hz_floor:.1f}")
    return 0


def run_poll_benchmark_log(sensor: PAA5100, seconds: float, log_dir: str, include_mem: bool) -> int:
    print("=== Poll Rate Benchmark + CSV ===")
    csv_path = _new_csv_path(log_dir, "paa5100_benchmark")
    print(f"log: {csv_path}")
    t_end = time.perf_counter() + seconds
    t_prev = time.perf_counter()
    reads = 0
    errors = 0
    dts: list[float] = []

    mem0 = _process_memory_kb()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = [
            "ts_iso",
            "seq",
            "dt_s",
            "inst_hz",
            "dx",
            "dy",
            "speed_counts",
            "speed_counts_s",
            "flow_heading_deg",
            "ok",
            "error_state",
            "error",
            "clock_monotonic_s",
            "clock_process_s",
        ]
        if include_mem:
            header.append("process_mem_kb")
        w.writerow(header)
        seq = 0
        while time.perf_counter() < t_end:
            t_loop = time.perf_counter()
            dt = t_loop - t_prev if seq > 0 else 0.0
            t_prev = t_loop
            hz = (1.0 / dt) if dt > 0 else 0.0
            dx = 0
            dy = 0
            ok = 1
            err = ""
            try:
                dx, dy = sensor.get_motion()
                reads += 1
                if dt > 0:
                    dts.append(dt)
            except Exception as exc:  # pragma: no cover
                errors += 1
                ok = 0
                err = repr(exc)
            speed_counts, speed_counts_s, heading_deg = _motion_metrics(dx, dy, dt)
            row = [
                _now_iso(),
                seq,
                f"{dt:.6f}",
                f"{hz:.3f}",
                dx,
                dy,
                f"{speed_counts:.3f}",
                f"{speed_counts_s:.3f}",
                f"{heading_deg:.3f}",
                ok,
                _error_state(err),
                err,
                f"{time.monotonic():.6f}",
                f"{time.process_time():.6f}",
            ]
            if include_mem:
                row.append(_process_memory_kb())

            w.writerow(row)
            if seq % 200 == 0:
                f.flush()
            seq += 1

    if not dts:
        print("FAIL: no successful benchmark reads.")
        return 1

    mean_dt = statistics.fmean(dts)
    min_dt = min(dts)
    max_dt = max(dts)
    jitter = statistics.pstdev(dts) if len(dts) > 1 else 0.0
    sorted_dts = sorted(dts)
    p50_dt = _quantile(sorted_dts, 0.50)
    p95_dt = _quantile(sorted_dts, 0.95)
    p99_dt = _quantile(sorted_dts, 0.99)
    print(f"reads={reads}, errors={errors}, error_rate={errors / max(1, (reads + errors)):.3f}")
    print(f"mean_hz={(1.0 / mean_dt):.1f}, peak_hz={(1.0 / min_dt):.1f}, floor_hz={(1.0 / max_dt):.1f}")
    print(
        f"p50_hz={(1.0 / p50_dt) if p50_dt > 0 else 0.0:.1f}, "
        f"p95_hz={(1.0 / p95_dt) if p95_dt > 0 else 0.0:.1f}, "
        f"p99_hz={(1.0 / p99_dt) if p99_dt > 0 else 0.0:.1f}"
    )
    print(f"dt_jitter_std_s={jitter:.6f}")
    mem1 = _process_memory_kb()
    summary = {
        "kind": "paa5100_benchmark_summary",
        "timestamp": _now_iso(),
        "csv_path": csv_path,
        "seconds": seconds,
        "reads": reads,
        "errors": errors,
        "error_rate": errors / max(1, reads + errors),
        "mean_dt_s": mean_dt,
        "min_dt_s": min_dt,
        "max_dt_s": max_dt,
        "mean_hz": (1.0 / mean_dt) if mean_dt > 0 else 0.0,
        "peak_hz": (1.0 / min_dt) if min_dt > 0 else 0.0,
        "floor_hz": (1.0 / max_dt) if max_dt > 0 else 0.0,
        "p50_hz": (1.0 / p50_dt) if p50_dt > 0 else 0.0,
        "p95_hz": (1.0 / p95_dt) if p95_dt > 0 else 0.0,
        "p99_hz": (1.0 / p99_dt) if p99_dt > 0 else 0.0,
        "dt_jitter_std_s": jitter,
        "include_mem": include_mem,
        "process_mem_kb_start": mem0,
        "process_mem_kb_end": mem1,
        "process_mem_kb_delta": mem1 - mem0,
    }
    summary_path = _new_json_path(log_dir, "paa5100_benchmark_summary")
    _write_json(summary_path, summary)
    print(f"summary: {summary_path}")
    return 0


def run_stable_rate_sweep(
    sensor: PAA5100,
    log_dir: str,
    start_hz: float,
    stop_hz: float,
    step_hz: float,
    hold_s: float,
    max_error_rate: float,
    max_jitter_ratio: float,
    include_mem: bool,
) -> int:
    print("=== Stable Poll-Rate Sweep ===")
    csv_path = _new_csv_path(log_dir, "paa5100_rate_sweep")
    print(f"log: {csv_path}")

    rate = start_hz
    best_stable = 0.0
    rows: list[list[object]] = []
    mem0 = _process_memory_kb()
    while rate <= stop_hz + 1e-9:
        target_dt = 1.0 / rate
        t_end = time.perf_counter() + hold_s
        errors = 0
        reads = 0
        dts: list[float] = []
        t_prev_success: Optional[float] = None
        next_tick = time.perf_counter()
        while time.perf_counter() < t_end:
            now = time.perf_counter()
            if now < next_tick:
                time.sleep(next_tick - now)
            loop_start = time.perf_counter()
            try:
                sensor.get_motion()
                reads += 1
                if t_prev_success is not None:
                    dts.append(loop_start - t_prev_success)
                t_prev_success = loop_start
            except Exception:  # pragma: no cover
                errors += 1
            next_tick += target_dt

        error_rate = errors / max(1, reads + errors)
        jitter = statistics.pstdev(dts) if len(dts) > 1 else 0.0
        jitter_ratio = (jitter / target_dt) if target_dt > 0 else 999.0
        mean_hz = (1.0 / statistics.fmean(dts)) if dts else 0.0
        expected_reads = max(1, int(hold_s * rate))
        min_reads_for_stable = max(5, int(expected_reads * 0.8))
        achieved_ratio = (mean_hz / rate) if rate > 0 else 0.0
        stable = int(
            error_rate <= max_error_rate
            and jitter_ratio <= max_jitter_ratio
            and reads >= min_reads_for_stable
            and achieved_ratio >= 0.8
        )
        if stable:
            best_stable = rate
        print(
            f"rate={rate:.1f}Hz mean={mean_hz:.1f}Hz errors={errors} "
            f"error_rate={error_rate:.3f} jitter_ratio={jitter_ratio:.3f} "
            f"reads={reads}/{min_reads_for_stable}+ stable={bool(stable)}"
        )
        rows.append(
            [
                _now_iso(),
                f"{rate:.3f}",
                f"{target_dt:.6f}",
                reads,
                errors,
                f"{error_rate:.6f}",
                f"{jitter:.6f}",
                f"{jitter_ratio:.6f}",
                f"{mean_hz:.3f}",
                f"{achieved_ratio:.6f}",
                min_reads_for_stable,
                stable,
            ]
        )
        if include_mem:
            rows[-1].append(_process_memory_kb())
        rate += step_hz

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = [
            "ts_iso",
            "target_hz",
            "target_dt_s",
            "reads",
            "errors",
            "error_rate",
            "dt_jitter_std_s",
            "jitter_ratio_to_target_dt",
            "mean_achieved_hz",
            "achieved_ratio",
            "min_reads_for_stable",
            "stable",
        ]
        if include_mem:
            header.append("process_mem_kb")
        w.writerow(header)
        w.writerows(rows)

    print(f"highest_stable_hz: {best_stable:.1f}")
    mem1 = _process_memory_kb()
    summary = {
        "kind": "paa5100_rate_sweep_summary",
        "timestamp": _now_iso(),
        "csv_path": csv_path,
        "start_hz": start_hz,
        "stop_hz": stop_hz,
        "step_hz": step_hz,
        "hold_s": hold_s,
        "max_error_rate": max_error_rate,
        "max_jitter_ratio": max_jitter_ratio,
        "highest_stable_hz": best_stable,
        "include_mem": include_mem,
        "process_mem_kb_start": mem0,
        "process_mem_kb_end": mem1,
        "process_mem_kb_delta": mem1 - mem0,
    }
    summary_path = _new_json_path(log_dir, "paa5100_rate_sweep_summary")
    _write_json(summary_path, summary)
    print(f"summary: {summary_path}")
    return 0 if best_stable > 0 else 1


def run_stream_log(
    sensor: PAA5100,
    log_dir: str,
    seconds: float,
    target_hz: float,
    max_error_rate: float,
    max_jitter_ratio: float,
    min_speed_counts_s: float,
    include_mem: bool,
) -> int:
    print("=== Continuous Stream Log ===")
    csv_path = _new_csv_path(log_dir, "paa5100_stream")
    print(f"log: {csv_path}")
    target_dt = 1.0 / target_hz if target_hz > 0 else 0.0
    end_t = time.perf_counter() + seconds
    next_tick = time.perf_counter()
    seq = 0
    errors = 0
    reads = 0
    dts: list[float] = []
    speeds: list[float] = []
    t_prev: Optional[float] = None
    mem0 = _process_memory_kb()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = [
            "ts_iso",
            "seq",
            "target_hz",
            "dt_s",
            "inst_hz",
            "dx",
            "dy",
            "speed_counts",
            "speed_counts_s",
            "flow_heading_deg",
            "error_state",
            "error",
            "quality_flag",
            "clock_monotonic_s",
            "clock_process_s",
        ]
        if include_mem:
            header.append("process_mem_kb")
        w.writerow(header)

        while time.perf_counter() < end_t:
            now = time.perf_counter()
            if target_dt > 0 and now < next_tick:
                time.sleep(next_tick - now)
            t_loop = time.perf_counter()
            dt = (t_loop - t_prev) if t_prev is not None else 0.0
            t_prev = t_loop
            hz = (1.0 / dt) if dt > 0 else 0.0
            dx = 0
            dy = 0
            err = ""
            try:
                dx, dy = sensor.get_motion()
                reads += 1
                if dt > 0:
                    dts.append(dt)
            except Exception as exc:  # pragma: no cover
                err = repr(exc)
                errors += 1

            speed_counts, speed_counts_s, heading_deg = _motion_metrics(dx, dy, dt)
            speeds.append(speed_counts_s)
            quality = "nominal"
            if err:
                quality = "sensor_error"
            elif target_hz > 0 and hz < (0.7 * target_hz):
                quality = "timing_lag"
            elif speed_counts_s < min_speed_counts_s:
                quality = "low_signal"

            row = [
                _now_iso(),
                seq,
                f"{target_hz:.3f}",
                f"{dt:.6f}",
                f"{hz:.3f}",
                dx,
                dy,
                f"{speed_counts:.3f}",
                f"{speed_counts_s:.3f}",
                f"{heading_deg:.3f}",
                _error_state(err),
                err,
                quality,
                f"{time.monotonic():.6f}",
                f"{time.process_time():.6f}",
            ]
            if include_mem:
                row.append(_process_memory_kb())
            w.writerow(row)
            if seq % 200 == 0:
                f.flush()
            seq += 1
            if target_dt > 0:
                next_tick += target_dt

    mem1 = _process_memory_kb()
    jitter = statistics.pstdev(dts) if len(dts) > 1 else 0.0
    mean_hz = (1.0 / statistics.fmean(dts)) if dts else 0.0
    error_rate = errors / max(1, reads + errors)
    jitter_ratio = (jitter / target_dt) if target_dt > 0 else 0.0
    speed_mean = statistics.fmean(speeds) if speeds else 0.0
    unreliable_reasons: list[str] = []
    if error_rate > max_error_rate:
        unreliable_reasons.append("HIGH_ERROR_RATE")
    if jitter_ratio > max_jitter_ratio:
        unreliable_reasons.append("HIGH_JITTER")
    if target_hz > 0 and mean_hz < (0.8 * target_hz):
        unreliable_reasons.append("LOW_EFFECTIVE_RATE")
    if min_speed_counts_s > 0 and speed_mean < min_speed_counts_s:
        unreliable_reasons.append("LOW_SIGNAL")

    summary = {
        "kind": "paa5100_stream_summary",
        "timestamp": _now_iso(),
        "csv_path": csv_path,
        "seconds": seconds,
        "target_hz": target_hz,
        "reads": reads,
        "errors": errors,
        "error_rate": error_rate,
        "mean_hz": mean_hz,
        "dt_jitter_std_s": jitter,
        "jitter_ratio_to_target_dt": jitter_ratio,
        "mean_speed_counts_s": speed_mean,
        "stream_reliable": len(unreliable_reasons) == 0,
        "unreliable_reasons": unreliable_reasons,
        "thresholds": {
            "max_error_rate": max_error_rate,
            "max_jitter_ratio": max_jitter_ratio,
            "min_speed_counts_s": min_speed_counts_s,
            "min_effective_rate_ratio": 0.8,
        },
        "include_mem": include_mem,
        "process_mem_kb_start": mem0,
        "process_mem_kb_end": mem1,
        "process_mem_kb_delta": mem1 - mem0,
    }
    summary_path = _new_json_path(log_dir, "paa5100_stream_summary")
    _write_json(summary_path, summary)
    print(f"summary: {summary_path}")
    print(f"stream reliability: {summary['stream_reliable']}")
    return 0 if summary["stream_reliable"] else 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAA5100 diagnostics and poll benchmark")
    p.add_argument("--config", default=_default_config_path(), help="Path to sensor YAML config")
    p.add_argument(
        "--mode",
        choices=["preflight", "comm", "comm-log", "led", "benchmark", "benchmark-log", "rate-sweep", "stream-log", "all"],
        default="all",
    )
    p.add_argument("--spi-port", type=int, default=None)
    p.add_argument("--spi-cs", type=int, default=None, help="0=CE0(GPIO8), 1=CE1(GPIO7)")
    p.add_argument("--rotation", type=int, default=None, choices=[0, 90, 180, 270])
    p.add_argument("--no-auto-cs", action="store_true")
    p.add_argument("--comm-samples", type=int, default=12)
    p.add_argument("--blink-count", type=int, default=4)
    p.add_argument("--blink-period", type=float, default=0.25)
    p.add_argument("--led-level", type=int, default=0x1C, help="LED brightness register value 0..213 (0xD5)")
    p.add_argument("--bench-seconds", type=float, default=5.0)
    p.add_argument("--log-dir", default="logs")
    p.add_argument("--sweep-start-hz", type=float, default=10.0)
    p.add_argument("--sweep-stop-hz", type=float, default=120.0)
    p.add_argument("--sweep-step-hz", type=float, default=10.0)
    p.add_argument("--sweep-hold-s", type=float, default=2.0)
    p.add_argument("--max-error-rate", type=float, default=0.01)
    p.add_argument("--max-jitter-ratio", type=float, default=0.40)
    p.add_argument("--stream-seconds", type=float, default=30.0)
    p.add_argument("--stream-target-hz", type=float, default=30.0)
    p.add_argument("--min-speed-counts-s", type=float, default=0.0)
    p.add_argument("--include-mem", action="store_true", help="Include process_mem_kb columns in CSV logs")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = _load_config(args.config)
    spi_port = args.spi_port if args.spi_port is not None else _cfg_int(cfg, ["spi", "port"], 0)
    spi_cs = args.spi_cs if args.spi_cs is not None else _cfg_int(cfg, ["spi", "cs"], 1)
    rotation = args.rotation if args.rotation is not None else _cfg_int(cfg, ["sensor_runtime", "rotation"], 0)
    auto_cs_cfg = _cfg_bool(cfg, ["spi", "auto_cs"], True)
    auto_cs = (not args.no_auto_cs) and auto_cs_cfg

    print(f"config: {args.config}")
    print(f"effective settings: spi_port={spi_port}, spi_cs={spi_cs}, rotation={rotation}, auto_cs={auto_cs}")

    if args.mode == "preflight":
        return run_preflight(cfg, spi_port, spi_cs)

    preflight_rc = run_preflight(cfg, spi_port, spi_cs)
    if preflight_rc != 0 and args.mode == "all":
        return preflight_rc

    try:
        sensor = open_sensor(spi_port, spi_cs, rotation, auto_cs=auto_cs)
    except Exception as exc:  # pragma: no cover (hardware path)
        print(f"FAIL: sensor open failed: {exc!r}")
        return 1
    probe = _sensor_probe(sensor)
    if probe:
        print("sensor probe: " + ", ".join(f"{k}={v}" for k, v in sorted(probe.items())))

    if args.mode == "comm":
        return run_comm(sensor, args.comm_samples)
    if args.mode == "comm-log":
        return run_comm_log(sensor, args.comm_samples, args.log_dir, args.include_mem)
    if args.mode == "led":
        return run_led(sensor, args.blink_count, args.blink_period, args.led_level)
    if args.mode == "benchmark":
        return run_poll_benchmark(sensor, args.bench_seconds)
    if args.mode == "benchmark-log":
        return run_poll_benchmark_log(sensor, args.bench_seconds, args.log_dir, args.include_mem)
    if args.mode == "rate-sweep":
        return run_stable_rate_sweep(
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
    if args.mode == "stream-log":
        return run_stream_log(
            sensor,
            args.log_dir,
            args.stream_seconds,
            args.stream_target_hz,
            args.max_error_rate,
            args.max_jitter_ratio,
            args.min_speed_counts_s,
            args.include_mem,
        )

    results = [
        run_comm(sensor, args.comm_samples),
        run_led(sensor, args.blink_count, args.blink_period, args.led_level),
        run_poll_benchmark_log(sensor, args.bench_seconds, args.log_dir, args.include_mem),
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
        ),
        run_stream_log(
            sensor,
            args.log_dir,
            args.stream_seconds,
            args.stream_target_hz,
            args.max_error_rate,
            args.max_jitter_ratio,
            args.min_speed_counts_s,
            args.include_mem,
        ),
    ]
    return 0 if all(rc == 0 for rc in results) else 1


if __name__ == "__main__":
    sys.exit(main())
