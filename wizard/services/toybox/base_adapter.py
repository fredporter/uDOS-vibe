"""Shared PTY adapter runtime for TOYBOX upstream game integrations."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import fcntl
import json
import os
import pty
import re
import shlex
import shutil
import signal
import threading
import time
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.services.logging_api import get_repo_root
from core.services.unified_config_loader import get_dynamic_config


class InputRequest(BaseModel):
    text: str


class PTYAdapter:
    """Run an upstream binary in a PTY and expose minimal HTTP controls."""

    def __init__(
        self,
        *,
        adapter_id: str,
        env_cmd_var: str,
        command_candidates: list[str],
        startup_args: list[str] | None = None,
        parse_fn: Callable[[str], list[dict[str, Any]]] | None = None,
        max_start_retries: int = 3,
        retry_backoff_seconds: list[float] | None = None,
    ) -> None:
        self.adapter_id = adapter_id
        self.env_cmd_var = env_cmd_var
        self.command_candidates = command_candidates
        self.startup_args = startup_args or []
        self.parse_fn = parse_fn
        self.max_start_retries = max(0, int(max_start_retries))
        self.retry_backoff_seconds = list(retry_backoff_seconds or [1.0, 2.0, 4.0])

        self.repo_root = get_repo_root()
        self.event_file = (
            self.repo_root / "memory" / "bank" / "private" / "gameplay_events.ndjson"
        )
        self.event_file.parent.mkdir(parents=True, exist_ok=True)

        self.proc_pid: int | None = None
        self.returncode: int | None = None
        self.master_fd: int | None = None
        self.buffer: deque[str] = deque(maxlen=2000)
        self.running = False
        self._reader_thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._last_error: str | None = None
        self._resolved_command: list[str] | None = None
        self._last_depth = 1
        self.state = "stopped"
        self.retries = 0
        self.last_transition_at = self._now_iso()

    def _transition(self, state: str, *, error: str | None = None) -> None:
        self.state = state
        self.last_transition_at = self._now_iso()
        if error:
            self._last_error = error

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _resolve_command(self) -> list[str]:
        env_cmd = get_dynamic_config(self.env_cmd_var, "").strip()
        if env_cmd:
            return shlex.split(env_cmd)

        for candidate in self.command_candidates:
            path = shutil.which(candidate)
            if path:
                return [path]

        raise RuntimeError(
            f"No upstream runtime found for {self.adapter_id}. Set {self.env_cmd_var} or install one of: "
            + ", ".join(self.command_candidates)
        )

    def _probe_pid_alive(self, pid: int | None) -> bool:
        if not pid:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _spawn_once(self, cmd: list[str], proc_env: dict[str, str]) -> tuple[int, int]:
        pid, master_fd = pty.fork()
        if pid == 0:
            os.chdir(str(self.repo_root))
            try:
                os.execvpe(cmd[0], cmd, proc_env)
            except Exception:
                os._exit(127)
        return pid, master_fd

    def _attempt_start(self, cmd: list[str]) -> bool:
        proc_env = os.environ.copy()
        proc_env.setdefault("TERM", "xterm-256color")
        proc_env.setdefault("LINES", "30")
        proc_env.setdefault("COLUMNS", "100")
        pid, master_fd = self._spawn_once(cmd, proc_env)
        self.master_fd = master_fd
        self.proc_pid = pid
        self.returncode = None
        self.running = True

        # Small startup probe: detect immediate crash and trigger retry path.
        time.sleep(0.05)
        if not self._probe_pid_alive(pid):
            self.running = False
            try:
                waited_pid, status = os.waitpid(pid, os.WNOHANG)
                if waited_pid == pid:
                    if os.WIFEXITED(status):
                        self.returncode = os.WEXITSTATUS(status)
                    elif os.WIFSIGNALED(status):
                        self.returncode = -os.WTERMSIG(status)
            except Exception:
                pass
            if self.master_fd is not None:
                try:
                    os.close(self.master_fd)
                except Exception:
                    pass
                self.master_fd = None
            self.proc_pid = None
            return False

        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()
        return True

    def start(self) -> None:
        if self.running and self._probe_pid_alive(self.proc_pid):
            return
        self._transition("starting")
        self.retries = 0
        cmd = self._resolve_command() + self.startup_args
        self._resolved_command = cmd

        attempts = 0
        while True:
            attempts += 1
            try:
                if self._attempt_start(cmd):
                    self.retries = max(0, attempts - 1)
                    self._transition("running")
                    self._emit_event(
                        "TOYBOX_RUNTIME_STARTED",
                        {"command": cmd, "retries": self.retries},
                    )
                    return
            except Exception as exc:
                self._last_error = str(exc)
                self.running = False
            if attempts - 1 >= self.max_start_retries:
                self.retries = max(0, attempts - 1)
                self._transition("failed", error=self._last_error or "startup failed")
                self._emit_event(
                    "TOYBOX_RUNTIME_FAILED",
                    {
                        "command": cmd,
                        "retries": self.retries,
                        "error": self._last_error or "startup failed",
                    },
                )
                raise RuntimeError(
                    self._last_error or f"Failed to start adapter {self.adapter_id}"
                )

            self.retries = max(0, attempts)
            backoff_idx = min(
                self.retries - 1, max(0, len(self.retry_backoff_seconds) - 1)
            )
            delay = (
                float(self.retry_backoff_seconds[backoff_idx])
                if self.retry_backoff_seconds
                else 1.0
            )
            time.sleep(max(0.0, delay))

    def stop(self) -> None:
        if not self.running and not self._probe_pid_alive(self.proc_pid):
            self._transition("stopped")
            return
        self._transition("stopping")
        try:
            if self.proc_pid:
                os.kill(self.proc_pid, signal.SIGTERM)
                for _ in range(30):
                    waited_pid, status = os.waitpid(self.proc_pid, os.WNOHANG)
                    if waited_pid == self.proc_pid:
                        if os.WIFEXITED(status):
                            self.returncode = os.WEXITSTATUS(status)
                        elif os.WIFSIGNALED(status):
                            self.returncode = -os.WTERMSIG(status)
                        break
                    time.sleep(0.1)
        except Exception:
            if self.proc_pid:
                try:
                    os.kill(self.proc_pid, signal.SIGKILL)
                except Exception:
                    pass
        finally:
            self.running = False
            if self.master_fd is not None:
                try:
                    os.close(self.master_fd)
                except Exception:
                    pass
                self.master_fd = None
            self.proc_pid = None
            self._transition("stopped")
            self._emit_event("TOYBOX_RUNTIME_STOPPED", {})

    def send(self, text: str) -> None:
        if not self.running or self.master_fd is None:
            raise RuntimeError("Runtime is not running")
        payload = text
        if not payload.endswith("\n"):
            payload += "\n"
        os.write(self.master_fd, payload.encode("utf-8", errors="ignore"))

    def _reader_loop(self) -> None:
        line_buf = ""
        while self.running and self.master_fd is not None:
            try:
                chunk = os.read(self.master_fd, 4096)
                if not chunk:
                    time.sleep(0.05)
                    continue
                text = chunk.decode("utf-8", errors="ignore")
                with self._lock:
                    self.buffer.append(text)
                line_buf += text
                while "\n" in line_buf:
                    line, line_buf = line_buf.split("\n", 1)
                    self._handle_line(line.rstrip("\r"))
            except OSError:
                break
            except Exception as exc:
                self._last_error = str(exc)
                break
        self.running = False
        if self.proc_pid:
            try:
                waited_pid, status = os.waitpid(self.proc_pid, os.WNOHANG)
                if waited_pid == self.proc_pid:
                    if os.WIFEXITED(status):
                        self.returncode = os.WEXITSTATUS(status)
                    elif os.WIFSIGNALED(status):
                        self.returncode = -os.WTERMSIG(status)
            except Exception:
                pass
        if self.state in {"running", "starting", "degraded"}:
            if self.returncode is not None and int(self.returncode) != 0:
                self._transition(
                    "failed",
                    error=self._last_error or f"runtime exited rc={self.returncode}",
                )
            else:
                self._transition("stopped")

    def _handle_line(self, line: str) -> None:
        if not line:
            return
        depth_match = re.search(r"\blevel\s+(\d+)\b", line, re.IGNORECASE)
        if depth_match:
            self._last_depth = max(self._last_depth, int(depth_match.group(1)))

        if self.parse_fn:
            events = self.parse_fn(line) or []
            for event in events:
                payload = dict(event.get("payload") or {})
                payload.setdefault("depth", self._last_depth)
                self._emit_event(str(event.get("type", "TOYBOX_OUTPUT_EVENT")), payload)

    def _emit_event(self, event_type: str, payload: dict[str, Any]) -> None:
        row = {
            "ts": self._now_iso(),
            "source": f"toybox:{self.adapter_id}",
            "type": event_type,
            "payload": payload,
        }
        with self.event_file.open("a", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                fh.write(json.dumps(row) + "\n")
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    def _health_level(self) -> str:
        if self.state == "running" and self._probe_pid_alive(self.proc_pid):
            return "ok"
        if self.state in {"starting", "stopping", "degraded"}:
            return "warn"
        return "fail"

    def status(self) -> dict[str, Any]:
        alive = self._probe_pid_alive(self.proc_pid)
        return {
            "adapter_id": self.adapter_id,
            "state": self.state,
            "running": bool(self.running and alive),
            "pid": self.proc_pid,
            "retries": self.retries,
            "returncode": self.returncode,
            "command": self._resolved_command,
            "last_error": self._last_error,
            "last_transition_at": self.last_transition_at,
            "health": self._health_level(),
            "depth": self._last_depth,
        }

    def health(self) -> dict[str, Any]:
        row = self.status()
        return {"ok": row.get("health") == "ok", **row}

    def output_text(self, tail_chars: int = 16000) -> str:
        with self._lock:
            text = "".join(self.buffer)
        return text[-tail_chars:]


def create_app(adapter: PTYAdapter) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        adapter.start()
        try:
            yield
        finally:
            adapter.stop()

    app = FastAPI(title=f"TOYBOX {adapter.adapter_id}", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return adapter.health()

    @app.get("/status")
    def status() -> dict[str, Any]:
        return adapter.status()

    @app.get("/output")
    def output() -> dict[str, Any]:
        return {"output": adapter.output_text()}

    @app.post("/input")
    def input_text(req: InputRequest) -> dict[str, Any]:
        try:
            adapter.send(req.text)
            return {"ok": True}
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))

    @app.get("/")
    def index() -> str:
        return (
            "<!doctype html><html><head><title>TOYBOX</title></head><body>"
            "<h1>TOYBOX Runtime</h1>"
            "<p>Use /output and /input endpoints for PTY interaction.</p>"
            "</body></html>"
        )

    return app
