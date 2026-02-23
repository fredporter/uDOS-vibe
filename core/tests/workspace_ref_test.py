from __future__ import annotations

from core.services.workspace_ref import parse_workspace_name, split_workspace_root


def test_split_workspace_root_supports_workspace_prefix_and_typo() -> None:
    roots = {"memory", "vault", "sandbox"}
    assert split_workspace_root("@workspace/vault/docs", valid_roots=roots) == ("vault", "docs")
    assert split_workspace_root("@worskspace/vault/docs", valid_roots=roots) == ("vault", "docs")


def test_parse_workspace_name_accepts_memory_and_workspace_forms() -> None:
    names = {"vault", "sandbox", "memory"}
    assert parse_workspace_name("@workspace/vault/foo.md", known_names=names) == ("vault", "foo.md")
    assert parse_workspace_name("memory/vault/foo.md", known_names=names) == ("vault", "foo.md")
