"""Dispatch-loop coverage for installer argument combinations."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "distribution" / "installer.sh"


def _write_exec(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def _prepare_fake_tools(tmp_path: Path) -> Path:
    tools_dir = tmp_path / "fake-tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    _write_exec(tools_dir / "tce-load", "#!/bin/sh\nexit 0\n")
    _write_exec(tools_dir / "md5sum", "#!/bin/sh\nexit 0\n")
    _write_exec(tools_dir / "unsquashfs", "#!/bin/sh\nexit 0\n")
    return tools_dir


def _prepare_pkg_dir(tmp_path: Path) -> Path:
    pkg_dir = tmp_path / "pkgs"
    pkg_dir.mkdir(parents=True)
    for name in ("udos-core.tcz", "udos-api.tcz", "udos-wizard.tcz"):
        (pkg_dir / name).write_bytes(b"pkg")
    return pkg_dir


def _run_installer(args: list[str], *, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    tools_dir = _prepare_fake_tools(tmp_path)
    env = os.environ.copy()
    env["PATH"] = f"{tools_dir}:{env.get('PATH', '')}"
    env["TMPDIR"] = str(tmp_path / "tmp")
    return subprocess.run(
        ["sh", str(INSTALLER), *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_installer_dispatch_loop_arg_combinations_succeed_in_dry_run(tmp_path: Path) -> None:
    pkg_dir = _prepare_pkg_dir(tmp_path)
    combos = [
        ["--dry-run", "--yes", "--packages=udos-core.tcz", f"--from={pkg_dir}"],
        ["--dry-run", "--yes", "--packages", "udos-core.tcz,udos-api.tcz", "--from", str(pkg_dir)],
        ["--dry-run", "--yes", "--tier=core", "--from", str(pkg_dir)],
        ["--dry-run", "-y", "-p", "udos-core.tcz", "-f", str(pkg_dir)],
    ]
    for combo in combos:
        proc = _run_installer(combo, tmp_path=tmp_path)
        assert proc.returncode == 0, f"combo failed: {combo}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        assert "Dry run mode - no changes will be made" in proc.stdout
        assert "Installation complete" in proc.stdout


def test_installer_dispatch_loop_rejects_unknown_option(tmp_path: Path) -> None:
    proc = _run_installer(["--dry-run", "--bogus"], tmp_path=tmp_path)
    assert proc.returncode != 0
    assert "Unknown option: --bogus" in proc.stderr
