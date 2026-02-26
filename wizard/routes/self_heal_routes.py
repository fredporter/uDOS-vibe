"""Self-Heal Routes
================

Expose diagnostics and guided repair actions for Wizard setup.
"""

from __future__ import annotations

import asyncio
import functools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.services.unified_config_loader import get_config
from wizard.providers.nounproject_client import (
    AuthenticationError,
    NounProjectClient,
    NounProjectConfig,
    ProviderError,
    QuotaExceededError,
    RateLimitError,
)
from wizard.services.logging_api import get_logger as _get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.port_manager import OperationStatus, get_port_manager

_log = _get_logger("wizard", category="self-heal")

DEFAULT_CATEGORIES = {
    "ui": ["check", "close", "menu", "plus", "minus"],
    "nav": ["arrow left", "arrow right", "arrow up", "arrow down"],
    "system": ["settings", "warning", "info", "alert"],
    "media": ["play", "pause", "stop", "record"],
}


class SeedRequest(BaseModel):
    categories: dict[str, list[str]] | None = None
    per_term: int = 2


class PullRequest(BaseModel):
    model: str


class RecoverRequest(BaseModel):
    strategy: str = "quick_recover"
    dry_run: bool = True


def _nounproject_client() -> NounProjectClient:
    return NounProjectClient(NounProjectConfig(name="nounproject"))


def _diagrams_root() -> Path:
    return (
        get_repo_root()
        / "core"
        / "framework"
        / "seed"
        / "bank"
        / "graphics"
        / "diagrams"
        / "svg"
        / "icons"
        / "nounproject"
    )


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "icon"


def _ollama_get(path: str) -> dict | None:
    import urllib.request

    url = f"http://127.0.0.1:11434{path}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _ollama_models() -> list[str]:
    data = _ollama_get("/api/tags")
    if not data:
        return []
    models = []
    for entry in data.get("models", []):
        name = entry.get("name", "")
        if name:
            models.append(name)
    return models


def _normalize_model_name(name: str) -> str:
    from wizard.services.ollama_tier_service import normalize_model_name
    return normalize_model_name(name)


def _required_ollama_models() -> list[str]:
    from wizard.services.ollama_tier_service import get_required_models

    recommended = get_config("VIBE_OLLAMA_RECOMMENDED_MODELS", "").strip()
    tier = get_config("VIBE_INSTALL_TIER", "").strip().lower()
    return get_required_models(tier=tier or None, override=recommended or None)


def _configured_ollama_default_model() -> str:
    return (
        get_config("OLLAMA_DEFAULT_MODEL", "").strip()
        or get_config("VIBE_ASK_MODEL", "").strip()
        or "devstral-small-2"
    )


def _ensure_ollama_running() -> dict[str, str | None]:
    """Ensure Ollama daemon is running; attempt to start if needed."""
    if _ollama_get("/api/version"):
        return {"started": False, "method": "already-running"}

    started = False
    method = None
    error = None

    try:
        # macOS app launch if available
        if os.path.exists("/Applications/Ollama.app"):
            subprocess.Popen(["open", "-a", "Ollama"])
            started = True
            method = "open-app"
        else:
            # Fallback to CLI daemon
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            started = True
            method = "ollama-serve"
    except Exception as exc:
        error = str(exc)

    # Wait briefly for daemon
    if started:
        for _ in range(10):
            if _ollama_get("/api/version"):
                return {"started": True, "method": method}
            time.sleep(0.5)

    return {"started": started, "method": method, "error": error}


def _handle_provider_error(exc: Exception):
    if isinstance(exc, AuthenticationError):
        raise HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, RateLimitError):
        raise HTTPException(status_code=429, detail=str(exc))
    if isinstance(exc, QuotaExceededError):
        raise HTTPException(status_code=402, detail=str(exc))
    if isinstance(exc, ProviderError):
        raise HTTPException(status_code=400, detail=str(exc))
    raise HTTPException(status_code=500, detail=str(exc))


