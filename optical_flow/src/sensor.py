#!/usr/bin/env python3
"""
Shared sensor/config helpers for optical-flow scripts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Optional

import yaml
from pmw3901 import PAA5100


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
