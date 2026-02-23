#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path


THEMES = ["nes", "c64", "medium", "teletext"]


def main() -> None:
    themes_root = Path(__file__).resolve().parents[1]
    template_root = themes_root / "prose"
    if not template_root.exists():
        raise SystemExit("Missing themes/prose template.")

    for name in THEMES:
        dest = themes_root / name
        if dest.exists():
            print(f"skip: {name} already exists")
            continue
        shutil.copytree(template_root, dest)
        theme_json = dest / "theme.json"
        if theme_json.exists():
            data = json.loads(theme_json.read_text())
            data["name"] = name
            data["description"] = f"Stub theme derived from prose ({name})."
            theme_json.write_text(json.dumps(data, indent=2) + "\n")
        print(f"created: {dest}")


if __name__ == "__main__":
    main()