def create_self_heal_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/self-heal", tags=["self-heal"], dependencies=dependencies
    )

    strategies = {
        "quick_recover": {
            "description": "Validate critical dependencies and start Ollama if needed.",
            "steps": ["check_ollama", "check_port_conflicts"],
        },
        "ollama_recover": {
            "description": "Recover Ollama daemon and validate required model availability.",
            "steps": ["check_ollama", "check_models"],
        },
        "ports_recover": {
            "description": "Detect service port conflicts and return remediation plan.",
            "steps": ["check_port_conflicts"],
        },
    }

    @router.get("/strategies")
    async def list_recovery_strategies():
        return {"success": True, "count": len(strategies), "strategies": strategies}

    @router.post("/recover")
    async def recover(payload: RecoverRequest):
        strategy = strategies.get(payload.strategy)
        if not strategy:
            raise HTTPException(
                status_code=404, detail=f"Unknown strategy: {payload.strategy}"
            )

        pm = get_port_manager()
        actions = []
        summary = {"dry_run": payload.dry_run, "strategy": payload.strategy}

        if "check_ollama" in strategy["steps"]:
            if payload.dry_run:
                actions.append({"step": "check_ollama", "planned": True})
            else:
                ollama_result = _ensure_ollama_running()
                actions.append({"step": "check_ollama", "result": ollama_result})

        if "check_models" in strategy["steps"]:
            models = _ollama_models()
            normalized = {_normalize_model_name(m) for m in models}
            required = _required_ollama_models()
            configured_default = _normalize_model_name(
                _configured_ollama_default_model()
            )
            if configured_default and configured_default not in required:
                required.append(configured_default)
            missing = [m for m in required if m not in normalized]
            actions.append({
                "step": "check_models",
                "required": required,
                "available": sorted(list(normalized)),
                "missing": missing,
            })

        if "check_port_conflicts" in strategy["steps"]:
            pm.check_all_services()
            conflicts = []
            for name, service in pm.services.items():
                if not service.port:
                    continue
                occupant = pm.get_port_occupant(service.port)
                if occupant and occupant.get("process") != service.process_name:
                    conflicts.append({
                        "service": name,
                        "port": service.port,
                        "expected_process": service.process_name,
                        "actual_process": occupant.get("process"),
                        "pid": occupant.get("pid"),
                    })
            actions.append({"step": "check_port_conflicts", "conflicts": conflicts})
            summary["conflict_count"] = len(conflicts)

        return {"success": True, "summary": summary, "actions": actions}

    @router.get("/status")
    async def status():
        env_admin_token = get_config("WIZARD_ADMIN_TOKEN", "").strip()
        noun_key = get_config("NOUNPROJECT_API_KEY", "").strip()
        noun_secret = get_config("NOUNPROJECT_API_SECRET", "").strip()
        noun_configured = bool(noun_key and noun_secret)

        noun_auth_ok = None
        noun_error = None
        if noun_configured:
            try:
                client = _nounproject_client()
                await client.authenticate()
                noun_auth_ok = True
            except Exception as exc:
                noun_auth_ok = False
                noun_error = str(exc)

        pm = get_port_manager()
        ollama_port_open = pm.is_port_open(11434)
        ollama_version = _ollama_get("/api/version")
        ollama_running = bool(ollama_version)
        models = _ollama_models() if ollama_running else []
        normalized = {_normalize_model_name(m) for m in models}
        required = _required_ollama_models()
        configured_default = _normalize_model_name(_configured_ollama_default_model())
        if configured_default and configured_default not in required:
            required.append(configured_default)
        missing = [m for m in required if m not in normalized]
        vibe_cli = bool(shutil.which("vibe"))

        next_steps = []
        if not env_admin_token:
            next_steps.append(
                "Set WIZARD_ADMIN_TOKEN in the Wizard server environment."
            )
        if not ollama_running:
            next_steps.append("Run `ollama serve` or open the Ollama app.")
        if missing:
            pull_cmds = " && ".join(f"ollama pull {name}" for name in missing)
            next_steps.append(f"Run `{pull_cmds}`.")
        if not noun_configured:
            next_steps.append("Set NOUNPROJECT_API_KEY and NOUNPROJECT_API_SECRET.")
        if noun_auth_ok is False:
            next_steps.append("Verify Noun Project credentials; auth failed.")

        # Run core offline diagnostics (blocking I/O → threadpool, auto_repair=False
        # to avoid any stdin interaction in a server context).
        core_diagnostics: dict = {}
        try:
            from core.services.self_healer import collect_self_heal_summary

            loop = asyncio.get_event_loop()
            core_diagnostics = await loop.run_in_executor(
                None,
                functools.partial(
                    collect_self_heal_summary, component="wizard", auto_repair=False
                ),
            )
        except Exception as _exc:
            core_diagnostics = {"error": str(_exc)}

        return {
            "admin_token_present": bool(env_admin_token),
            "ollama": {
                "running": ollama_running,
                "port_open": ollama_port_open,
                "version": ollama_version,
                "models": models,
                "required_models": required,
                "configured_default_model": configured_default,
                "missing_default_model": configured_default in missing,
                "missing_models": missing,
            },
            "vibe_cli": {"installed": vibe_cli},
            "nounproject": {
                "configured": noun_configured,
                "auth_ok": noun_auth_ok,
                "error": noun_error,
            },
            "next_steps": next_steps,
            "core_diagnostics": core_diagnostics,
        }

    @router.post("/ollama/pull")
    async def pull_model(payload: PullRequest):
        """Pull Ollama model with progress streaming."""
        import asyncio

        from fastapi.responses import StreamingResponse

        try:

            async def generate_progress():
                pm = get_port_manager()

                # Register operation start
                op_id = pm.start_operation(
                    operation_type="pull_model",
                    description=f"Pulling Ollama model: {payload.model}",
                )

                try:
                    startup = _ensure_ollama_running()
                    # Use json.dumps for proper escaping
                    msg = json.dumps({
                        "progress": 0,
                        "status": "starting",
                        "message": f"Starting Ollama pull for {payload.model}...",
                    })
                    yield f"data: {msg}\n\n"

                    if not shutil.which("ollama"):
                        pm.complete_operation(op_id, error="ollama not installed")
                        msg = json.dumps({
                            "error": "ollama not installed",
                            "status": "failed",
                        })
                        yield f"data: {msg}\n\n"
                        return

                    proc = await asyncio.create_subprocess_exec(
                        "ollama",
                        "pull",
                        payload.model,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )

                    progress = 10
                    async for line in proc.stdout:
                        line_text = line.decode().strip()
                        if line_text:
                            progress = min(progress + 5, 90)
                            # Update operation with progress
                            pm.update_operation(
                                op_id,
                                progress=progress,
                                status=OperationStatus.IN_PROGRESS,
                            )
                            # Use json.dumps for proper escaping
                            msg = json.dumps({
                                "progress": progress,
                                "status": "pulling",
                                "message": line_text[:100],
                            })
                            yield f"data: {msg}\n\n"

                    await proc.wait()

                    if proc.returncode == 0:
                        pm.complete_operation(op_id)
                        msg = json.dumps({
                            "progress": 100,
                            "status": "complete",
                            "message": f"✅ Pulled {payload.model} successfully",
                        })
                        yield f"data: {msg}\n\n"
                    else:
                        stderr = await proc.stderr.read()
                        error_msg = stderr.decode().strip() or "Pull failed"
                        pm.complete_operation(op_id, error=error_msg)
                        msg = json.dumps({"error": error_msg, "status": "failed"})
                        yield f"data: {msg}\n\n"
                except Exception as exc:
                    error_detail = f"{exc.__class__.__name__}: {exc!s}"
                    _log.error("ollama/pull error", err=exc)
                    pm.complete_operation(op_id, error=error_detail)
                    msg = json.dumps({"error": error_detail, "status": "failed"})
                    yield f"data: {msg}\n\n"

            return StreamingResponse(
                generate_progress(), media_type="text/event-stream"
            )
        except Exception as exc:
            error_detail = f"{exc.__class__.__name__}: {exc!s}"
            _log.error("ollama/pull handler error", err=exc)
            raise HTTPException(status_code=500, detail=error_detail)

    @router.post("/port-conflicts")
    async def check_port_conflicts():
        """Check for port conflicts and return details with repair options."""
        pm = get_port_manager()
        pm.check_all_services()

        conflicts = []
        for name, service in pm.services.items():
            if not service.port:
                continue

            occupant = pm.get_port_occupant(service.port)
            if occupant:
                conflicts.append({
                    "service": name,
                    "port": service.port,
                    "expected_process": service.process_name,
                    "actual_process": occupant.get("process"),
                    "pid": occupant.get("pid"),
                    "is_correct": occupant.get("process") == service.process_name,
                    "can_kill": True,
                    "can_restart": bool(service.startup_cmd),
                })

        return {
            "conflicts": conflicts,
            "total": len(conflicts),
            "requires_attention": any(not c["is_correct"] for c in conflicts),
        }

    @router.post("/port-conflicts/kill")
    async def kill_port_conflict(payload: dict):
        """Kill process occupying a port."""
        pid = payload.get("pid")
        service_name = payload.get("service")

        if not pid:
            raise HTTPException(status_code=400, detail="Missing pid")

        pm = get_port_manager()

        try:
            success = pm.kill_process_by_pid(int(pid), force=True)
            if success:
                return {
                    "success": True,
                    "message": f"Killed process {pid}",
                    "pid": pid,
                    "service": service_name,
                }
            else:
                raise HTTPException(status_code=500, detail=f"Failed to kill PID {pid}")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/port-conflicts/restart")
    async def restart_conflicted_service(payload: dict):
        """Kill conflicting process and restart service."""
        service_name = payload.get("service")

        if not service_name:
            raise HTTPException(status_code=400, detail="Missing service name")

        pm = get_port_manager()
        service = pm.services.get(service_name)

        if not service:
            raise HTTPException(
                status_code=404, detail=f"Unknown service: {service_name}"
            )

        # Kill existing process on port
        if service.port:
            occupant = pm.get_port_occupant(service.port)
            if occupant:
                pid = occupant.get("pid")
                pm.kill_process_by_pid(int(pid), force=True)
                time.sleep(1)

        # Start service
        result = pm.start_service(service_name, wait_for_ready=True, timeout=15)

        if result.get("success"):
            return {
                "success": True,
                "message": f"Restarted {service_name}",
                "pid": result.get("pid"),
                "port": result.get("port"),
            }
        else:
            raise HTTPException(
                status_code=500, detail=result.get("error", "Failed to restart service")
            )

    @router.post("/ok-setup")
    async def run_ok_setup_endpoint():
        """Run OK setup with progress streaming."""
        from fastapi.responses import StreamingResponse

        try:

            async def generate_progress():
                pm = get_port_manager()

                # Register operation start
                op_id = pm.start_operation(
                    operation_type="ok_setup", description="Running OK Gateway setup"
                )

                try:
                    # Use json.dumps for proper escaping
                    msg = json.dumps({
                        "progress": 0,
                        "status": "starting",
                        "message": "Initializing OK Setup...",
                    })
                    yield f"data: {msg}\n\n"

                    try:
                        from core.services.ok_setup import run_ok_setup
                    except Exception as exc:
                        pm.complete_operation(op_id, error=f"Import failed: {exc!s}")
                        msg = json.dumps({
                            "error": f"Import failed: {exc!s}",
                            "status": "failed",
                        })
                        yield f"data: {msg}\n\n"
                        return

                    msg = json.dumps({
                        "progress": 10,
                        "status": "running",
                        "message": "Checking Ollama installation...",
                    })
                    yield f"data: {msg}\n\n"

                    try:
                        result = run_ok_setup(get_repo_root())
                    except Exception as exc:
                        error_detail = f"{exc.__class__.__name__}: {exc!s}"
                        _log.error("ok_setup error", err=exc)
                        pm.complete_operation(op_id, error=error_detail)
                        msg = json.dumps({
                            "error": f"Setup failed: {error_detail}",
                            "status": "failed",
                        })
                        yield f"data: {msg}\n\n"
                        return

                    # Update operation progress
                    pm.update_operation(
                        op_id, progress=50, status=OperationStatus.IN_PROGRESS
                    )

                    msg = json.dumps({
                        "progress": 50,
                        "status": "running",
                        "message": "Configuring OK Gateway...",
                    })
                    yield f"data: {msg}\n\n"

                    steps = result.get("steps", [])
                    warnings = result.get("warnings", [])

                    for step in steps:
                        # Use json.dumps for proper escaping
                        msg = json.dumps({
                            "progress": 70,
                            "status": "running",
                            "message": f"✅ {step}",
                        })
                        yield f"data: {msg}\n\n"

                    for warn in warnings:
                        # Use json.dumps for proper escaping
                        msg = json.dumps({
                            "progress": 80,
                            "status": "warning",
                            "message": f"⚠️ {warn}",
                        })
                        yield f"data: {msg}\n\n"

                    pm.complete_operation(op_id)
                    # Don't include full result in JSON - too complex to serialize safely
                    summary = {
                        "progress": 100,
                        "status": "complete",
                        "message": "✅ OK Setup completed",
                        "steps_count": len(steps),
                        "warnings_count": len(warnings),
                    }
                    msg = json.dumps(summary)
                    yield f"data: {msg}\n\n"
                except Exception as exc:
                    error_detail = f"{exc.__class__.__name__}: {exc!s}"
                    _log.error("ok-setup outer error", err=exc)
                    pm.complete_operation(op_id, error=error_detail)
                    msg = json.dumps({
                        "error": f"Setup failed: {error_detail}",
                        "status": "failed",
                    })
                    yield f"data: {msg}\n\n"

            return StreamingResponse(
                generate_progress(), media_type="text/event-stream"
            )
        except Exception as exc:
            error_detail = f"{exc.__class__.__name__}: {exc!s}"
            _log.error("ok-setup handler error", err=exc)
            raise HTTPException(status_code=500, detail=error_detail)

    @router.post("/nounproject/seed")
    async def seed_icons(payload: SeedRequest):
        """Seed Noun Project icons with progress tracking."""
        from fastapi.responses import StreamingResponse

        try:

            async def generate_progress():
                pm = get_port_manager()

                # Register operation start
                op_id = pm.start_operation(
                    operation_type="seed_icons",
                    description="Seeding Noun Project icons",
                )

                try:
                    categories = payload.categories or DEFAULT_CATEGORIES
                    per_term = max(1, min(payload.per_term, 5))
                    dest_root = _diagrams_root()
                    dest_root.mkdir(parents=True, exist_ok=True)

                    # Calculate total work
                    total_terms = sum(len(terms) for terms in categories.values())
                    processed = 0

                    # Use json.dumps for proper escaping
                    msg = json.dumps({
                        "progress": 0,
                        "status": "authenticating",
                        "message": "Authenticating with Noun Project...",
                    })
                    yield f"data: {msg}\n\n"

                    client = _nounproject_client()
                    try:
                        await client.authenticate()
                    except Exception as exc:
                        error_detail = f"{exc.__class__.__name__}: {exc!s}"
                        _log.error("noun auth error", err=exc)
                        pm.complete_operation(op_id, error=error_detail)
                        msg = json.dumps({
                            "error": f"Auth failed: {error_detail}",
                            "status": "failed",
                        })
                        yield f"data: {msg}\n\n"
                        return

                    msg = json.dumps({
                        "progress": 5,
                        "status": "seeding",
                        "message": "Starting icon download...",
                    })
                    yield f"data: {msg}\n\n"

                    added = []
                    skipped = []
                    errors = []

                    for category, terms in categories.items():
                        cat_dir = dest_root / category
                        cat_dir.mkdir(parents=True, exist_ok=True)

                        for term in terms:
                            processed += 1
                            progress = int(5 + (processed / total_terms) * 85)

                            # Use json.dumps for proper escaping
                            msg = json.dumps({
                                "progress": progress,
                                "status": "seeding",
                                "message": f"Searching {category}: {term}...",
                            })
                            yield f"data: {msg}\n\n"

                            # Update operation progress
                            pm.update_operation(
                                op_id,
                                progress=progress,
                                status=OperationStatus.IN_PROGRESS,
                            )

                            try:
                                result = await client.search(term=term, limit=10)
                            except Exception as exc:
                                errors.append(f"{category}:{term} search failed: {exc}")
                                msg = json.dumps({
                                    "progress": progress,
                                    "status": "warning",
                                    "message": f"⚠️ Search failed: {term}",
                                })
                                yield f"data: {msg}\n\n"
                                continue

                            icons = (result.get("icons") or [])[:per_term]
                            for icon in icons:
                                icon_id = icon.get("id")
                                if not icon_id:
                                    continue
                                try:
                                    download = await client.download(
                                        icon_id=int(icon_id), format="svg"
                                    )
                                    src_path = Path(download.get("path", ""))
                                    if not src_path.exists():
                                        errors.append(
                                            f"{category}:{term} {icon_id} missing cache file"
                                        )
                                        continue
                                    file_name = f"{_slugify(term)}-{icon_id}.svg"
                                    dest_path = cat_dir / file_name
                                    if dest_path.exists():
                                        skipped.append(str(dest_path))
                                        continue
                                    shutil.copyfile(src_path, dest_path)
                                    added.append(str(dest_path))
                                except Exception as exc:
                                    errors.append(
                                        f"{category}:{term} {icon_id} download failed: {exc}"
                                    )

                    # Final summary
                    pm.complete_operation(op_id)
                    summary = {
                        "progress": 100,
                        "status": "complete",
                        "message": f"✅ Seeded {len(added)} SVGs (skipped {len(skipped)}, {len(errors)} errors)",
                        "added_count": len(added),
                        "skipped_count": len(skipped),
                        "error_count": len(errors),
                        "root": str(dest_root),
                    }
                    msg = json.dumps(summary)
                    yield f"data: {msg}\n\n"
                except Exception as exc:
                    error_detail = f"{exc.__class__.__name__}: {exc!s}"
                    _log.error("nounproject/seed error", err=exc)
                    pm.complete_operation(op_id, error=error_detail)
                    # Use json.dumps for proper escaping
                    msg = json.dumps({
                        "error": f"Seeding failed: {error_detail}",
                        "status": "failed",
                    })
                    yield f"data: {msg}\n\n"

            return StreamingResponse(
                generate_progress(), media_type="text/event-stream"
            )
        except Exception as exc:
            error_detail = f"{exc.__class__.__name__}: {exc!s}"
            _log.error("nounproject/seed handler error", err=exc)
            raise HTTPException(status_code=500, detail=error_detail)

    return router
