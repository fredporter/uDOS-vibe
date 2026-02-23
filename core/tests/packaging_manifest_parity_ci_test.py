"""Manifest parity checks for packaging docs/scripts/workflow CI surfaces."""

from __future__ import annotations

from pathlib import Path
import re

from core.services.packaging_dependency_service import (
    dependency_profile,
    render_apkbuild_dependency_snippet,
    render_dependency_docs_table,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _extract_block_values(apkbuild_text: str, key: str) -> list[str]:
    pattern = rf'{key}="\n(?P<body>.*?)\n"'
    match = re.search(pattern, apkbuild_text, re.DOTALL)
    if not match:
        raise AssertionError(f"Unable to parse {key} block from APKBUILD")
    return [line.strip() for line in match.group("body").splitlines() if line.strip()]


def test_apkbuild_dependency_blocks_match_manifest_profile() -> None:
    apkbuild_path = REPO_ROOT / "distribution" / "apkbuild" / "udos-ui" / "APKBUILD"
    text = apkbuild_path.read_text(encoding="utf-8")
    deps = dependency_profile(REPO_ROOT, "linux", "udos-ui-thin-gui")
    assert _extract_block_values(text, "depends") == deps["runtime_packages"]
    assert _extract_block_values(text, "makedepends") == deps["build_packages"]


def test_generated_apkbuild_dependency_snippet_matches_manifest() -> None:
    generated_path = REPO_ROOT / "distribution" / "apkbuild" / "udos-ui" / "APKBUILD.depends.generated"
    expected = render_apkbuild_dependency_snippet(REPO_ROOT, profile="udos-ui-thin-gui")
    assert generated_path.read_text(encoding="utf-8") == expected


def test_generated_packaging_dependency_docs_match_manifest() -> None:
    docs_path = REPO_ROOT / "docs" / "features" / "packaging-dependency-map.md"
    expected = render_dependency_docs_table(REPO_ROOT)
    assert docs_path.read_text(encoding="utf-8") == expected


def test_ci_workflow_runs_packaging_dependency_parity_check() -> None:
    workflow_path = REPO_ROOT / ".github" / "workflows" / "ci-profiles.yml"
    text = workflow_path.read_text(encoding="utf-8")
    assert "tools/ci/check_packaging_dependency_artifacts_sync.py" in text
