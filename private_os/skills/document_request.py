from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class DocumentRequestSkill(Skill):
    manifest = SkillManifest(
        id="document_request",
        name="Document request",
        description="Organize document requests, checklists, and tracking.",
        area="bureaucracy",
        trigger_examples=["document", "documents", "certificate", "request"],
        outputs=["document checklist", "request email", "tracker", "follow-up"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["recipient organization or person", "deadline", "required format"],
            risks=["Sensitive documents: do not upload or send them without explicit approval."],
            recommended_strategy="Create a checklist and request draft; every send remains manually approved.",
            steps=[
                PlanStep(title="Checklist", description="List the documents and their status."),
                PlanStep(
                    title="Request draft", description="Prepare the email.", requires_approval=True
                ),
            ],
            required_skills=["document_request", "email_followup"],
            required_tools=["GmailTool(draft)", "DriveTool(mock_local)"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Send document request",
                    "description": "Send the request after verifying the data.",
                }
            ],
            expected_outputs=["checklist", "tracker", "draft"],
            final_recommendation_placeholder="Proceed only after the recipient and deadline are confirmed.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/emails/document-request-en.md"}
