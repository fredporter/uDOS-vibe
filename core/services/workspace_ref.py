"""Shared workspace reference parsing helpers."""

from __future__ import annotations

from typing import Iterable

_WORKSPACE_TOKEN = "workspace/"
_WORKSPACE_TYPO_TOKEN = "worskspace/"
_MEMORY_TOKEN = "memory/"


def normalize_workspace_ref(path: str) -> str:
    raw = (path or "").strip().replace("\\", "/")
    if raw.startswith("@"):
        raw = raw[1:]
    raw = raw.lstrip("/")
    if raw.startswith(_WORKSPACE_TYPO_TOKEN):
        return f"{_WORKSPACE_TOKEN}{raw[len(_WORKSPACE_TYPO_TOKEN):]}"
    return raw


def split_workspace_root(
    path: str,
    *,
    valid_roots: Iterable[str],
    default_root: str = "memory",
) -> tuple[str, str]:
    roots = set(valid_roots)
    raw = normalize_workspace_ref(path)
    if not raw:
        return default_root, ""

    if raw.startswith(_WORKSPACE_TOKEN):
        parts = raw.split("/", 2)
        if len(parts) >= 2:
            root = parts[1]
            rel = parts[2] if len(parts) > 2 else ""
            if root in roots:
                return root, rel

    parts = raw.split("/", 1)
    root = parts[0]
    if root in roots:
        rel = parts[1] if len(parts) > 1 else ""
        return root, rel

    return default_root, raw


def parse_workspace_name(
    path: str,
    *,
    known_names: Iterable[str],
) -> tuple[str, str]:
    names = set(known_names)
    raw = normalize_workspace_ref(path)
    if not raw:
        raise ValueError("Workspace reference is empty")

    parts = raw.split("/", 2)
    match parts:
        case ["workspace", name]:
            rel = ""
        case ["workspace", name, rel]:
            pass
        case ["memory", name]:
            rel = ""
        case ["memory", name, rel]:
            pass
        case [name]:
            rel = ""
        case [name, rel]:
            pass
        case _:
            raise ValueError(f"Invalid workspace reference: {path}")

    if name not in names:
        raise ValueError(f"Unknown workspace: {name}")
    return name, rel
