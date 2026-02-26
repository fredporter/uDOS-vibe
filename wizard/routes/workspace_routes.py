"""Workspace Routes
===============

Provide browser-safe access to /memory for Wizard UI.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.services.spatial_filesystem import WORKSPACE_CONFIG
from core.services.story_service import parse_story_document
from core.services.unified_config_loader import get_config
from core.services.workspace_ref import split_workspace_root
from wizard.services.path_utils import get_memory_dir, get_repo_root, get_vault_dir


class WriteRequest(BaseModel):
    path: str
    content: str


class MkdirRequest(BaseModel):
    path: str


def _resolve_workspace_root() -> dict[str, Path]:
    """Build a map of workspace-key → resolved absolute Path.

    All ``memory/``-prefixed workspace paths are resolved relative to
    ``get_memory_dir()`` so that a custom ``file_locations.memory_root``
    in wizard.json is honoured consistently across every workspace.
    Non-memory paths (``knowledge``, ``dev``) fall back to ``get_repo_root()``.
    """
    memory_root = get_memory_dir().resolve()
    repo_root = get_repo_root().resolve()

    root_map: dict[str, Path] = {"memory": memory_root}

    for ws_type, config in WORKSPACE_CONFIG.items():
        rel_path = config.get("path")
        if not isinstance(rel_path, str):
            continue
        if rel_path.startswith("memory/"):
            # Use the resolved memory root so customised paths stay coherent.
            tail = rel_path[len("memory/"):]
            root_map[ws_type.value] = (memory_root / tail).resolve()
        else:
            root_map[ws_type.value] = (repo_root / rel_path).resolve()

    # Canonical vault alias always mirrors the resolved vault workspace.
    root_map["vault"] = get_vault_dir().resolve()
    return root_map


def _split_root(path: str) -> tuple[str, str]:
    root_map = _resolve_workspace_root()
    return split_workspace_root(
        path, valid_roots=root_map.keys(), default_root="memory"
    )


def _resolve_path(relative_path: str) -> Path:
    root_map = _resolve_workspace_root()
    root_key, rel = _split_root(relative_path)
    root_dir = root_map[root_key]
    candidate = (root_dir / rel).resolve()
    try:
        candidate.relative_to(root_dir)
    except ValueError:
        raise ValueError(f"Path must be within {root_key}/")
    return candidate


def create_workspace_routes(auth_guard=None, prefix="/api/workspace") -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix=prefix, tags=["workspace"], dependencies=dependencies)

    @router.get("/roots")
    async def get_roots():
        """Return all workspace roots with resolved absolute paths and metadata.

        Each entry exposes:
        - ``ref``        — canonical ``@key`` reference for the GUI
        - ``abs_path``   — resolved filesystem path
        - ``exists``     — whether the directory currently exists on disk
        - ``description``— human-readable label from WORKSPACE_CONFIG
        - ``aliases``    — additional ``@workspace/<key>`` form
        """
        root_map = _resolve_workspace_root()
        ws_descriptions: dict[str, str] = {
            ws_type.value: cfg.get("description", "")
            for ws_type, cfg in WORKSPACE_CONFIG.items()
        }

        roots: dict[str, dict] = {}
        for key in sorted(root_map):
            abs_path = root_map[key]
            roots[f"@{key}"] = {
                "ref": f"@{key}",
                "key": key,
                "abs_path": str(abs_path),
                "exists": abs_path.exists(),
                "description": ws_descriptions.get(key, ""),
                "aliases": [f"@workspace/{key}"],
            }

        return {"success": True, "roots": roots}

    @router.get("/resolve")
    async def resolve_workspace_path(path: str = ""):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        root_key, rel = _split_root(path)
        normalized_path = root_key if not rel else f"{root_key}/{rel}"
        return {
            "success": True,
            "input": path,
            "normalized": normalized_path,
            "absolute_path": str(resolved),
        }

    @router.get("/list")
    async def list_entries(path: str = ""):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        if not resolved.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if not resolved.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        root_key, rel = _split_root(path)
        root_dir = _resolve_workspace_root()[root_key]

        entries = []
        for entry in sorted(
            resolved.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
        ):
            rel_path = entry.relative_to(root_dir).as_posix()
            if rel_path:
                rel_path = f"{root_key}/{rel_path}"
            else:
                rel_path = root_key
            entries.append({
                "name": entry.name,
                "path": rel_path,
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size,
                "modified": entry.stat().st_mtime,
            })

        normalized_path = root_key if not rel else f"{root_key}/{rel}"
        return {"success": True, "path": normalized_path, "entries": entries}

    @router.get("/read")
    async def read_file(path: str):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        if not resolved.exists() or not resolved.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        try:
            return {"success": True, "content": resolved.read_text()}
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File is not valid text")

    @router.get("/story/parse")
    async def parse_story(path: str):
        try:
            resolved = _resolve_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if not resolved.exists() or not resolved.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        try:
            story = parse_story_document(
                resolved.read_text(), required_frontmatter_keys=["title", "type"]
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return {"success": True, "path": path, "story": story}

    @router.post("/write")
    async def write_file(payload: WriteRequest):
        try:
            resolved = _resolve_path(payload.path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(payload.content)
        return {"success": True, "path": payload.path}

    @router.post("/mkdir")
    async def mkdir(payload: MkdirRequest):
        try:
            resolved = _resolve_path(payload.path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        resolved.mkdir(parents=True, exist_ok=True)
        return {"success": True, "path": payload.path}

    return router
