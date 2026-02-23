#!/usr/bin/env python3
"""Check packaging dependency artifacts are synchronized to manifest profiles."""

from __future__ import annotations

from pathlib import Path
import re

from core.services.packaging_dependency_service import (
    dependency_profile,
    render_apkbuild_dependency_snippet,
    render_dependency_docs_table,
)


def _extract_block_values(apkbuild_text: str, key: str) -> list[str]:
    pattern = rf'{key}="\n(?P<body>.*?)\n"'
    match = re.search(pattern, apkbuild_text, re.DOTALL)
    if not match:
        raise ValueError(f"Unable to parse {key} block from APKBUILD")
    return [line.strip() for line in match.group("body").splitlines() if line.strip()]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    apkbuild_path = repo_root / "distribution" / "apkbuild" / "udos-ui" / "APKBUILD"
    snippet_path = repo_root / "distribution" / "apkbuild" / "udos-ui" / "APKBUILD.depends.generated"
    docs_path = repo_root / "docs" / "features" / "packaging-dependency-map.md"

    expected = dependency_profile(repo_root, "linux", "udos-ui-thin-gui")
    apkbuild_text = apkbuild_path.read_text(encoding="utf-8")
    apk_runtime = _extract_block_values(apkbuild_text, "depends")
    apk_build = _extract_block_values(apkbuild_text, "makedepends")

    if apk_runtime != expected["runtime_packages"]:
        print("[packaging-deps] FAIL: APKBUILD depends block diverges from manifest profile")
        return 1
    if apk_build != expected["build_packages"]:
        print("[packaging-deps] FAIL: APKBUILD makedepends block diverges from manifest profile")
        return 1

    expected_snippet = render_apkbuild_dependency_snippet(repo_root, profile="udos-ui-thin-gui")
    expected_docs = render_dependency_docs_table(repo_root)
    current_snippet = snippet_path.read_text(encoding="utf-8") if snippet_path.exists() else ""
    current_docs = docs_path.read_text(encoding="utf-8") if docs_path.exists() else ""

    if current_snippet != expected_snippet:
        print("[packaging-deps] FAIL: APKBUILD.depends.generated is stale; run tools/generate_packaging_dependency_artifacts.py")
        return 1
    if current_docs != expected_docs:
        print("[packaging-deps] FAIL: packaging dependency docs table is stale; run tools/generate_packaging_dependency_artifacts.py")
        return 1

    print("[packaging-deps] PASS: dependency artifacts synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
