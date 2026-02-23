from __future__ import annotations

from pathlib import Path

from core.services.editor_utils import resolve_workspace_path


def test_resolve_workspace_path_accepts_workspace_aliases(monkeypatch, tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    memory_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("core.services.editor_utils.get_memory_root", lambda: memory_root)

    resolved = resolve_workspace_path("@workspace/vault/notes")
    assert resolved == (memory_root / "vault" / "notes.md").resolve()
