from __future__ import annotations

from typing import Any

from private_os.models.action import ActionRequest
from private_os.tools.base import ApprovalToken, Tool


class CalendarTool(Tool):
    name = "CalendarTool"

    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        self.check(action, approval)
        return {"mode": "draft-event", "created": approval is not None, "payload": action.payload}
