"""Background process lifecycle helpers for core-managed services."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import signal
import subprocess
import time

from core.services.logging_api import get_logger, get_repo_root
from core.services.stdlib_http import HTTPError, http_get

_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
_WIZARD_DEFAULT_BASE_URL = "http://127.0.0.1:8765"
_WIZARD_START_CMD = ("uv", "run", "wizard/server.py", "--no-interactive")

logger = get_logger("background-service-manager")


@dataclass(slots=True)
class WizardServiceStatus:
    base_url: str
    running: bool
    connected: bool
    pid: int | None
    message: str
    health: dict[str, object]


def _extract_host(url: str) -> str:
    value = (url or "").strip()
    if "://" in value:
        value = value.split("://", 1)[1]
    authority = value.split("/", 1)[0].strip()
    if "@" in authority:
        authority = authority.rsplit("@", 1)[1]
    if authority.startswith("["):
        return authority[1:].split("]", 1)[0].strip().lower()
    return authority.split(":", 1)[0].strip().lower()


def _assert_loopback_base_url(base_url: str) -> None:
    if _extract_host(base_url) in _LOOPBACK_HOSTS:
        return
    raise ValueError(f"non-loopback target blocked: {base_url}")


class WizardProcessManager:
    """Manage Wizard lifecycle for on-demand core command execution."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.pid_file = self.repo_root / ".wizard.pid"
        self.log_file = self.repo_root / "memory" / "logs" / "wizard-daemon.log"

    @staticmethod
    def _base_url(value: str | None = None) -> str:
        from core.services.unified_config_loader import get_config

        base_url = (value or get_config("WIZARD_BASE_URL", "") or _WIZARD_DEFAULT_BASE_URL).rstrip("/")
        _assert_loopback_base_url(base_url)
        return base_url

    @staticmethod
    def _pid_alive(pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def _read_pid(self) -> int | None:
        if not self.pid_file.exists():
            return None
        raw_pid = self.pid_file.read_text(encoding="utf-8").strip()
        if not raw_pid.isdigit():
            return None
        pid = int(raw_pid)
        return pid if self._pid_alive(pid) else None

    def _write_pid(self, pid: int) -> None:
        self.pid_file.write_text(f"{pid}\n", encoding="utf-8")

    def _clear_pid(self) -> None:
        self.pid_file.unlink(missing_ok=True)

    @staticmethod
    def _health(base_url: str, timeout: int = 2) -> tuple[bool, dict[str, object]]:
        try:
            response = http_get(f"{base_url}/health", timeout=timeout)
        except HTTPError:
            return False, {}
        payload = response.get("json") if isinstance(response, dict) else None
        data = payload if isinstance(payload, dict) else {}
        return response.get("status_code") == 200, data

    def status(self, *, base_url: str | None = None) -> WizardServiceStatus:
        url = self._base_url(base_url)
        connected, health = self._health(url, timeout=2)
        pid = self._read_pid()
        running = connected or pid is not None
        if connected:
            message = "wizard reachable"
        elif running:
            message = "wizard process running but not healthy"
        else:
            message = "wizard not running"
        return WizardServiceStatus(
            base_url=url,
            running=running,
            connected=connected,
            pid=pid,
            message=message,
            health=health,
        )

    def ensure_running(self, *, base_url: str | None = None, wait_seconds: int = 25) -> WizardServiceStatus:
        status = self.status(base_url=base_url)
        if status.connected:
            return status

        if not status.running:
            self._start_process()

        deadline = time.monotonic() + max(1, wait_seconds)
        url = self._base_url(base_url)
        while time.monotonic() < deadline:
            connected, health = self._health(url, timeout=1)
            if connected:
                pid = self._read_pid()
                return WizardServiceStatus(
                    base_url=url,
                    running=True,
                    connected=True,
                    pid=pid,
                    message="wizard started",
                    health=health,
                )
            time.sleep(0.25)

        latest = self.status(base_url=url)
        if latest.running:
            latest.message = "wizard start timeout"
        return latest

    def _start_process(self) -> int:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.log_file.open("ab") as handle:
            proc = subprocess.Popen(
                list(_WIZARD_START_CMD),
                cwd=self.repo_root,
                stdin=subprocess.DEVNULL,
                stdout=handle,
                stderr=handle,
                start_new_session=os.name != "nt",
            )
        self._write_pid(proc.pid)
        logger.info("started wizard process pid=%s", proc.pid)
        return proc.pid

    def stop(self, *, base_url: str | None = None, timeout_seconds: int = 8) -> WizardServiceStatus:
        _ = self._base_url(base_url)
        pid = self._read_pid()
        if pid is None:
            self._clear_pid()
            return self.status(base_url=base_url)

        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            self._clear_pid()
            return self.status(base_url=base_url)

        deadline = time.monotonic() + max(1, timeout_seconds)
        while time.monotonic() < deadline:
            if not self._pid_alive(pid):
                self._clear_pid()
                return self.status(base_url=base_url)
            time.sleep(0.2)

        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        self._clear_pid()
        return self.status(base_url=base_url)


_WIZARD_MANAGER: WizardProcessManager | None = None


def get_wizard_process_manager() -> WizardProcessManager:
    global _WIZARD_MANAGER
    if _WIZARD_MANAGER is None:
        _WIZARD_MANAGER = WizardProcessManager()
    return _WIZARD_MANAGER
