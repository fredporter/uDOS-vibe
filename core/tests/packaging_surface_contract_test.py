"""Release packaging surface contracts that should stay stable."""

from __future__ import annotations

from pathlib import Path

from wizard.services.sonic_build_service import SonicBuildService


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_packaging_scripts_and_validators_exist() -> None:
    required_files = [
        REPO_ROOT / "distribution" / "alpine-core" / "build-sonic-stick.sh",
        REPO_ROOT / "core" / "tools" / "release_version_cli.py",
        REPO_ROOT / "distribution" / "installer.sh",
        REPO_ROOT / "bin" / "install-udos-vibe.sh",
        REPO_ROOT / "tools" / "ci" / "validate_sonic_artifact_manifest.py",
    ]
    for required in required_files:
        assert required.exists(), f"Missing packaging surface: {required}"


def test_sonic_build_service_points_to_canonical_build_script() -> None:
    service = SonicBuildService(repo_root=REPO_ROOT)
    expected = REPO_ROOT / "distribution" / "alpine-core" / "build-sonic-stick.sh"
    assert service.build_script == expected
    assert expected.exists()


def test_packaging_surfaces_do_not_use_hardcoded_legacy_version_fallback() -> None:
    build_script = (REPO_ROOT / "distribution" / "alpine-core" / "build-sonic-stick.sh").read_text(encoding="utf-8")
    build_service = (REPO_ROOT / "wizard" / "services" / "sonic_build_service.py").read_text(encoding="utf-8")

    assert "v1.3.17" not in build_script
    assert "v1.3.17" not in build_service
