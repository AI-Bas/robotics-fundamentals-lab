#!/usr/bin/env python3
"""
First-pass hardware test for PAA5100JE on Raspberry Pi.

Modes:
- info: print detected API paths and basic sensor checks
- motion: sample motion and write CSV with basic diagnostics
- led: try toggling illumination LEDs (if available) and optionally blink

This script is intentionally defensive because LED control support depends on
library version and undocumented sensor behavior.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from typing import Callable, Optional

from pmw3901 import PAA5100


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


def _build_sensor(spi_port: int, spi_cs: int, rotation: int) -> PAA5100:
    sensor = PAA5100(spi_port=spi_port, spi_cs=spi_cs)
    sensor.set_rotation(rotation)
    return sensor


def _spi_troubleshoot_text() -> str:
    return (
        "\nSPI / chip-select troubleshooting (Product ID 0x00 usually means no MISO data):\n"
        "  1) raspi-config: enable SPI, then reboot.\n"
        "  2) Check: ls /dev/spidev0.*  (expect spidev0.0 and/or spidev0.1)\n"
        "  3) Wiring: SCK/MOSI/MISO/3V3/GND + CS to CE0 (GPIO8) or CE1 (GPIO7) on SPI0.\n"
        "     Pimoroni 'front' slot often uses BCM7 → try --spi-cs 1 first, then --spi-cs 0.\n"
        "  4) Re-run with the other CE:  python src/paa5100_first_test.py --mode info --spi-cs 0\n"
        "     or:  ... --spi-cs 1\n"
        "  5) If still 0x00: loose wire, wrong bus (not SPI0), or sensor not powered.\n"
    )


def open_sensor(
    spi_port: int,
    spi_cs: int,
    rotation: int,
    *,
    auto_cs: bool,
) -> PAA5100:
    """Open PAA5100; optionally try the other SPI chip-select if the first fails."""
    order = [spi_cs]
    if auto_cs and spi_cs in (0, 1):
        other = 1 - spi_cs
        if other not in order:
            order.append(other)

    last: Optional[Exception] = None
    for cs in order:
        try:
            sensor = _build_sensor(spi_port, cs, rotation)
            if len(order) > 1 and cs != spi_cs:
                print(f"Note: init OK with --spi-cs {cs} (preferred {spi_cs} failed).")
            elif len(order) > 1:
                print(f"Note: init OK with --spi-cs {cs}.")
            return sensor
        except Exception as exc:  # pragma: no cover (hardware)
            last = exc
            print(f"Tried spi_port={spi_port} spi_cs={cs}: {exc!r}")

    assert last is not None
    print(_spi_troubleshoot_text())
    raise last


def _make_led_setter(sensor: PAA5100) -> tuple[Optional[Callable[[bool], None]], str]:
    """Return (setter, source) where source describes the method path used."""
    # 1) Preferred: library-provided high-level method if available.
    if hasattr(sensor, "set_led"):
        method = getattr(sensor, "set_led")
        if callable(method):
            return method, "set_led(bool)"

    # 2) Fallback: raw/private register writes seen in community examples.
    #    Bank select: 0x7F=0x14, brightness/on register: 0x6F.
    #    on -> 0x1C, off -> 0x00.
    write_fn = getattr(sensor, "_write", None)
    if callable(write_fn):
        def _setter(on: bool) -> None:
            write_fn(0x7F, 0x14)
            write_fn(0x6F, 0x1C if on else 0x00)
            write_fn(0x7F, 0x00)

        return _setter, "private _write(register, value)"

    return None, "no LED control path available"


def run_info(sensor: PAA5100) -> int:
    print("=== PAA5100 Info ===")
    print(f"time: {_now_iso()}")

    set_led, source = _make_led_setter(sensor)
    print(f"LED path: {source}")
    print(f"get_motion available: {callable(getattr(sensor, 'get_motion', None))}")

    # Smoke read
    try:
        dx, dy = sensor.get_motion()
        print(f"motion read ok: dx={dx}, dy={dy}")
    except Exception as exc:  # pragma: no cover (hardware/runtime path)
        print(f"motion read failed: {exc!r}")
        return 1

    if set_led is None:
        print("LED control not exposed in this environment/package version.")
    else:
        print("LED control appears available.")

    return 0


def run_led(sensor: PAA5100, blink_count: int, blink_period: float) -> int:
    print("=== LED Test ===")
    set_led, source = _make_led_setter(sensor)
    print(f"LED path: {source}")

    if set_led is None:
        print("Cannot control LED in this package/version. Use motion test instead.")
        return 2

    try:
        for i in range(blink_count):
            set_led(True)
            print(f"{_now_iso()} blink {i + 1}/{blink_count}: ON")
            time.sleep(blink_period)
            set_led(False)
            print(f"{_now_iso()} blink {i + 1}/{blink_count}: OFF")
            time.sleep(blink_period)
    except Exception as exc:  # pragma: no cover (hardware/runtime path)
        print(f"LED test failed: {exc!r}")
        return 1

    return 0


def run_motion(sensor: PAA5100, seconds: float, rate_hz: float, log_dir: str) -> int:
    print("=== Motion + CSV Test ===")
    os.makedirs(log_dir, exist_ok=True)
    csv_name = datetime.now().strftime("paa5100_test_%Y%m%d_%H%M%S.csv")
    csv_path = os.path.join(log_dir, csv_name)
    dt_target = 1.0 / rate_hz

    seq = 0
    total_x = 0
    total_y = 0
    t_start = time.perf_counter()
    t_prev = t_start

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "ts_iso",
                "seq",
                "dx",
                "dy",
                "dt_s",
                "vx_counts_s",
                "vy_counts_s",
                "total_x",
                "total_y",
                "spi_ok",
                "led_action",
                "error",
            ]
        )

        print(f"logging to: {csv_path}")

        while (time.perf_counter() - t_start) < seconds:
            t_loop = time.perf_counter()
            dt = t_loop - t_prev if seq > 0 else dt_target
            t_prev = t_loop

            spi_ok = 1
            err = ""
            led_action = "none"

            try:
                dx, dy = sensor.get_motion()
            except Exception as exc:  # pragma: no cover (hardware/runtime path)
                dx, dy = 0, 0
                spi_ok = 0
                err = repr(exc)

            total_x += dx
            total_y += dy
            vx = (dx / dt) if dt > 0 else 0.0
            vy = (dy / dt) if dt > 0 else 0.0

            writer.writerow(
                [
                    _now_iso(),
                    seq,
                    dx,
                    dy,
                    f"{dt:.6f}",
                    f"{vx:.3f}",
                    f"{vy:.3f}",
                    total_x,
                    total_y,
                    spi_ok,
                    led_action,
                    err,
                ]
            )
            f.flush()

            if seq % int(max(1, rate_hz)) == 0:
                print(f"seq={seq:05d} dx={dx:4d} dy={dy:4d} total=({total_x},{total_y})")

            seq += 1
            elapsed = time.perf_counter() - t_loop
            time.sleep(max(0.0, dt_target - elapsed))

    print("done.")
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAA5100 first hardware test utility")
    p.add_argument("--mode", choices=["info", "led", "motion"], default="info")
    p.add_argument("--spi-port", type=int, default=0)
    p.add_argument("--spi-cs", type=int, default=1, help="0 = CE0 (GPIO8), 1 = CE1 (GPIO7) on SPI0")
    p.add_argument(
        "--no-auto-cs",
        action="store_true",
        help="Do not try the other chip-select if the first init fails",
    )
    p.add_argument("--rotation", type=int, default=0, choices=[0, 90, 180, 270])

    p.add_argument("--blink-count", type=int, default=6)
    p.add_argument("--blink-period", type=float, default=0.4)

    p.add_argument("--seconds", type=float, default=15.0)
    p.add_argument("--rate-hz", type=float, default=50.0)
    p.add_argument("--log-dir", default="logs")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        sensor = open_sensor(
            args.spi_port,
            args.spi_cs,
            args.rotation,
            auto_cs=not args.no_auto_cs,
        )
    except Exception as exc:  # pragma: no cover (hardware/runtime path)
        print(f"sensor init failed after tries: {exc!r}")
        return 1

    if args.mode == "info":
        return run_info(sensor)
    if args.mode == "led":
        return run_led(sensor, args.blink_count, args.blink_period)
    return run_motion(sensor, args.seconds, args.rate_hz, args.log_dir)


if __name__ == "__main__":
    sys.exit(main())

