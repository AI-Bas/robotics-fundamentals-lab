"""Module: hmi_dashboard
Task-switchable HMI scaffold for local touchscreen and remote browser clients.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import yaml

from components.layout_sections import SECTION_RENDERERS

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "layout_profiles.yaml"


def load_layout_profiles(config_path: Path) -> dict[str, Any]:
    """Load layout profile configuration from YAML file.

    Args:
        config_path: Absolute path to layout profile YAML.

    Returns:
        Parsed profile dictionary with default and profiles keys.
    """
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config_data: dict[str, Any] = yaml.safe_load(config_file)
            return config_data
    except FileNotFoundError:
        # Missing config usually means path or deployment packaging issue.
        st.error(f"Layout config not found: {config_path}")
        return {"default_profile": "", "profiles": {}}
    except yaml.YAMLError as yaml_error:
        # Invalid YAML blocks profile rendering and should be corrected first.
        st.error(f"Invalid layout configuration: {yaml_error}")
        return {"default_profile": "", "profiles": {}}


def render_profile(profile_name: str, profile_data: dict[str, Any]) -> None:
    """Render selected profile sections in configured order.

    Args:
        profile_name: Active profile identifier.
        profile_data: Selected profile object containing title and sections.
    """
    st.title(f"HMI - {profile_data.get('page_title', profile_name)}")
    st.caption("Local HDMI touchscreen + remote browser mirror mode")

    for section_name in profile_data.get("sections", []):
        renderer = SECTION_RENDERERS.get(section_name)
        if renderer is None:
            # Unknown section usually means config drift vs component map.
            st.warning(f"Unknown section configured: {section_name}")
            continue
        renderer()
        st.divider()


def main() -> None:
    """Run the HMI dashboard application entrypoint."""
    st.set_page_config(page_title="Robotics HMI", layout="wide")

    layout_config = load_layout_profiles(CONFIG_PATH)
    profile_map: dict[str, dict[str, Any]] = layout_config.get("profiles", {})
    default_profile_name = layout_config.get("default_profile", "")

    if not profile_map:
        st.error("No layout profiles are configured.")
        return

    sidebar_options = list(profile_map.keys())
    if default_profile_name not in sidebar_options:
        default_profile_name = sidebar_options[0]

    selected_profile = st.sidebar.selectbox(
        "Task Layout",
        options=sidebar_options,
        index=sidebar_options.index(default_profile_name),
        help="Switch layout by task context.",
    )
    st.sidebar.markdown("### Access")
    st.sidebar.code("Local:  http://127.0.0.1:8501")
    st.sidebar.code("Remote: http://<pi-ip>:8501")

    render_profile(selected_profile, profile_map[selected_profile])


if __name__ == "__main__":
    main()
