"""Sonic Linux launcher adapter for Alpine GUI session flows."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from core.services.json_utils import read_json_file, write_json_file
from core.services.time_utils import utc_now_iso_z
from wizard.services.launch_adapters import LaunchAdapterExecution
from wizard.services.launch_orchestrator import (
    LaunchIntent,
    get_launch_orchestrator,
)

VALID_ACTIONS = {"start", "stop", "restart"}
VALID_PROTOCOLS = {"openrc", "direct"}


@dataclass(frozen=True)
class _LinuxLauncherAdapter:
    action: str
    protocol: str
    command: list[str]
    execute_command: bool
    workspace: str | None
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]]

    def starting_state(self, intent: LaunchIntent) -> str:
        return "stopping" if self.action == "stop" else "starting"

    def execute(self, intent: LaunchIntent) -> LaunchAdapterExecution:
        exit_code: int | None = None
        command_error: str | None = None
        command_output: str | None = None
        if self.execute_command:
            result = self.runner(self.command)
            exit_code = result.returncode
            command_output = (result.stdout or "").strip()[:2000] or None
            if result.returncode != 0:
                command_error = (result.stderr or result.stdout or "launcher action failed").strip()[:2000]

        final_state = "error" if command_error else ("stopped" if self.action == "stop" else "ready")
        return LaunchAdapterExecution(
            final_state=final_state,
            error=command_error,
            session_updates={
                "action": self.action,
                "protocol": self.protocol,
                "command": self.command,
                "executed": self.execute_command,
                "workspace": self.workspace,
                "exit_code": exit_code,
            },
            state_payload={
                "action": self.action,
                "protocol": self.protocol,
                "workspace": self.workspace,
                "executed": self.execute_command,
                "command": self.command,
                "updated_at": utc_now_iso_z(),
                "last_exit_code": exit_code,
                "last_error": command_error,
                "last_output": command_output,
            },
        )


class SonicLinuxLauncherService:
    def __init__(
        self,
        repo_root: Path | None = None,
        runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
    ):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.script_path = self.repo_root / "distribution" / "udos" / "bin" / "udos-gui"
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "linux-launcher.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.launch_orchestrator = get_launch_orchestrator(repo_root=self.repo_root)
        self.runner = runner or self._run_command

    def _read_state(self) -> dict[str, Any]:
        return read_json_file(self.state_path, default={})

    def _write_state(self, payload: dict[str, Any]) -> None:
        write_json_file(self.state_path, payload, indent=2)

    def _run_command(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, check=False, capture_output=True, text=True)

    def get_status(self) -> dict[str, Any]:
        state = self._read_state()
        return {
            "enabled": self.script_path.exists(),
            "script_path": str(self.script_path),
            "state_path": str(self.state_path),
            "launch_state_namespace": str(self.repo_root / "memory" / "wizard" / "launch"),
            "available_actions": sorted(VALID_ACTIONS),
            "available_protocols": sorted(VALID_PROTOCOLS),
            "action": state.get("action"),
            "state": state.get("state"),
            "session_id": state.get("session_id"),
            "workspace": state.get("workspace"),
            "protocol": state.get("protocol"),
            "updated_at": state.get("updated_at"),
            "last_exit_code": state.get("last_exit_code"),
        }

    def apply_action(
        self,
        action: str,
        *,
        workspace: str | None = None,
        protocol: str = "openrc",
        execute: bool = False,
    ) -> dict[str, Any]:
        normalized_action = action.strip().lower()
        if normalized_action not in VALID_ACTIONS:
            raise ValueError(f"Unsupported launcher action: {action}")

        normalized_protocol = protocol.strip().lower()
        if normalized_protocol not in VALID_PROTOCOLS:
            raise ValueError(f"Unsupported launcher protocol: {protocol}")

        if not self.script_path.exists():
            raise FileNotFoundError(f"Linux launcher script not found: {self.script_path}")

        command = [str(self.script_path), normalized_action]
        intent = LaunchIntent(
            target="alpine-core-linux-gui",
            mode="gui",
            launcher="udos-gui",
            workspace=workspace,
            profile_id="alpine-core-gui",
            auth={"protocol": normalized_protocol},
        )
        adapter = _LinuxLauncherAdapter(
            action=normalized_action,
            protocol=normalized_protocol,
            command=command,
            execute_command=execute,
            workspace=workspace,
            runner=self.runner,
        )
        result = self.launch_orchestrator.execute(intent, adapter)
        payload = result["state"]
        self._write_state(payload)
        return payload


def get_sonic_linux_launcher_service(repo_root: Path | None = None) -> SonicLinuxLauncherService:
    return SonicLinuxLauncherService(repo_root=repo_root)
