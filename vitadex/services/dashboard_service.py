from __future__ import annotations

import sqlite3

from vitadex.services.approval_service import ApprovalService
from vitadex.services.followup_service import FollowupService
from vitadex.services.task_service import TaskService


class DashboardService:
    def __init__(self, conn: sqlite3.Connection):
        self.tasks = TaskService(conn)
        self.approvals = ApprovalService(conn)
        self.followups = FollowupService(conn)

    def render(self) -> str:
        tasks = self.tasks.list()
        active = [t for t in tasks if t.status == "active"]
        waiting = [t for t in tasks if t.status == "waiting"]
        blocked = [t for t in tasks if t.status == "blocked"]
        approvals = self.approvals.list("pending")
        due = self.followups.due()
        decisions = [t for t in tasks if t.missing_info or t.status == "needs_approval"]
        recent_done = [t for t in tasks if t.decision_log][:5]
        lines = [
            "VITADEX DASHBOARD",
            "",
            "Today",
            f"- {len(active)} active tasks",
            f"- {len(approvals)} pending approvals",
            f"- {len(due)} overdue follow-ups",
            f"- {len(decisions)} required decisions",
            "",
            "Priority tasks",
        ]
        priority = [
            t for t in tasks if t.status in {"active", "needs_approval", "waiting", "blocked"}
        ][:5]
        lines.extend(
            [f"- {t.title} ({t.status})" for t in priority]
            or ["- No priority tasks"]
        )
        lines.extend(["", "Suggested actions"])
        if approvals:
            lines.append("- Approve, edit, or reject the pending drafts")
        if due:
            lines.append("- Handle overdue follow-ups")
        if decisions:
            lines.append("- Complete the missing information in open tasks")
        if blocked:
            lines.append("- Unblock or archive blocked tasks")
        if not (approvals or due or decisions or blocked):
            lines.append("- No urgent actions")
        lines.extend(
            [
                "",
                "Waiting",
                *(
                    [f"- {t.title}: {t.waiting_on or 'waiting'}" for t in waiting]
                    or ["- None"]
                ),
            ]
        )
        lines.extend(["", "Blocked", *([f"- {t.title}" for t in blocked] or ["- None"])])
        lines.extend(
            [
                "",
                "Recent decisions",
                *([f"- {t.title}: {t.decision_log[-1]}" for t in recent_done] or ["- None"]),
            ]
        )
        return "\n".join(lines)
