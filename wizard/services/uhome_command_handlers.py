"""uHOME Command Handlers

Implements the uHOME commands exposed through the Home Assistant bridge.
Each handler is a pure function that takes params and returns a result dict.

Scope:
    - Tuner: HDHomeRun HTTP discovery (LAN probe, no third-party SDK required)
    - DVR: JSON-backed schedule store under memory/bank/uhome/
    - Ad processing: Wizard config flag (get/set)
    - Playback: Jellyfin HTTP probe if configured; status-only otherwise
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.services.logging_manager import get_logger

_log = get_logger("wizard.uhome-handlers")

# ------------------------------------------------------------------
# DVR schedule store path
# ------------------------------------------------------------------

def _dvr_schedule_path() -> Path:
    try:
        from core.services.logging_api import get_repo_root
        return get_repo_root() / "memory" / "bank" / "uhome" / "dvr_schedule.json"
    except Exception:
        return Path.home() / ".udos" / "uhome" / "dvr_schedule.json"


def _load_schedule() -> list[dict[str, Any]]:
    path = _dvr_schedule_path()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_schedule(rules: list[dict[str, Any]]) -> None:
    path = _dvr_schedule_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rules, indent=2), encoding="utf-8")


# ------------------------------------------------------------------
# Tuner handlers
# ------------------------------------------------------------------

def tuner_discover(params: dict[str, Any]) -> dict[str, Any]:
    """Probe LAN for HDHomeRun devices via their HTTP discovery endpoint."""
    import socket

    devices: list[dict[str, Any]] = []
    candidates = [
        params.get("host") or "hdhomerun.local",
        "192.168.1.1",  # common home router; HDHomeRun often on same subnet
    ]
    # Also try the configured tuner host from env/config
    try:
        from core.services.unified_config_loader import get_config
        env_host = get_config("HDHOMERUN_HOST", "").strip()
        if env_host:
            candidates.insert(0, env_host)
    except Exception:
        pass

    for host in dict.fromkeys(candidates):  # dedupe while preserving order
        try:
            ip = socket.gethostbyname(host)
            import urllib.request
            with urllib.request.urlopen(
                f"http://{ip}/discover.json", timeout=2
            ) as resp:
                data = json.loads(resp.read())
                devices.append({
                    "host": ip,
                    "device_id": data.get("DeviceID"),
                    "friendly_name": data.get("FriendlyName", "HDHomeRun"),
                    "model": data.get("ModelNumber"),
                    "tuner_count": data.get("TunerCount", 1),
                    "firmware": data.get("FirmwareVersion"),
                    "base_url": data.get("BaseURL"),
                })
        except Exception as exc:
            _log.debug("tuner_discover: %s unreachable: %s", host, exc)

    return {
        "command": "uhome.tuner.discover",
        "devices_found": len(devices),
        "devices": devices,
    }


def tuner_status(params: dict[str, Any]) -> dict[str, Any]:
    """Return status of the primary HDHomeRun tuner."""
    try:
        from core.services.unified_config_loader import get_config
        host = (params.get("host") or get_config("HDHOMERUN_HOST", "") or "hdhomerun.local").strip()
    except Exception:
        host = params.get("host") or "hdhomerun.local"

    result: dict[str, Any] = {
        "command": "uhome.tuner.status",
        "host": host,
        "reachable": False,
        "channels": [],
    }

    try:
        import socket
        import urllib.request
        ip = socket.gethostbyname(host)
        with urllib.request.urlopen(f"http://{ip}/discover.json", timeout=2) as resp:
            data = json.loads(resp.read())
            result["reachable"] = True
            result["device_id"] = data.get("DeviceID")
            result["model"] = data.get("ModelNumber")
            result["tuner_count"] = data.get("TunerCount", 1)
    except Exception as exc:
        result["issue"] = str(exc)

    return result


# ------------------------------------------------------------------
# DVR handlers
# ------------------------------------------------------------------

def dvr_list_rules(params: dict[str, Any]) -> dict[str, Any]:
    """Return all DVR schedule rules."""
    rules = _load_schedule()
    return {
        "command": "uhome.dvr.list_rules",
        "rule_count": len(rules),
        "rules": rules,
    }


def dvr_schedule(params: dict[str, Any]) -> dict[str, Any]:
    """Add a DVR schedule rule."""
    title = str(params.get("title") or "").strip()
    if not title:
        return {"command": "uhome.dvr.schedule", "success": False, "error": "title is required"}

    rule: dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "channel": params.get("channel"),
        "start_time": params.get("start_time"),
        "duration_minutes": params.get("duration_minutes"),
        "repeat": params.get("repeat", "none"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    rules = _load_schedule()
    rules.append(rule)
    _save_schedule(rules)

    return {"command": "uhome.dvr.schedule", "success": True, "rule": rule}


def dvr_cancel(params: dict[str, Any]) -> dict[str, Any]:
    """Remove a DVR schedule rule by id."""
    rule_id = str(params.get("id") or "").strip()
    if not rule_id:
        return {"command": "uhome.dvr.cancel", "success": False, "error": "id is required"}

    rules = _load_schedule()
    before = len(rules)
    rules = [r for r in rules if r.get("id") != rule_id]
    _save_schedule(rules)

    removed = before - len(rules)
    return {
        "command": "uhome.dvr.cancel",
        "success": removed > 0,
        "removed": removed,
        "id": rule_id,
    }


# ------------------------------------------------------------------
# Ad-processing handlers
# ------------------------------------------------------------------

_AD_MODE_KEY = "uhome_ad_processing_mode"
_AD_MODES = {"disabled", "comskip_auto", "comskip_manual", "passthrough"}


def ad_get_mode(params: dict[str, Any]) -> dict[str, Any]:
    """Return the current ad-processing mode from Wizard config."""
    mode = "disabled"
    try:
        from wizard.services.wizard_config import WizardConfig
        mode = str(WizardConfig().get(_AD_MODE_KEY, "disabled") or "disabled")
    except Exception:
        pass

    return {"command": "uhome.ad_processing.get_mode", "mode": mode, "valid_modes": sorted(_AD_MODES)}


def ad_set_mode(params: dict[str, Any]) -> dict[str, Any]:
    """Set the ad-processing mode in Wizard config."""
    mode = str(params.get("mode") or "").strip().lower()
    if mode not in _AD_MODES:
        return {
            "command": "uhome.ad_processing.set_mode",
            "success": False,
            "error": f"invalid mode {mode!r}; valid: {sorted(_AD_MODES)}",
        }

    try:
        from wizard.services.wizard_config import WizardConfig
        cfg = WizardConfig()
        cfg.set(_AD_MODE_KEY, mode)
    except Exception as exc:
        return {
            "command": "uhome.ad_processing.set_mode",
            "success": False,
            "error": str(exc),
        }

    return {"command": "uhome.ad_processing.set_mode", "success": True, "mode": mode}


# ------------------------------------------------------------------
# Playback handlers
# ------------------------------------------------------------------

def _jellyfin_base_url() -> str:
    try:
        from core.services.unified_config_loader import get_config
        return (get_config("JELLYFIN_URL", "") or "").strip()
    except Exception:
        return ""


def playback_status(params: dict[str, Any]) -> dict[str, Any]:
    """Return playback status, probing Jellyfin if configured."""
    base_url = _jellyfin_base_url()
    result: dict[str, Any] = {
        "command": "uhome.playback.status",
        "jellyfin_configured": bool(base_url),
        "active_sessions": [],
    }

    if not base_url:
        result["note"] = "Set JELLYFIN_URL to enable live playback status."
        return result

    try:
        import urllib.request
        api_key = ""
        try:
            from core.services.unified_config_loader import get_config
            api_key = get_config("JELLYFIN_API_KEY", "") or ""
        except Exception:
            pass

        url = f"{base_url.rstrip('/')}/Sessions?api_key={api_key}"
        with urllib.request.urlopen(url, timeout=3) as resp:
            sessions = json.loads(resp.read())
            active = [s for s in sessions if s.get("NowPlayingItem")]
            result["active_sessions"] = [
                {
                    "user": s.get("UserName"),
                    "title": s.get("NowPlayingItem", {}).get("Name"),
                    "media_type": s.get("NowPlayingItem", {}).get("Type"),
                    "client": s.get("Client"),
                }
                for s in active
            ]
            result["jellyfin_reachable"] = True
    except Exception as exc:
        result["jellyfin_reachable"] = False
        result["issue"] = str(exc)

    return result


def playback_handoff(params: dict[str, Any]) -> dict[str, Any]:
    """Queue a playback handoff event (deferred to next playback session)."""
    item_id = str(params.get("item_id") or "").strip()
    target_client = str(params.get("target_client") or "default").strip()

    if not item_id:
        return {
            "command": "uhome.playback.handoff",
            "success": False,
            "error": "item_id is required",
        }

    # Persist to a handoff queue file
    try:
        from core.services.logging_api import get_repo_root
        queue_path = get_repo_root() / "memory" / "bank" / "uhome" / "playback_queue.json"
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        queue: list[dict[str, Any]] = []
        if queue_path.exists():
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
        queue.append({
            "id": str(uuid.uuid4())[:8],
            "item_id": item_id,
            "target_client": target_client,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "params": {k: v for k, v in params.items() if k not in {"item_id", "target_client"}},
        })
        queue_path.write_text(json.dumps(queue, indent=2), encoding="utf-8")
        return {
            "command": "uhome.playback.handoff",
            "success": True,
            "item_id": item_id,
            "target_client": target_client,
        }
    except Exception as exc:
        return {
            "command": "uhome.playback.handoff",
            "success": False,
            "error": str(exc),
        }


# ------------------------------------------------------------------
# Dispatch table
# ------------------------------------------------------------------

_HANDLERS = {
    "uhome.tuner.discover": tuner_discover,
    "uhome.tuner.status": tuner_status,
    "uhome.dvr.list_rules": dvr_list_rules,
    "uhome.dvr.schedule": dvr_schedule,
    "uhome.dvr.cancel": dvr_cancel,
    "uhome.ad_processing.get_mode": ad_get_mode,
    "uhome.ad_processing.set_mode": ad_set_mode,
    "uhome.playback.status": playback_status,
    "uhome.playback.handoff": playback_handoff,
}


def dispatch(command: str, params: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a uHOME command to its handler.

    Returns a result dict. Raises KeyError for unknown commands.
    """
    handler = _HANDLERS.get(command)
    if handler is None:
        raise KeyError(f"No handler for uHOME command: {command!r}")
    return handler(params)
