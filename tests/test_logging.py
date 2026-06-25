from __future__ import annotations

from vitadex.core.logging import audit
from vitadex.models.approval import ApprovalRecord
from vitadex.models.task import TaskRecord
from vitadex.services.approval_service import ApprovalService
from vitadex.services.audit_service import AuditService
from vitadex.services.planning_service import PlanningService


def test_logging_of_planning_and_approval(conn, memory, tasks):
    task = tasks.create(
        TaskRecord(title="Find a 6-month rental in Munich", area="home", goal="Find a home")
    )
    PlanningService(conn, memory, tasks).create_plan(task.id)
    ApprovalService(conn).create(
        ApprovalRecord(
            task_id=task.id, action_type="send_message", title="Send", description="Email"
        )
    )
    events = [log["event_type"] for log in AuditService(conn).list()]
    assert "planning.created" in events
    assert "approval.created" in events


def test_audit_logs_keep_latest_insert_first_with_same_second_timestamps(conn):
    first = audit(conn, "system.first", "First event")
    second = audit(conn, "system.second", "Second event")

    logs = AuditService(conn).list()

    assert [log["id"] for log in logs[:2]] == [second["id"], first["id"]]
