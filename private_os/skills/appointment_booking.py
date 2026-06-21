from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class AppointmentBookingSkill(Skill):
    manifest = SkillManifest(
        id="appointment_booking",
        name="Appointment booking",
        description="Prepare appointment requests for personal services.",
        area="bureaucracy",
        trigger_examples=["appointment", "book", "visit", "office"],
        outputs=["message draft", "availability grid", "document checklist"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["available time slots", "required documents"],
            risks=["Sending personal data without review."],
            recommended_strategy="Prepare the request and availability, then approve sending.",
            steps=[
                PlanStep(title="Availability", description="Create an availability grid."),
                PlanStep(title="Draft", description="Prepare the request.", requires_approval=True),
            ],
            required_skills=["appointment_booking"],
            required_tools=["GmailTool(draft)", "CalendarTool(draft)"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Send appointment request",
                    "description": "Send the request after review.",
                }
            ],
            expected_outputs=["draft", "checklist"],
            final_recommendation_placeholder="Confirm the most convenient slot before sending.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/emails/appointment-request-en.md"}
