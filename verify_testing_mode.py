#!/usr/bin/env python3
"""Quick verification of alert-only mode."""

from __future__ import annotations

from pathlib import Path

handlers = [
    "binder_handler.py",
    "run_handler.py",
    "wizard_handler.py",
    "seed_handler.py",
    "file_editor_handler.py",
    "repair_handler.py",
    "maintenance_handler.py",
    "destroy_handler.py",
    "empire_handler.py",
]

print("ALERT MARKER CHECK:")
for h in handlers:
    p = Path(f"core/commands/{h}")
    if p.exists():
        has_alert = "[TESTING ALERT]" in p.read_text()
        print(f"{'✓' if has_alert else '✗'} {h}")

print("\nLOCK FLAGS:")
action = Path("action.yml")
has_locked = "--locked" in action.read_text()
print(
    f"{'✗' if has_locked else '✓'} action.yml: --locked {'PRESENT' if has_locked else 'REMOVED'}"
)

print("\nPERMISSION SYSTEM:")
try:
    from core.services.user_service import Permission

    perms = list(Permission)
    print(f"✓ Permission enum: {len(perms)} permissions")
except Exception as e:
    print(f"✗ Permission system: {e}")

try:
    from core.services.mode_policy import RuntimeMode

    modes = list(RuntimeMode)
    print(f"✓ RuntimeMode: {len(modes)} modes")
except Exception as e:
    print(f"✗ Mode policy: {e}")
