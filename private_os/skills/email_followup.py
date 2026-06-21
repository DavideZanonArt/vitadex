from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class EmailFollowupSkill(Skill):
    manifest = SkillManifest(
        id="email_followup",
        name="Email follow-up",
        description="Track expected emails and prepare follow-ups.",
        area="communication",
        trigger_examples=["follow-up", "followup", "reply", "email"],
        outputs=["cadence", "follow-up draft", "waiting status", "closure criteria"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["recipient", "date of the first send"],
            risks=["Repeated messages or messages sent without context."],
            recommended_strategy="Prepare the cadence and drafts; sending remains approval-gated.",
            steps=[
                PlanStep(title="Cadence", description="Define 3/7/14 days."),
                PlanStep(title="Draft", description="Prepare the follow-up.", requires_approval=True),
            ],
            required_skills=["email_followup"],
            required_tools=["GmailTool(draft)"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Send follow-up",
                    "description": "Send the follow-up after approval.",
                }
            ],
            expected_outputs=["draft", "follow-up"],
            final_recommendation_placeholder="Close if there is no reply after 14 days or if it is not worth pushing further.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "cadence": ["3 days", "7 days", "14 days"],
            "template": "templates/emails/followup-en.md",
        }
