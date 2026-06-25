from __future__ import annotations

from vitadex.models.approval import ApprovalRecord
from vitadex.panels.base import Panel


def approval_panel(approval: ApprovalRecord) -> Panel:
    return Panel(
        title=approval.title,
        type="approval",
        related_task_id=approval.task_id,
        content=approval.model_dump(),
        tags=[approval.action_type, approval.status],
        source="approval",
    )
