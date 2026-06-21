from __future__ import annotations

import re
import sqlite3
from typing import Any

from private_os.core.logging import audit
from private_os.models.plan import PlanRecord
from private_os.models.task import TaskRecord
from private_os.services.approval_service import ApprovalService
from private_os.services.followup_service import FollowupService
from private_os.services.memory_service import MemoryService
from private_os.services.planning_service import PlanningService
from private_os.services.skill_service import SkillService
from private_os.services.task_service import TaskService


class AgentIntakeService:
    def __init__(self, conn: sqlite3.Connection, memory: MemoryService, tasks: TaskService):
        self.conn = conn
        self.memory = memory
        self.tasks = tasks
        self.planning = PlanningService(conn, memory, tasks)
        self.skills = SkillService()
        self.approvals = ApprovalService(conn)
        self.followups = FollowupService(conn)

    def intake(self, message: str) -> dict[str, Any]:
        parsed = self.parse_message(message)
        memories = self.memory.search(message)
        task = self.tasks.create(
            TaskRecord(
                title=parsed["title"],
                description=message,
                area=parsed["area"],
                priority=parsed["priority"],
                autonomy_level=parsed["autonomy_level"],
                goal=parsed["goal"],
                constraints=parsed["constraints"],
                missing_info=parsed["missing_info"],
            )
        )
        skill = self.skills.match(task)
        plan = self.planning.create_plan(task.id)
        execution = self.planning.execute(task.id, dry_run=True)
        refreshed_task = self.tasks.get(task.id)
        approvals = self.approvals.list("pending")
        task_approvals = [a for a in approvals if a.task_id == task.id]
        followups = [f for f in self.followups.list("pending") if f.task_id == task.id]
        payload = {
            "input_message": message,
            "task": refreshed_task.model_dump(),
            "selected_skill": skill.manifest.id,
            "relevant_memories": [m.model_dump() for m in memories],
            "plan": plan.model_dump(),
            "execution": execution,
            "approvals": [a.model_dump() for a in task_approvals],
            "followups": [f.model_dump() for f in followups],
            "markdown": self.render_markdown(
                message=message,
                task=refreshed_task,
                plan=plan,
                execution=execution,
                approvals=task_approvals,
                followups=followups,
                relevant_memory_count=len(memories),
            ),
        }
        audit(
            self.conn,
            "agent.intake.completed",
            f"Agent intake completed: {refreshed_task.title}",
            task_id=task.id,
            actor="agent",
            payload=payload,
        )
        return payload

    def parse_message(self, message: str) -> dict[str, Any]:
        normalized = message.strip()
        lower = normalized.lower()
        area = "private_projects"
        if any(term in lower for term in ["munich", "rental", "house", "apartment", "stay"]):
            area = "home"
        elif any(term in lower for term in ["travel", "hotel", "flight", "train"]):
            area = "travel"
        elif any(term in lower for term in ["document", "certificate", "bureaucracy"]):
            area = "bureaucracy"

        constraints: list[str] = []
        if "center" in lower:
            constraints.append("City center or an area close to the center.")
        distance_match = re.search(r"(\d+)\s*minut", lower)
        if distance_match:
            constraints.append(f"At most {distance_match.group(1)} minutes by car from the center.")
        duration_match = re.search(r"(\d+)\s*months?", lower)
        if duration_match:
            constraints.append(f"Expected duration: {duration_match.group(1)} months.")

        missing_info = ["maximum budget", "exact dates", "recipients to contact"]
        if area == "home":
            missing_info.extend(["number of people", "Wi-Fi and parking requirements"])

        return {
            "title": self._title_from_message(normalized),
            "area": area,
            "priority": "high" if any(term in lower for term in ["urgent", "asap"]) else "medium",
            "autonomy_level": "A3",
            "goal": normalized,
            "constraints": constraints,
            "missing_info": missing_info,
        }

    def render_markdown(
        self,
        *,
        message: str,
        task: TaskRecord,
        plan: PlanRecord,
        execution: dict[str, object],
        approvals: list[Any],
        followups: list[Any],
        relevant_memory_count: int,
    ) -> str:
        raw_drafts = execution.get("drafts")
        drafts = raw_drafts if isinstance(raw_drafts, dict) else {}
        raw_search_strategy = execution.get("search_strategy")
        search_strategy = raw_search_strategy if isinstance(raw_search_strategy, list) else []
        lines = [
            "*Private OS - intake completed*",
            "",
            f"*Message:* {message}",
            f"*Task created:* `{task.id}` - {task.title}",
            f"*Selected skill:* `{task.selected_skill}`",
            f"*Relevant memories:* {relevant_memory_count}",
            "",
            "*Execution plan*",
            *[f"- {step.title}: {step.description}" for step in plan.steps],
            "",
            "*Assumptions*",
            *[f"- {item}" for item in plan.assumptions],
            "",
            "*Missing information*",
            *[f"- {item}" for item in plan.missing_info],
            "",
            "*Dry-run execution*",
            *[f"- {item}" for item in search_strategy],
            "",
            "*Email drafts*",
        ]
        if drafts:
            lines.extend([f"- EN: {drafts.get('en', '')}"])
        else:
            lines.append("- No email draft generated.")
        lines.extend(
            [
                "",
                "*Email sending*",
                "- Not executed. Explicit approval is required.",
                "",
                "*Follow-up*",
                *[f"- `{f.id}` {f.due_date}: {f.title}" for f in followups],
                "",
                "*Approvals to confirm*",
                *[f"- `{a.id}` {a.action_type}: {a.title}" for a in approvals],
                "",
                "*Recommended next action*",
                f"- {execution.get('recommendation_next', plan.final_recommendation_placeholder)}",
            ]
        )
        return "\n".join(lines)

    def _title_from_message(self, message: str) -> str:
        cleaned = message.strip().rstrip(".")
        if len(cleaned) <= 70:
            return cleaned[0].upper() + cleaned[1:]
        return cleaned[:67].rstrip() + "..."
