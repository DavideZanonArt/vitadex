from __future__ import annotations

import pytest

from vitadex.models.action import ActionRequest
from vitadex.models.approval import ApprovalRecord
from vitadex.services.action_gateway import ActionGateway
from vitadex.services.approval_service import ApprovalService
from vitadex.tools.gmail import GmailTool


def test_gateway_rejects_external_action_without_approved_matching_approval(conn):
    gateway = ActionGateway(conn)
    action = ActionRequest(
        id="act_send_email",
        task_id="task_1",
        action_type="send_message",
        title="Send email",
        payload={"to": "landlord@example.com"},
    )

    with pytest.raises(PermissionError):
        gateway.execute(GmailTool(), action)

    pending = ApprovalService(conn).create(
        ApprovalRecord(
            task_id="task_1",
            action_type="send_message",
            title="Send email",
            description="Test",
            payload={"action_id": action.id},
        )
    )
    with pytest.raises(PermissionError):
        gateway.execute(GmailTool(), action, approval_id=pending.id)


def test_gateway_executes_external_action_only_with_approved_matching_approval(conn):
    gateway = ActionGateway(conn)
    approvals = ApprovalService(conn)
    action = ActionRequest(
        id="act_send_email",
        task_id="task_1",
        action_type="send_message",
        title="Send email",
        payload={"to": "landlord@example.com"},
    )
    approval = approvals.create(
        ApprovalRecord(
            task_id="task_1",
            action_type="send_message",
            title="Send email",
            description="Test",
            payload={"action_id": action.id},
        )
    )
    approvals.approve(approval.id)

    result = gateway.execute(GmailTool(), action, approval_id=approval.id)

    assert result["sent"] is True


def test_tool_does_not_accept_boolean_as_approval_bypass():
    action = ActionRequest(
        id="act_send_email",
        task_id="task_1",
        action_type="send_message",
        title="Send email",
    )
    with pytest.raises(PermissionError):
        GmailTool().run(action, approval=True)  # type: ignore[arg-type]
