from __future__ import annotations

from vitadex.panels.base import Panel


def dashboard_panel(active_tasks: int, pending_approvals: int, pending_followups: int) -> Panel:
    return Panel(
        title="VitaDex Dashboard",
        type="dashboard",
        content={
            "active_tasks": active_tasks,
            "pending_approvals": pending_approvals,
            "pending_followups": pending_followups,
        },
        tags=["dashboard"],
        source="dashboard",
    )
