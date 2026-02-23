from __future__ import annotations

from pathlib import Path

from core.services.packaging_dependency_service import (
    dependency_profile,
    render_apkbuild_dependency_snippet,
    render_dependency_docs_table,
)


def test_dependency_profile_returns_linux_profile_defaults(tmp_path: Path) -> None:
    deps = dependency_profile(tmp_path, "linux", "udos-ui-thin-gui")
    assert "cage" in deps["runtime_packages"]
    assert "cargo" in deps["build_packages"]


def test_render_apkbuild_dependency_snippet_contains_expected_blocks(tmp_path: Path) -> None:
    snippet = render_apkbuild_dependency_snippet(tmp_path, profile="udos-ui-thin-gui")
    assert 'depends="' in snippet
    assert "cage" in snippet
    assert 'makedepends="' in snippet
    assert "cargo" in snippet


def test_render_dependency_docs_table_contains_platform_rows(tmp_path: Path) -> None:
    docs = render_dependency_docs_table(tmp_path)
    assert "| linux | `udos-ui-thin-gui` |" in docs
    assert "| windows | `windows10-entertainment` |" in docs
