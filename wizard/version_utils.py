"""Wizard server version utility.

Single source of truth for the wizard server version string.
Imported by ``wizard/server.py`` (module constant) and by route modules
such as ``dashboard_summary_routes`` that need the version without
importing from ``server.py`` (which would be circular).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_VERSION_PATH = Path(__file__).parent / "version.json"


def get_wizard_server_version() -> str:
    """Return semantic wizard server version from wizard/version.json."""
    try:
        data = json.loads(_VERSION_PATH.read_text(encoding="utf-8"))
        version = data.get("version")
        if isinstance(version, dict):
            major = int(version.get("major", 1))
            minor = int(version.get("minor", 0))
            patch = int(version.get("patch", 0))
            return f"{major}.{minor}.{patch}"
        display = str(data.get("display", "")).strip()
        if display.startswith("v"):
            display = display[1:]
        if re.match(r"^\d+\.\d+\.\d+$", display):
            return display
    except Exception:
        pass
    return "1.0.0"
