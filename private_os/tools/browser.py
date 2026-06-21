from __future__ import annotations

from typing import Any

from private_os.models.action import ActionRequest
from private_os.tools.base import ApprovalToken, Tool


class BrowserTool(Tool):
    name = "BrowserTool"

    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        self.check(action, approval)
        return {
            "mode": "mock/search-plan",
            "message": "Browser reale disabilitato in safe mode.",
            "payload": action.payload,
        }
