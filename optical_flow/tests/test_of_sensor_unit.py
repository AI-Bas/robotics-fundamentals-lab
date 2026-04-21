from __future__ import annotations

import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import of_sensor


class DummySensor:
    def __init__(self) -> None:
        self.writes: list[tuple[int, int]] = []

    def get_id(self) -> int:
        return 0x49

    def get_motion(self) -> tuple[int, int]:
        return (3, -4)

    def _read(self, register: int) -> int:
        values = {0x07: 55, 0x0B: 0x34, 0x0C: 0x12}
        return values.get(register, 0)

    def _write(self, register: int, value: int) -> None:
        self.writes.append((register, value))


def test_percent_to_led_level_bounds() -> None:
    assert of_sensor.percent_to_led_level(None) == 0xD5
    assert of_sensor.percent_to_led_level(0) == 0x00
    assert of_sensor.percent_to_led_level(100) == 0xD5
    assert of_sensor.percent_to_led_level(-10) == 0x00
    assert of_sensor.percent_to_led_level(150) == 0xD5


def test_sensor_probe_reports_capabilities() -> None:
    probe = of_sensor.sensor_probe(DummySensor())
    assert probe["has_get_motion"] == "True"
    assert probe["has_private_read"] == "True"
    assert probe["sensor_id"] == str(0x49)


def test_motion_burst_snapshot_includes_register_details() -> None:
    snap = of_sensor.motion_burst_snapshot(DummySensor())
    assert snap["ok"] is True
    assert snap["dx"] == 3
    assert snap["dy"] == -4
    assert snap["squal"] == 55
    assert snap["shutter"] == 0x1234
