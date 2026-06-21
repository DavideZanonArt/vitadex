from __future__ import annotations

from private_os.core.logging import audit
from private_os.models.approval import ApprovalRecord
from private_os.models.task import TaskRecord
from private_os.services.approval_service import ApprovalService
from private_os.services.audit_service import AuditService
from private_os.services.planning_service import PlanningService


def test_logging_of_planning_and_approval(conn, memory, tasks):
    task = tasks.create(
        TaskRecord(title="Cercare affitto 6 mesi a Monaco", area="home", goal="Trovare casa")
    )
    PlanningService(conn, memory, tasks).create_plan(task.id)
    ApprovalService(conn).create(
        ApprovalRecord(
            task_id=task.id, action_type="send_message", title="Invio", description="Email"
        )
    )
    events = [log["event_type"] for log in AuditService(conn).list()]
    assert "planning.created" in events
    assert "approval.created" in events


def test_audit_logs_keep_latest_insert_first_with_same_second_timestamps(conn):
    first = audit(conn, "system.first", "Primo evento")
    second = audit(conn, "system.second", "Secondo evento")

    logs = AuditService(conn).list()

    assert [log["id"] for log in logs[:2]] == [second["id"], first["id"]]
