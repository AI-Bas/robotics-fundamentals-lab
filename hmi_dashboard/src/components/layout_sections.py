"""Module: hmi_dashboard
Reusable section renderers for task-specific HMI layouts.
"""

from __future__ import annotations

from typing import Callable

import streamlit as st


def render_system_overview() -> None:
    """Render high-level system summary and platform status."""
    st.subheader("System Overview")
    st.info("Show platform profile, active modules, and last bootstrap timestamp.")


def render_network_settings() -> None:
    """Render controls for hostname, Wi-Fi/Ethernet, and remote access."""
    st.subheader("Network Settings")
    st.text_input("Hostname", value="robotics-node")
    st.text_input("HMI Bind Address", value="0.0.0.0")
    st.number_input("HMI Port", min_value=1, max_value=65535, value=8501)


def render_module_toggles() -> None:
    """Render module enable/disable controls for staged startup."""
    st.subheader("Module Toggles")
    st.checkbox("Enable optical_flow", value=True)
    st.checkbox("Enable power_monitor", value=True)
    st.checkbox("Enable modular_io", value=True)
    st.checkbox("Enable vision_camera", value=True)


def render_save_profile() -> None:
    """Render profile save actions for reusable setup states."""
    st.subheader("Save Profile")
    st.text_input("Profile Name", value="default_profile")
    st.button("Save Profile")


def render_sensor_selection() -> None:
    """Render sensor/source selection for calibration workflows."""
    st.subheader("Sensor Selection")
    st.multiselect(
        "Active calibration modules",
        ["optical_flow", "power_monitor", "vision_camera", "modular_io"],
        default=["optical_flow"],
    )


def render_calibration_steps() -> None:
    """Render guided calibration steps and step progression controls."""
    st.subheader("Calibration Steps")
    st.selectbox(
        "Current step",
        ["preflight", "capture", "fit/solve", "validate", "export"],
        index=0,
    )
    st.button("Mark Step Complete")


def render_live_graphs() -> None:
    """Render placeholder for interactive calibration graphs."""
    st.subheader("Live Graphs")
    st.line_chart({"metric_a": [0, 1, 2, 3], "metric_b": [1, 1, 2, 4]})


def render_results_export() -> None:
    """Render export actions for calibration and diagnostics outputs."""
    st.subheader("Results Export")
    st.button("Export JSON Summary")
    st.button("Export CSV Snapshot")


def render_mode_selection() -> None:
    """Render run-mode selection controls for operation profiles."""
    st.subheader("Mode Selection")
    st.radio("Run Mode", ["idle", "diagnostics", "calibration", "active_control"], index=0)


def render_runtime_controls() -> None:
    """Render runtime command controls for start/stop/restart actions."""
    st.subheader("Runtime Controls")
    st.button("Start")
    st.button("Stop")
    st.button("Restart")


def render_health_status() -> None:
    """Render health summary for module and interface status indicators."""
    st.subheader("Health Status")
    st.success("All critical checks are currently healthy (placeholder).")


def render_event_log() -> None:
    """Render a recent event log view for runtime troubleshooting."""
    st.subheader("Event Log")
    st.code("INFO: placeholder event stream", language="text")


def render_io_device_scan() -> None:
    """Render I/O scan tools for serial/I2C/SPI device discovery."""
    st.subheader("I/O Device Scan")
    st.button("Scan I2C")
    st.button("Scan SPI")
    st.button("Scan Serial")


def render_serial_console() -> None:
    """Render a serial console placeholder for quick protocol tests."""
    st.subheader("Serial Console")
    st.text_input("Serial Device", value="/dev/ttyACM0")
    st.text_area("Console Output", value="No data yet.", height=120)


def render_pin_map() -> None:
    """Render board pin mapping summary for GPIO troubleshooting."""
    st.subheader("Pin Map")
    st.table(
        {
            "Interface": ["I2C", "SPI", "UART"],
            "Pins": ["SDA/SCL", "MOSI/MISO/SCLK/CS", "TX/RX"],
        }
    )


def render_io_actions() -> None:
    """Render quick I/O actions for smoke and bench validation."""
    st.subheader("I/O Actions")
    st.button("Toggle Test Pin")
    st.button("Send Heartbeat Packet")


SECTION_RENDERERS: dict[str, Callable[[], None]] = {
    "system_overview": render_system_overview,
    "network_settings": render_network_settings,
    "module_toggles": render_module_toggles,
    "save_profile": render_save_profile,
    "sensor_selection": render_sensor_selection,
    "calibration_steps": render_calibration_steps,
    "live_graphs": render_live_graphs,
    "results_export": render_results_export,
    "mode_selection": render_mode_selection,
    "runtime_controls": render_runtime_controls,
    "health_status": render_health_status,
    "event_log": render_event_log,
    "io_device_scan": render_io_device_scan,
    "serial_console": render_serial_console,
    "pin_map": render_pin_map,
    "io_actions": render_io_actions,
}
