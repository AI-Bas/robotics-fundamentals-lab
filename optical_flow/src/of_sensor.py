#!/usr/bin/env python3
"""
Shared sensor/config helpers for optical-flow scripts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Optional
import time

import yaml
from pmw3901 import PAA5100

_LED_LEVEL_MAX = 0xD5
_LED_LEVEL_MIN = 0x00


@dataclass
class SensorSettings:
    config_path: str
    spi_port: int
    spi_cs: int
    rotation: int
    auto_cs: bool
    cfg: dict


def default_config_path() -> str:
    here = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(here, "..", "config", "sensor_config.yaml"))


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


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
        if value in {"true", "1", "yes", "y", "on"}:
            return True
        if value in {"false", "0", "no", "n", "off"}:
            return False
    return default


def resolve_settings(
    *,
    config_path: str,
    spi_port_override: int | None,
    spi_cs_override: int | None,
    rotation_override: int | None,
    no_auto_cs: bool,
) -> SensorSettings:
    cfg = load_config(config_path)
    spi_port = spi_port_override if spi_port_override is not None else _cfg_int(cfg, ["spi", "port"], 0)
    spi_cs = spi_cs_override if spi_cs_override is not None else _cfg_int(cfg, ["spi", "cs"], 1)
    rotation = rotation_override if rotation_override is not None else _cfg_int(cfg, ["sensor_runtime", "rotation"], 0)
    auto_cs_cfg = _cfg_bool(cfg, ["spi", "auto_cs"], True)
    return SensorSettings(
        config_path=config_path,
        spi_port=spi_port,
        spi_cs=spi_cs,
        rotation=rotation,
        auto_cs=(not no_auto_cs) and auto_cs_cfg,
        cfg=cfg,
    )


def build_sensor(spi_port: int, spi_cs: int, rotation: int) -> PAA5100:
    sensor = PAA5100(spi_port=spi_port, spi_cs=spi_cs)
    sensor.set_rotation(rotation)
    return sensor


def open_sensor(spi_port: int, spi_cs: int, rotation: int, auto_cs: bool) -> PAA5100:
    order = [spi_cs]
    if auto_cs and spi_cs in (0, 1):
        order.append(1 - spi_cs)
    last: Optional[Exception] = None
    for cs in order:
        try:
            sensor = build_sensor(spi_port, cs, rotation)
            if cs != spi_cs:
                print(f"init fallback: preferred cs={spi_cs} failed; using cs={cs}")
            return sensor
        except Exception as exc:  # pragma: no cover
            last = exc
            print(f"init failed on spi_port={spi_port}, cs={cs}: {exc!r}")
    assert last is not None
    raise last


def led_setter(sensor: PAA5100) -> tuple[Optional[Callable[[bool, int], None]], str]:
    if hasattr(sensor, "set_led"):
        method = getattr(sensor, "set_led")
        if callable(method):
            def _setter(on: bool, level: int) -> None:
                # High-level API path may ignore brightness.
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


def sensor_probe(sensor: PAA5100) -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("get_id", "get_motion", "get_motion_slow", "frame_capture"):
        out[f"has_{name}"] = str(callable(getattr(sensor, name, None)))
    get_id = getattr(sensor, "get_id", None)
    if callable(get_id):
        try:
            out["sensor_id"] = str(get_id())
        except Exception as exc:  # pragma: no cover
            out["sensor_id"] = f"error:{exc!r}"
    out["has_private_read"] = str(callable(getattr(sensor, "_read", None)))
    out["has_private_write"] = str(callable(getattr(sensor, "_write", None)))
    return out


def supports_raw_register_access(sensor: PAA5100) -> bool:
    return callable(getattr(sensor, "_read", None)) and callable(getattr(sensor, "_write", None))


def read_register(sensor: PAA5100, register: int) -> int:
    read_fn = getattr(sensor, "_read", None)
    if not callable(read_fn):
        raise RuntimeError("Raw register read not available")
    return int(read_fn(register))


def write_register(sensor: PAA5100, register: int, value: int) -> None:
    write_fn = getattr(sensor, "_write", None)
    if not callable(write_fn):
        raise RuntimeError("Raw register write not available")
    write_fn(register, value)


def motion_burst_snapshot(sensor: PAA5100) -> dict[str, Any]:
    snap: dict[str, Any] = {"ok": False}
    try:
        dx, dy = sensor.get_motion()
        snap.update({"ok": True, "dx": int(dx), "dy": int(dy)})
    except Exception as exc:  # pragma: no cover
        snap["error"] = repr(exc)
        return snap
    if supports_raw_register_access(sensor):
        try:
            snap["squal"] = read_register(sensor, 0x07)
            shutter_l = read_register(sensor, 0x0B)
            shutter_h = read_register(sensor, 0x0C)
            snap["shutter"] = (shutter_h << 8) | shutter_l
        except Exception as exc:  # pragma: no cover
            snap["burst_extra_error"] = repr(exc)
    return snap


def frame_capture_snapshot(sensor: PAA5100, max_bytes: int = 1225) -> dict[str, Any]:
    fn = getattr(sensor, "frame_capture", None)
    if not callable(fn):
        return {"ok": False, "error": "frame_capture not available"}
    try:
        raw = fn()
        if isinstance(raw, (bytes, bytearray)):
            data = list(raw[:max_bytes])
        elif isinstance(raw, list):
            data = [int(v) for v in raw[:max_bytes]]
        else:
            data = []
        return {
            "ok": True,
            "bytes": len(data),
            "mean": (sum(data) / len(data)) if data else 0.0,
            "min": min(data) if data else 0,
            "max": max(data) if data else 0,
        }
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": repr(exc)}


def percent_to_led_level(percent: float | int | None) -> int:
    if percent is None:
        return _LED_LEVEL_MAX
    pct = max(0.0, min(100.0, float(percent)))
    return int(round(_LED_LEVEL_MIN + (_LED_LEVEL_MAX - _LED_LEVEL_MIN) * (pct / 100.0)))


def set_led(sensor: PAA5100, on: bool, percent: float | int | None = None) -> tuple[bool, str]:
    setter, source = led_setter(sensor)
    if setter is None:
        return False, source
    effective = percent_to_led_level(percent)
    setter(on, effective)
    return True, source


def led_blink(
    sensor: PAA5100,
    *,
    blinks: int = 2,
    period_s: float = 0.35,
    percent: float | int | None = None,
) -> tuple[bool, str]:
    ok, source = True, "unknown"
    for _ in range(max(1, blinks)):
        ok, source = set_led(sensor, True, percent)
        if not ok:
            return ok, source
        time.sleep(max(0.0, period_s))
        ok, source = set_led(sensor, False, percent)
        if not ok:
            return ok, source
        time.sleep(max(0.0, period_s))
    return ok, source


def led_breathe(
    sensor: PAA5100,
    *,
    up_seconds: float = 1.0,
    down_seconds: float = 1.0,
    steps: int = 20,
) -> tuple[bool, str]:
    source = "unknown"
    n = max(2, steps)
    up_dt = max(0.0, up_seconds) / (n - 1)
    down_dt = max(0.0, down_seconds) / (n - 1)
    for i in range(n):
        pct = (i * 100.0) / (n - 1)
        ok, source = set_led(sensor, True, pct)
        if not ok:
            return ok, source
        time.sleep(up_dt)
    for i in range(n):
        pct = 100.0 - (i * 100.0) / (n - 1)
        ok, source = set_led(sensor, True, pct)
        if not ok:
            return ok, source
        time.sleep(down_dt)
    return set_led(sensor, False, 0)
