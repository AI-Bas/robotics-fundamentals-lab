"""Module: ros2_core
Print lightweight ROS2 environment and command availability status.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any


def run_command(command: list[str]) -> dict[str, Any]:
    """Execute a command and capture output safely.

    Args:
        command: Command tokens for subprocess execution.

    Returns:
        Command result dictionary with success and output fields.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=8)
        return {
            "ok": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as error:
        return {"ok": False, "return_code": None, "stdout": "", "stderr": str(error)}


def collect_status() -> dict[str, Any]:
    """Collect ROS2-related environment and CLI status.

    Returns:
        ROS2 status dictionary.
    """
    ros_distro = os.environ.get("ROS_DISTRO", "")
    ros_root = os.environ.get("ROS_ROOT", "")
    ros_cmd_available = shutil.which("ros2") is not None

    return {
        "ros_env": {"ROS_DISTRO": ros_distro, "ROS_ROOT": ros_root},
        "ros2_cli_available": ros_cmd_available,
        "ros2_cli_help": run_command(["ros2", "--help"]) if ros_cmd_available else None,
        "ros2_doctor": run_command(["ros2", "doctor", "--report"]) if ros_cmd_available else None,
    }


def main() -> None:
    """Run ROS2 status collector entrypoint."""
    print(json.dumps(collect_status(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
