"""System Script Runner
=====================

Ensures `/memory/bank/system` scripts exist and invokes them via the TS runtime.
Provides startup/reboot hooks that seed the runtime with simple DRAW PAT output
so the Core TUI and automation logs always show a visible signal when each run
executes.

Author: uDOS Engineering
Version: v1.0.1
Date: 2026-02-02
"""
from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from core.services.automation_monitor import AutomationMonitor
from core.services.hotkey_map import read_hotkey_payload, write_hotkey_payload
from core.services.logging_api import get_logger, get_repo_root
from core.services.notification_history_service import remind_if_pending
from core.services.provider_registry import (
    ProviderNotAvailableError,
    ProviderType,
    get_provider,
)
from core.services.todo_reminder_service import get_reminder_service
from core.services.ts_runtime_service import TSRuntimeService

logger = get_logger("system-script")


class SystemScriptRunner:
    """Runs the startup/reboot scripts stored under /memory/bank/system."""

    SCRIPT_TEMPLATE_DIR = Path("core/framework/seed/bank/system")

    def __init__(self):
        self.repo_root = get_repo_root()
        from core.services.paths import get_memory_root

        self.memory_root = get_memory_root()
        self.system_dir = self.memory_root / "bank" / "system"
        self.user_system_dir = self.memory_root / "user" / "system"
        try:
            provider = get_provider(ProviderType.MONITORING_MANAGER)
            self.monitoring = provider() if callable(provider) else provider
        except ProviderNotAvailableError:
            self.monitoring = None
        except Exception:
            self.monitoring = None
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.user_system_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = self.repo_root / self.SCRIPT_TEMPLATE_DIR
        self.todo_reminder = get_reminder_service()

        # Migrate old scripts from memory/system to memory/bank/system
        self._migrate_old_scripts()

        # Seed system scripts on first run
        self._seed_system_scripts()

    def _migrate_old_scripts(self) -> None:
        """Migrate scripts from old memory/system to new memory/bank/system location."""
        old_system_dir = self.memory_root / "system"
        if old_system_dir.exists() and old_system_dir.is_dir():
            for script_name in ["startup-script.md", "reboot-script.md"]:
                old_script = old_system_dir / script_name
                if old_script.exists():
                    new_script = self.system_dir / script_name
                    if not new_script.exists():
                        try:
                            shutil.move(str(old_script), str(new_script))
                            logger.info(f"[MIGRATION] Moved {script_name} to memory/bank/system/")
                        except Exception as exc:
                            logger.warning(f"[MIGRATION] Failed to move {script_name}: {exc}")

    def _seed_system_scripts(self) -> None:
        """Seed system scripts from templates if they don't exist."""
        script_templates = ["startup-script.md", "reboot-script.md"]

        for script_name in script_templates:
            target = self.system_dir / script_name
            if not target.exists():
                template = self.template_dir / script_name
                if template.exists():
                    try:
                        shutil.copy(template, target)
                        logger.info(f"[SYSTEM SCRIPT] Seeded {script_name} from template")
                    except Exception as exc:
                        logger.warning(f"[SYSTEM SCRIPT] Failed to seed {script_name}: {exc}")
                else:
                    logger.warning(f"[SYSTEM SCRIPT] Template not found: {template}")

    def run_startup_script(self) -> dict[str, Any]:
        """Run the startup script and return the execution summary."""
        return self._run_script("startup-script.md", "startup")

    def run_reboot_script(self) -> dict[str, Any]:
        """Run the reboot script and return the execution summary."""
        return self._run_script("reboot-script.md", "reboot")

    def _run_script(self, script_name: str, label: str) -> dict[str, Any]:
        _previous_hotkeys = read_hotkey_payload(self.memory_root)
        hotkey_payload = write_hotkey_payload(self.memory_root)
        automation_monitor = AutomationMonitor(self.memory_root)
        automation_summary = automation_monitor.summary()
        if automation_summary.get("should_gate"):
            message = (
                "Automation gating active: "
                f"{automation_summary.get('gate_reason') or 'monitoring throttle'}"
            )
            logger.warning(f"[SYSTEM SCRIPT] {message}")
            return {
                "status": "gated",
                "message": message,
                "script": script_name,
                "automation_monitor": automation_summary,
                "hotkey_snapshot": hotkey_payload.get("snapshot"),
            }
        notification_reminder = remind_if_pending()
        todo_reminder = self.todo_reminder.log_reminder()
        script_path = self._resolve_script_path(script_name, label)
        if not script_path:
            message = f"{label.title()} script not found ({script_name})"
            logger.warning(f"[SYSTEM SCRIPT] {message}")
            return {
                "status": "error",
                "message": message,
                "script": script_name,
                "notification_reminder": notification_reminder,
                "todo_reminder": todo_reminder,
            }

        monitoring_summary = self.monitoring.log_training_summary() if self.monitoring else None

        service = TSRuntimeService()
        result = service.execute(script_path)
        if result.get("status") != "success":
            message = result.get("message", "Unknown error")
            details = result.get("details", "")
            logger.warning(f"[SYSTEM SCRIPT] {label.title()} failed: {message}")
            return {
                "status": "error",
                "message": message,
                "details": details,
                "script": script_name,
                "script_path": str(script_path),
                "monitoring_summary": monitoring_summary,
                "notification_reminder": notification_reminder,
                "automation_monitor": automation_summary,
                "todo_reminder": todo_reminder,
            }

        payload = result.get("payload", {})
        exec_result = payload.get("result", {})
        output = exec_result.get("output", "").strip()
        hotkey_snapshot = hotkey_payload.get("snapshot")
        hotkey_last = hotkey_payload.get("last_updated")
        message = f"{label.title()} script executed"
        logger.info(f"[SYSTEM SCRIPT] {message} ({script_path})")
        if hotkey_snapshot:
            logger.info(f"[SYSTEM SCRIPT] Hotkey snapshot: {hotkey_snapshot} ({hotkey_last})")
        reminder = remind_if_pending()
        return {
            "status": "success",
            "message": message,
            "script": script_name,
            "script_path": str(script_path),
            "output": output,
            "hotkey_snapshot": hotkey_snapshot,
            "hotkey_last_updated": hotkey_last,
            "monitoring_summary": monitoring_summary,
            "notification_reminder": reminder,
            "automation_monitor": automation_summary,
            "todo_reminder": todo_reminder,
        }

    def _resolve_script_path(self, script_name: str, label: str) -> Path | None:
        env_path = self._env_override_path(label)
        if env_path and env_path.exists():
            return env_path

        user_override = self.user_system_dir / script_name
        if user_override.exists():
            return user_override

        target = self.system_dir / script_name
        if target.exists():
            return target

        return self._seed_script(script_name)

    @staticmethod
    def _env_override_key(label: str) -> str:
        return f"UDOS_{label.upper()}_SCRIPT_PATH"

    def _env_override_path(self, label: str) -> Path | None:
        key = self._env_override_key(label)
        from core.services.unified_config_loader import get_config

        value = get_config(key, "").strip()
        if not value:
            return None
        candidate = Path(value)
        if candidate.is_absolute():
            return candidate
        return (self.repo_root / candidate).resolve()

    def _seed_script(self, script_name: str) -> Path | None:
        target = self.system_dir / script_name
        template = self.template_dir / script_name
        if template.exists():
            try:
                shutil.copy(template, target)
                return target
            except Exception as exc:
                logger.warning(f"[SYSTEM SCRIPT] Failed to copy {template}: {exc}")
                return None

        logger.warning(f"[SYSTEM SCRIPT] Template missing: {template}")
        return None
