from __future__ import annotations

from typing import Any

from vitadex.models.action import ActionRequest
from vitadex.tools.base import ApprovalToken, Tool


class TelegramTool(Tool):
    name = "TelegramTool"

    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        self.check(action, approval)
        return {"mode": "mock-notification", "sent": approval is not None, "payload": action.payload}
