from __future__ import annotations

from typing import Any

from vitadex.models.action import ActionRequest
from vitadex.tools.base import ApprovalToken, Tool


class BrowserTool(Tool):
    name = "BrowserTool"

    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        self.check(action, approval)
        return {
            "mode": "mock/search-plan",
            "message": "Real browser access is disabled in safe mode.",
            "payload": action.payload,
        }
