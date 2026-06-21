from __future__ import annotations

import sqlite3

from private_os.services.approval_service import ApprovalService
from private_os.services.followup_service import FollowupService
from private_os.services.task_service import TaskService


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
            "PRIVATE OPS DASHBOARD",
            "",
            "Oggi",
            f"- {len(active)} task attive",
            f"- {len(approvals)} approvazioni in attesa",
            f"- {len(due)} follow-up scaduti",
            f"- {len(decisions)} decisioni richieste",
            "",
            "Task prioritarie",
        ]
        priority = [
            t for t in tasks if t.status in {"active", "needs_approval", "waiting", "blocked"}
        ][:5]
        lines.extend(
            [f"- {t.title} ({t.status})" for t in priority]
            or ["- Nessuna task prioritaria"]
        )
        lines.extend(["", "Azioni consigliate"])
        if approvals:
            lines.append("- Approva, modifica o rifiuta le bozze in attesa")
        if due:
            lines.append("- Gestisci i follow-up scaduti")
        if decisions:
            lines.append("- Completa le informazioni mancanti nelle task aperte")
        if blocked:
            lines.append("- Sblocca o archivia le task bloccate")
        if not (approvals or due or decisions or blocked):
            lines.append("- Nessuna azione urgente")
        lines.extend(
            [
                "",
                "Waiting",
                *(
                    [f"- {t.title}: {t.waiting_on or 'in attesa'}" for t in waiting]
                    or ["- Nessuna"]
                ),
            ]
        )
        lines.extend(["", "Bloccate", *([f"- {t.title}" for t in blocked] or ["- Nessuna"])])
        lines.extend(
            [
                "",
                "Decisioni recenti",
                *([f"- {t.title}: {t.decision_log[-1]}" for t in recent_done] or ["- Nessuna"]),
            ]
        )
        return "\n".join(lines)
