from __future__ import annotations

from vitadex.models.followup import FollowupRecord
from vitadex.panels.base import Panel


def followup_panel(followup: FollowupRecord) -> Panel:
    return Panel(
        title=followup.title,
        type="followup",
        related_task_id=followup.task_id,
        content=followup.model_dump(),
        tags=[followup.status],
        source="followup",
    )
