from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class DashboardDigestSkill(Skill):
    manifest = SkillManifest(
        id="dashboard_digest",
        name="Private ops digest",
        description="Create a daily or weekly summary of private operations.",
        area="private_projects",
        trigger_examples=["dashboard", "digest", "summary", "week"],
        outputs=["urgent tasks", "waiting", "approvals", "decisions", "suggested actions"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            recommended_strategy="Summarize the operational state and next actions.",
            steps=[
                PlanStep(title="Collect", description="Read tasks, follow-ups, and approvals."),
                PlanStep(title="Summarize", description="Produce a practical digest."),
            ],
            required_skills=["dashboard_digest"],
            required_tools=["FileSystemTool"],
            expected_outputs=["digest"],
            final_recommendation_placeholder="Focus on blockers, approvals, and the next action.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "digest": "Use private-os dashboard for the latest state."}
