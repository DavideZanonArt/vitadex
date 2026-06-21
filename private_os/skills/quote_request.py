from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class QuoteRequestSkill(Skill):
    manifest = SkillManifest(
        id="quote_request",
        name="Quote request",
        description="Prepare quote requests and compare suppliers.",
        area="bureaucracy",
        trigger_examples=["quote", "supplier", "vendor", "insurance"],
        outputs=[
            "supplier outline",
            "message template",
            "follow-up",
            "comparison matrix",
            "recommendation",
        ],
        required_tools=["GmailTool(draft)", "FileSystemTool"],
        approval_requirements=["Sending requests to suppliers"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title, task.description],
            assumptions=["The request stays as a draft; nothing is sent without approval."],
            missing_info=["supplier list", "financial criteria", "decision deadline"],
            risks=["Sharing personal data and getting poorly comparable terms."],
            recommended_strategy="Standardize the request and compare quotes using identical criteria.",
            steps=[
                PlanStep(title="Criteria", description="Define what to ask for and the constraints."),
                PlanStep(title="Suppliers", description="Prepare the supplier list."),
                PlanStep(
                    title="Draft",
                    description="Create the quote request email.",
                    requires_approval=True,
                    autonomy_level="A3",
                ),
            ],
            required_skills=["quote_request", "decision_matrix", "email_followup"],
            required_tools=["GmailTool(draft)", "FileSystemTool"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Send quote request",
                    "description": "Send the email to the selected suppliers.",
                }
            ],
            expected_outputs=["request template", "comparison matrix", "recommendation"],
            final_recommendation_placeholder="Recommend the supplier with the best balance of price, risk, and quality.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "template": "templates/emails/quote-request-en.md",
            "matrix": "templates/tables/supplier-comparison.md",
        }
