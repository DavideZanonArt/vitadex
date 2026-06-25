from __future__ import annotations

from typing import Any

from vitadex.models.plan import PlanRecord, PlanStep
from vitadex.models.skill import SkillManifest
from vitadex.models.task import TaskRecord
from vitadex.skills.base import Skill, SkillContext


class TravelPlanningSkill(Skill):
    manifest = SkillManifest(
        id="travel_planning",
        name="Travel planning",
        description="Organize personal travel with practical constraints.",
        area="travel",
        trigger_examples=["travel", "hotel", "itinerary", "transport"],
        outputs=[
            "itinerary",
            "lodging criteria",
            "transport",
            "budget",
            "workability check",
            "recommendation",
        ],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title, task.description],
            assumptions=[
                "Prefer options that are verifiable and cancellable when the data is incomplete."
            ],
            missing_info=["dates", "budget", "transport preferences"],
            risks=["Non-refundable bookings, poor Wi-Fi, missing parking."],
            recommended_strategy="Build comparable options and keep bookings behind approval.",
            steps=[
                PlanStep(
                    title="Travel criteria",
                    description="Define dates, transport, lodging, and remote-work needs.",
                ),
                PlanStep(title="Itinerary", description="Prepare a day-by-day plan."),
            ],
            required_skills=["travel_planning", "decision_matrix"],
            required_tools=["BrowserTool(mock)", "CalendarTool(draft)"],
            approval_points=[
                {
                    "action_type": "create_calendar_event",
                    "title": "Create travel calendar event",
                    "description": "Create the event only after approval.",
                }
            ],
            expected_outputs=["travel checklist", "budget", "recommendation"],
            final_recommendation_placeholder="Choose the most robust option across cost, logistics, and flexibility.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "template": "templates/tables/decision-matrix.md",
            "checklist": "templates/reviews/weekly-private-review.md",
        }
