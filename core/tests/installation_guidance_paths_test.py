"""Documentation contracts for Core/Wizard/Sonic install and update guidance."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_installation_guide_covers_core_and_wizard_profiles() -> None:
    installation_doc = (REPO_ROOT / "docs" / "INSTALLATION.md").read_text(encoding="utf-8")
    assert "./bin/install-udos-vibe.sh --core" in installation_doc
    assert "./bin/install-udos-vibe.sh --wizard" in installation_doc
    assert "uv sync --extra udos" in installation_doc
    assert "uv sync --extra udos-wizard" in installation_doc


def test_sonic_release_install_guide_exists_and_contains_build_flow() -> None:
    sonic_doc = (REPO_ROOT / "docs" / "howto" / "SONIC-STANDALONE-RELEASE-AND-INSTALL.md").read_text(
        encoding="utf-8"
    )
    assert "distribution/alpine-core/build-sonic-stick.sh" in sonic_doc
    assert "release-readiness" in sonic_doc
