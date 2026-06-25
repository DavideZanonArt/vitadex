from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vitadex.cli import app
from vitadex.integrations.codex_harness.adapter import CodexHarnessAdapter
from vitadex.integrations.codex_harness.config import CodexHarnessConfig
from vitadex.models.task import TaskRecord
from vitadex.services.audit_service import AuditService


def test_codex_disabled_fails_closed(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Test Codex", area="private_projects", goal="Run Codex"))
    adapter = CodexHarnessAdapter(conn, root, CodexHarnessConfig(enabled=False, mode="dry_run"))

    result = adapter.run_task(task.id, dry_run=False)

    assert result.status == "failed_closed"
    assert result.executed is False


def test_codex_dry_run_does_not_execute_external_actions(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Dry Codex", area="private_projects", goal="Prepare command"))
    adapter = CodexHarnessAdapter(
        conn, root, CodexHarnessConfig(enabled=True, mode="dry_run", denied_paths=[])
    )

    result = adapter.run_task(task.id, dry_run=True)

    assert result.status == "dry_run"
    assert result.executed is False
    assert "command" in result.payload


def test_task_can_be_bound_to_codex_thread(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Bind Codex", area="private_projects", goal="Bind"))
    adapter = CodexHarnessAdapter(
        conn, root, CodexHarnessConfig(enabled=True, mode="dry_run", denied_paths=[])
    )

    binding = adapter.bind_task(task.id)

    saved = tasks.get(task.id)
    assert binding.thread.id.startswith("codex_thread_")
    assert saved.codex_thread is not None


def test_codex_output_is_logged(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Log Codex", area="private_projects", goal="Log"))
    adapter = CodexHarnessAdapter(
        conn, root, CodexHarnessConfig(enabled=True, mode="dry_run", denied_paths=[])
    )

    adapter.run_task(task.id, dry_run=True)

    events = [log["event_type"] for log in AuditService(conn).list()]
    assert "codex.execution_result" in events
    assert "codex.output" in events


def test_denied_paths_are_blocked(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Blocked Codex", area="private_projects", goal="Block"))
    adapter = CodexHarnessAdapter(
        conn,
        root,
        CodexHarnessConfig(enabled=True, mode="dry_run", denied_paths=[str(root.resolve())]),
    )

    result = adapter.run_task(task.id, dry_run=True)

    assert result.status == "failed_closed"
    assert result.executed is False


def test_codex_cli_commands(tmp_path: Path):
    runner = CliRunner()
    env = {
        "VITADEX_ROOT": str(tmp_path),
        "VITADEX_DB_PATH": str(tmp_path / "data" / "vitadex.sqlite"),
        "VITADEX_IGNORE_CONSTITUTION": "true",
    }
    created = runner.invoke(
        app,
        [
            "task",
            "create",
            "--title",
            "Codex CLI",
            "--area",
            "private_projects",
            "--goal",
            "Test harness",
        ],
        env=env,
    )
    assert created.exit_code == 0, created.output
    task_id = created.output.split(":")[-1].strip()

    assert runner.invoke(app, ["codex", "status"], env=env).exit_code == 0
    assert "Codex thread" in runner.invoke(app, ["codex", "bind", task_id], env=env).output
    assert "failed_closed" in runner.invoke(app, ["codex", "run", task_id, "--dry-run"], env=env).output
    assert "codex_thread_" in runner.invoke(app, ["codex", "threads"], env=env).output
    assert "ownership_split" in runner.invoke(app, ["codex", "export-context", task_id], env=env).output
