from __future__ import annotations

from pathlib import Path
from typing import Any

from private_os.models.action import ActionRequest
from private_os.tools.base import ApprovalToken, Tool


class FileSystemTool(Tool):
    name = "FileSystemTool"

    def __init__(self, root: Path):
        super().__init__()
        self.root = root.resolve()

    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        self.check(action, approval)
        target = (self.root / action.payload.get("path", "")).resolve()
        if not str(target).startswith(str(self.root)):
            raise PermissionError("FileSystemTool limitato alla cartella del progetto.")
        if action.action_type == "read":
            return {
                "path": str(target),
                "content": target.read_text(encoding="utf-8") if target.exists() else "",
            }
        if action.action_type == "write_local":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(action.payload.get("content", ""), encoding="utf-8")
            return {"path": str(target), "written": True}
        return {"path": str(target), "noop": True}
