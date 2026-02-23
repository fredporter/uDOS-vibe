"""CLI for canonical repo release version resolution."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.services.release_version_service import get_release_display_version


def main() -> int:
    parser = argparse.ArgumentParser(description="Print canonical release version from repo version.json")
    parser.add_argument("--repo-root", default=".", help="Repository root path (default: current directory)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    print(get_release_display_version(repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
