from __future__ import annotations

from typer.testing import CliRunner

from vitadex.cli import app
from vitadex.constitution import Constitution
from vitadex.core.config import get_settings
from vitadex.models.action import ActionRequest
from vitadex.models.task import TaskRecord
from vitadex.permissions.evaluator import PermissionEvaluator
from vitadex.services.planning_service import PlanningService


def test_constitution_is_loaded():
    text = Constitution(__import__("pathlib").Path.cwd()).load()
    assert "VitaDex Constitution" in text
    assert "Forbidden Actions" in text


def test_missing_constitution_fails_safe(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["task", "list"],
        env={
            "VITADEX_ROOT": str(tmp_path),
            "VITADEX_DB_PATH": str(tmp_path / "data" / "vitadex.sqlite"),
        },
    )
    assert result.exit_code == 2
    assert "CONSTITUTION.md missing" in result.output


def test_local_constitution_override_is_preferred(tmp_path):
    (tmp_path / "CONSTITUTION.md").write_text("# Public Constitution\n\n## Identity\n", encoding="utf-8")
    state_root = tmp_path / "local-state"
    state_root.mkdir()
    (state_root / "CONSTITUTION.local.md").write_text("# Local Constitution\n\n## Identity\n", encoding="utf-8")

    text = Constitution(tmp_path, state_root).load()

    assert "Local Constitution" in text


def test_forbidden_action_blocked_because_of_constitution():
    decision = PermissionEvaluator().evaluate(
        ActionRequest(action_type="payment", title="Paga caparra")
    )
    assert decision.forbidden is True
    assert "CONSTITUTION.md §5" in decision.reason


def test_planner_cites_constitution_for_risky_actions(conn, memory, tasks):
    task = tasks.create(
        TaskRecord(title="Find a 6-month rental in Munich", area="home", goal="Find a home")
    )
    plan = PlanningService(conn, memory, tasks).create_plan(task.id)
    assert any("CONSTITUTION.md §5" in risk for risk in plan.risks)


def test_user_facing_style_follows_constitution():
    style = Constitution(__import__("pathlib").Path.cwd()).risky_action_context()
    assert any("English" in item for item in style)


def test_settings_support_separate_state_root(monkeypatch, tmp_path):
    state_root = tmp_path / "state"
    monkeypatch.setenv("VITADEX_ROOT", str(tmp_path))
    monkeypatch.setenv("VITADEX_STATE_ROOT", str(state_root))

    settings = get_settings()

    assert settings.root == tmp_path.resolve()
    assert settings.state_root == state_root.resolve()
    assert settings.memory_dir == (state_root / "memory").resolve()


def test_settings_load_env_local_file(monkeypatch, tmp_path):
    monkeypatch.delenv("VITADEX_STATE_ROOT", raising=False)
    monkeypatch.delenv("VITADEX_MEMORY_DIR", raising=False)
    (tmp_path / ".env.local").write_text(
        "VITADEX_STATE_ROOT=~/.vitadex-test\nVITADEX_MEMORY_DIR=~/.vitadex-test/memory\n",
        encoding="utf-8",
    )

    settings = get_settings(tmp_path)

    assert settings.state_root == (__import__("pathlib").Path("~/.vitadex-test").expanduser().resolve())
    assert settings.memory_dir == (__import__("pathlib").Path("~/.vitadex-test/memory").expanduser().resolve())
