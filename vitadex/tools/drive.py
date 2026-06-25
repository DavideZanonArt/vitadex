from __future__ import annotations

from typing import Any

from vitadex.models.action import ActionRequest
from vitadex.tools.base import ApprovalToken, Tool


class DriveTool(Tool):
    name = "DriveTool"

    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        self.check(action, approval)
        return {"mode": "mock-local", "uploaded": False, "payload": action.payload}
