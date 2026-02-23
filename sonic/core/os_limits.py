"""OS detection and limitations for Sonic Screwdriver."""

import platform
from pathlib import Path
from typing import Dict


def detect_platform() -> str:
    """
    Detect OS using the same logic as Wizard SystemInfoService.

    Returns: "alpine", "ubuntu", "macos", "windows", or "unknown"
    """
    alpine_release = Path("/etc/alpine-release")
    if alpine_release.exists():
        return "alpine"

    try:
        import shutil

        if shutil.which("apk"):
            return "alpine"
    except Exception:
        pass

    os_release = Path("/etc/os-release")
    if os_release.exists():
        try:
            content = os_release.read_text()
            if "ID=alpine" in content or "ID='alpine'" in content:
                return "alpine"
            if "ID=ubuntu" in content or "ID='ubuntu'" in content:
                return "ubuntu"
        except Exception:
            pass

    system = platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Linux":
        return "ubuntu"
    if system == "Windows":
        return "windows"

    return "unknown"


def os_capabilities() -> Dict[str, bool]:
    os_name = detect_platform()
    return {
        "linux": os_name in {"ubuntu", "alpine"},
        "alpine": os_name == "alpine",
        "macos": os_name == "macos",
        "windows": os_name == "windows",
        "ubuntu": os_name == "ubuntu",
    }


def is_supported() -> bool:
    caps = os_capabilities()
    return caps.get("linux", False)


def support_message() -> str:
    if is_supported():
        return "OK Linux-based OS detected."
    return "WARN Sonic Screwdriver build requires Linux (Ubuntu/Debian/Alpine)."
