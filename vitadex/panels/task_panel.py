from __future__ import annotations

from vitadex.models.task import TaskRecord
from vitadex.panels.base import Panel


def task_panel(task: TaskRecord) -> Panel:
    return Panel(
        title=task.title,
        type="task",
        related_task_id=task.id,
        content={
            "goal": task.goal,
            "status": task.status,
            "constraints": task.constraints,
            "assumptions": task.assumptions,
            "next_actions": task.next_actions,
            "approval_required": task.approval_required,
        },
        tags=[task.area, task.status],
        source="task",
    )
