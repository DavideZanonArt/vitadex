from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vitadex.cli import app
from vitadex.models.approval import ApprovalRecord
from vitadex.models.followup import FollowupRecord
from vitadex.models.task import TaskRecord
from vitadex.panels.renderer import PanelRenderer
from vitadex.services.approval_service import ApprovalService
from vitadex.services.followup_service import FollowupService
from vitadex.services.panel_service import PanelService


def test_panel_created_from_task(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Find a rental", area="home", goal="Find a home"))
    panel = PanelService(conn, root).from_task(task.id)

    assert panel.type == "task"
    assert panel.related_task_id == task.id
    assert (root / "workspace" / "panels" / f"{panel.id}.md").exists()


def test_dashboard_panel_includes_approvals_and_followups(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Munich housing", area="home", goal="Find a home", status="active"))
    ApprovalService(conn).create(
        ApprovalRecord(task_id=task.id, action_type="send_message", title="Send email", description="Draft")
    )
    FollowupService(conn).create(
        FollowupRecord(task_id=task.id, title="Follow-up landlord", due_date="2026-06-24", trigger_condition="no reply", action="draft")
    )

    panel = PanelService(conn, root).dashboard()

    assert panel.content["active_tasks"] == 1
    assert panel.content["pending_approvals"] == 1
    assert panel.content["pending_followups"] == 1


def test_panel_rendering_works(conn, tasks, root):
    task = tasks.create(TaskRecord(title="Housing decision", area="home", goal="Choose a home"))
    panel = PanelService(conn, root).from_task(task.id)
    markdown = PanelRenderer().markdown(panel)
    json_payload = PanelRenderer().json(panel)

    assert "# Housing decision" in markdown
    assert '"type": "task"' in json_payload


def test_local_serve_command_can_initialize(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["serve"],
        env={
            "VITADEX_ROOT": str(tmp_path),
            "VITADEX_DB_PATH": str(tmp_path / "data" / "vitadex.sqlite"),
            "VITADEX_IGNORE_CONSTITUTION": "true",
        },
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "workspace" / "index.html").exists()
