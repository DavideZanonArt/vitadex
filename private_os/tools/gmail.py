from __future__ import annotations

from typing import Any

from private_os.models.action import ActionRequest
from private_os.tools.base import ApprovalToken, Tool


class GmailTool(Tool):
    name = "GmailTool"

    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        self.check(action, approval)
        if action.action_type == "draft_external":
            return {"mode": "draft", "draft": action.payload, "sent": False}
        return {"mode": "approval-gated", "sent": approval is not None, "payload": action.payload}
