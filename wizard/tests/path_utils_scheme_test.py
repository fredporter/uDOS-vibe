from wizard.services import path_utils


def test_logs_dir_defaults_to_memory_logs(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(path_utils, "_load_wizard_config", lambda: {})
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)

    logs_dir = path_utils.get_logs_dir()

    assert logs_dir == tmp_path / "memory" / "logs"
    assert logs_dir.is_dir()


def test_logs_dir_ignores_config_and_env_override_in_strict_mode(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        path_utils,
        "_load_wizard_config",
        lambda: {"file_locations": {"logs_root": ".runtime/logs"}},
    )
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)
    monkeypatch.setenv("UDOS_LOGS_DIR", ".env-logs")

    logs_dir = path_utils.get_logs_dir()

    assert logs_dir == tmp_path / "memory" / "logs"
    assert logs_dir.is_dir()


def test_artifacts_and_test_run_paths_default_under_dot_artifacts(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(path_utils, "_load_wizard_config", lambda: {})
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)

    artifacts_dir = path_utils.get_artifacts_dir()
    test_runs_dir = path_utils.get_test_runs_dir()

    assert artifacts_dir == tmp_path / ".artifacts"
    assert test_runs_dir == tmp_path / ".artifacts" / "test-runs"
    assert artifacts_dir.is_dir()
    assert test_runs_dir.is_dir()
