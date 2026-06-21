from __future__ import annotations

import sqlite3

from private_os.constitution import Constitution, ConstitutionMissingError
from private_os.core.config import get_settings
from private_os.core.db import upsert
from private_os.core.logging import audit
from private_os.models.followup import FollowupRecord
from private_os.models.plan import PlanRecord
from private_os.services.approval_service import ApprovalService
from private_os.services.followup_service import FollowupService
from private_os.services.memory_service import MemoryService
from private_os.services.skill_service import SkillService
from private_os.services.task_service import TaskService
from private_os.skills.base import SkillContext


class PlanningService:
    def __init__(self, conn: sqlite3.Connection, memory: MemoryService, tasks: TaskService):
        self.conn = conn
        self.memory = memory
        self.tasks = tasks
        self.skills = SkillService()
        self.approvals = ApprovalService(conn)
        self.followups = FollowupService(conn)

    def create_plan(self, task_id: str) -> PlanRecord:
        task = self.tasks.get(task_id)
        memories = self.memory.search(f"{task.title} {task.goal} {task.area}")
        context = SkillContext(memories=memories)
        skill = self.skills.match(task, context)
        plan = skill.plan(task, context)
        settings = get_settings()
        try:
            plan.risks.extend(Constitution(settings.root, settings.state_root).risky_action_context())
        except ConstitutionMissingError:
            plan.risks.append("CONSTITUTION.md missing: constitutional risk, proceed only in safe mode.")
        upsert(self.conn, "plans", plan.id, plan.model_dump())
        for approval in skill.required_approvals(task, plan):
            self.approvals.create(approval)
        for data in plan.followups:
            self.followups.create(FollowupRecord(task_id=task.id, **data))
        task.selected_skill = skill.manifest.id
        task.plan_id = plan.id
        task.relevant_memories = [m.id for m in memories]
        task.assumptions = plan.assumptions
        task.missing_info = plan.missing_info
        task.next_actions = [step.title for step in plan.steps]
        task.approval_required = bool(plan.approval_points)
        task.status = "needs_approval" if task.approval_required else "active"
        self.tasks.save(task)
        audit(
            self.conn,
            "planning.created",
            f"Plan created with skill {skill.manifest.id}",
            task_id=task.id,
            payload=plan.model_dump(),
        )
        return plan

    def execute(self, task_id: str, dry_run: bool = True) -> dict[str, object]:
        task = self.tasks.get(task_id)
        if not task.plan_id:
            plan = self.create_plan(task_id)
        else:
            from private_os.core.db import get

            row = get(self.conn, "plans", task.plan_id)
            if not row:
                plan = self.create_plan(task_id)
            else:
                plan = PlanRecord(**row)
        skill = self.skills.get(task.selected_skill or plan.required_skills[0])
        result = skill.execute(task, plan, SkillContext(memories=[]), dry_run=dry_run)
        task.outputs.update(skill.produce_outputs(task, result))
        if dry_run:
            task.status = "needs_approval" if task.approval_required else "active"
        self.tasks.save(task)
        audit(
            self.conn,
            "skill.executed",
            f"Skill execution {skill.manifest.id} dry_run={dry_run}",
            task_id=task.id,
            payload=result,
        )
        return result
