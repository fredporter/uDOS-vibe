from __future__ import annotations

from core.services.background_service_manager import WizardProcessManager, WizardServiceStatus


def test_ensure_running_starts_process_when_wizard_is_down(monkeypatch, tmp_path) -> None:
    manager = WizardProcessManager(repo_root=tmp_path)
    state: dict[str, bool] = {"started": False}

    monkeypatch.setattr(
        manager,
        "status",
        lambda **_kwargs: WizardServiceStatus(
            base_url="http://127.0.0.1:8765",
            running=False,
            connected=False,
            pid=None,
            message="wizard not running",
            health={},
        ),
    )
    monkeypatch.setattr(
        manager,
        "_start_process",
        lambda: state.__setitem__("started", True) or 111,
    )
    probes = iter(((False, {}), (True, {"status": "ok"})))
    monkeypatch.setattr(manager, "_health", lambda *_args, **_kwargs: next(probes))
    monkeypatch.setattr(manager, "_read_pid", lambda: 111)

    status = manager.ensure_running(base_url="http://127.0.0.1:8765", wait_seconds=1)

    assert state["started"]
    assert status.connected
    assert status.running
    assert status.pid == 111


def test_status_marks_process_running_when_pid_exists_but_health_offline(monkeypatch, tmp_path) -> None:
    manager = WizardProcessManager(repo_root=tmp_path)
    manager.pid_file.write_text("123\n", encoding="utf-8")
    monkeypatch.setattr(manager, "_health", lambda *_args, **_kwargs: (False, {}))
    monkeypatch.setattr("core.services.background_service_manager.WizardProcessManager._pid_alive", staticmethod(lambda _pid: True))

    status = manager.status(base_url="http://127.0.0.1:8765")

    assert status.running
    assert not status.connected
    assert status.pid == 123
