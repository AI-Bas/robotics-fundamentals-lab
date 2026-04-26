"""Module: hmi_dashboard
Unit tests for layout profile loading behavior.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from src.app import load_layout_profiles


def test_load_layout_profiles_returns_profiles_dict() -> None:
    """Validate profile config loader for minimal valid YAML input."""
    with TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "layout_profiles.yaml"
        config_path.write_text(
            "default_profile: configuration\nprofiles:\n  configuration:\n    page_title: Configuration\n    sections: []\n",
            encoding="utf-8",
        )

        profile_data = load_layout_profiles(config_path)
        assert profile_data["default_profile"] == "configuration"
        assert "configuration" in profile_data["profiles"]
