from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from private_os.cli import app
from private_os.models.approval import ApprovalRecord
from private_os.models.followup import FollowupRecord
from private_os.models.task import TaskRecord
from private_os.panels.renderer import PanelRenderer
from private_os.services.approval_service import ApprovalService
from private_os.services.followup_service import FollowupService
from private_os.services.panel_service import PanelService


def test_panel_created_from_task(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Cercare affitto", area="home", goal="Trovare casa"))
    panel = PanelService(conn, root).from_task(task.id)

    assert panel.type == "task"
    assert panel.related_task_id == task.id
    assert (root / "workspace" / "panels" / f"{panel.id}.md").exists()


def test_dashboard_panel_includes_approvals_and_followups(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Casa Monaco", area="home", goal="Trovare casa", status="active"))
    ApprovalService(conn).create(
        ApprovalRecord(task_id=task.id, action_type="send_message", title="Invio email", description="Bozza")
    )
    FollowupService(conn).create(
        FollowupRecord(task_id=task.id, title="Follow-up landlord", due_date="2026-06-24", trigger_condition="no reply", action="draft")
    )

    panel = PanelService(conn, root).dashboard()

    assert panel.content["active_tasks"] == 1
    assert panel.content["pending_approvals"] == 1
    assert panel.content["pending_followups"] == 1


def test_panel_rendering_works(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Decisione casa", area="home", goal="Scegliere casa"))
    panel = PanelService(conn, root).from_task(task.id)
    markdown = PanelRenderer().markdown(panel)
    json_payload = PanelRenderer().json(panel)

    assert "# Decisione casa" in markdown
    assert '"type": "task"' in json_payload


def test_local_serve_command_can_initialize(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["serve"],
        env={
            "PRIVATE_OS_ROOT": str(tmp_path),
            "PRIVATE_OS_DB_PATH": str(tmp_path / "data" / "private_os.sqlite"),
            "PRIVATE_OS_IGNORE_CONSTITUTION": "true",
        },
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "workspace" / "index.html").exists()
