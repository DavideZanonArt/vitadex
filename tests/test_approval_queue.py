from __future__ import annotations

from vitadex.models.approval import ApprovalRecord
from vitadex.services.approval_service import ApprovalService


def test_approval_queue(conn):
    service = ApprovalService(conn)
    approval = service.create(
        ApprovalRecord(
            task_id="task_1", action_type="send_message", title="Invio email", description="Test"
        )
    )
    assert service.list("pending")[0].id == approval.id
    assert service.approve(approval.id).status == "approved"
    assert service.reject(approval.id).status == "rejected"
