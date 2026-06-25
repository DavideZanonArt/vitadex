from __future__ import annotations

import sqlite3
from typing import Any

from vitadex.core.logging import audit
from vitadex.models.action import ActionRequest
from vitadex.permissions.policy import APPROVAL_REQUIRED_ACTIONS
from vitadex.services.approval_service import ApprovalService
from vitadex.tools.base import ApprovalToken, Tool


class ActionGateway:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.approvals = ApprovalService(conn)

    def execute(
        self,
        tool: Tool,
        action: ActionRequest,
        *,
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        token = self._approval_token(action, approval_id)
        try:
            result = tool.run(action, approval=token)
        except PermissionError as exc:
            audit(
                self.conn,
                "action.rejected",
                str(exc),
                task_id=action.task_id,
                payload=action.model_dump(),
                risk_level="high",
            )
            raise
        audit(
            self.conn,
            "action.executed",
            f"Azione eseguita tramite {tool.name}: {action.action_type}",
            task_id=action.task_id,
            payload={"action": action.model_dump(), "result": result, "approval_id": approval_id},
        )
        return result

    def _approval_token(
        self, action: ActionRequest, approval_id: str | None
    ) -> ApprovalToken | None:
        if action.action_type not in APPROVAL_REQUIRED_ACTIONS:
            return None
        if not approval_id:
            return None
        approval = self.approvals.get(approval_id)
        action_id = approval.payload.get("action_id")
        if (
            approval.status == "approved"
            and approval.task_id == action.task_id
            and approval.action_type == action.action_type
            and action_id == action.id
        ):
            return ApprovalToken(approval_id=approval.id, action_id=action.id)
        return None
