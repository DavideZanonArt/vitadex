from __future__ import annotations

from typing import Any

from vitadex.models.plan import PlanRecord, PlanStep
from vitadex.models.skill import SkillManifest
from vitadex.models.task import TaskRecord
from vitadex.skills.base import Skill, SkillContext


class ComplaintManagementSkill(Skill):
    manifest = SkillManifest(
        id="complaint_management",
        name="Complaint management",
        description="Prepare factual complaints while avoiding defamatory or legally risky language.",
        area="bureaucracy",
        trigger_examples=["complaint", "refund", "dispute", "issue"],
        outputs=["factual timeline", "neutral draft", "escalation plan", "evidence checklist"],
        risk_level="high",
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["verifiable timeline", "evidence", "requested outcome"],
            risks=["Unproven accusations, aggressive tone, unintended legal commitments."],
            recommended_strategy="Use only verifiable facts, a clear request, and cautious escalation.",
            steps=[
                PlanStep(title="Timeline", description="Collect dates and evidence."),
                PlanStep(
                    title="Neutral draft",
                    description="Write a factual complaint.",
                    requires_approval=True,
                ),
            ],
            required_skills=["complaint_management"],
            required_tools=["GmailTool(draft)", "FileSystemTool"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Send complaint",
                    "description": "Send only after reviewing the content.",
                }
            ],
            expected_outputs=["timeline", "draft", "escalation"],
            final_recommendation_placeholder="Send only if the facts and request are clear.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/emails/complaint-neutral-en.md"}
