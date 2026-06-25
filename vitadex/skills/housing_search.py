from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from vitadex.models.plan import PlanRecord, PlanStep
from vitadex.models.skill import SkillManifest
from vitadex.models.task import TaskRecord
from vitadex.skills.base import Skill, SkillContext


class HousingSearchSkill(Skill):
    manifest = SkillManifest(
        id="housing_search",
        name="Housing search",
        description="Search, structure, compare, and manage temporary housing research.",
        area="home",
        trigger_examples=["rental", "munich", "house", "apartment", "housing"],
        required_inputs=["city", "expected duration"],
        optional_inputs=["budget", "neighborhoods", "parking", "Wi-Fi", "pets", "dates"],
        outputs=[
            "search strategy",
            "sources to review",
            "comparison table",
            "outreach draft",
            "follow-up",
            "shortlist",
            "recommendation",
        ],
        max_autonomy_level="A3",
        required_tools=["BrowserTool(mock)", "GmailTool(draft)", "FileSystemTool"],
        approval_requirements=["Send email", "Send documents", "Bookings or contracts"],
        risk_level="medium",
        runbook=[
            "Define minimum criteria.",
            "Prepare sources and queries.",
            "Build the comparison table.",
            "Prepare draft messages.",
            "Create follow-ups.",
            "Request approval before external contacts.",
        ],
        test_examples=[{"input": "Search for a 6-month rental in Munich", "matches": True}],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        memories = [m.id for m in context.get("memories", [])]
        missing = [
            "maximum monthly budget",
            "exact move-in and move-out dates",
            "number of people",
            "parking and Wi-Fi requirements",
        ]
        assumptions = [
            "Research is limited to private life and does not use business data or tools.",
            "Duration: 6 months.",
            "Area: Munich city center or at most 10 minutes by car from the center.",
            "No external contact is sent without approval.",
        ]
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title, task.description, *task.constraints],
            relevant_memories=memories,
            assumptions=assumptions,
            missing_info=missing,
            risks=[
                "Scams or unverified listings.",
                "Deposit requests before verification.",
                "Improper sharing of personal documents.",
                "Contract terms that are not suitable for 6 months.",
            ],
            recommended_strategy=(
                "Prepare a multi-source search in dry-run, compare only verifiable listings, "
                "create contact drafts, and ask the user for budget and dates before sending."
            ),
            steps=[
                PlanStep(
                    title="Define criteria",
                    description="Confirm budget, dates, people, neighborhoods, and constraints.",
                    output="criteria",
                ),
                PlanStep(
                    title="Prepare sources",
                    description="Set up the source list: rental portals, serviced apartments, agencies, verified groups.",
                    tool="BrowserTool(mock)",
                    output="sources",
                ),
                PlanStep(
                    title="Comparison table",
                    description="Create a schema for price, area, distance, furnished status, deposit, risks, and contact.",
                    output="table",
                ),
                PlanStep(
                    title="Outreach draft",
                    description="Prepare EN-only emails without attachments and without sensitive data.",
                    autonomy_level="A3",
                    requires_approval=True,
                    tool="GmailTool(draft)",
                    output="email draft",
                ),
                PlanStep(
                    title="Follow-up",
                    description="Create reminders at 3 and 7 days for landlord or agency replies.",
                    output="follow-up",
                ),
                PlanStep(
                    title="Recommendation",
                    description="Produce a shortlist and recommended choice with explicit risks.",
                    output="recommendation",
                ),
            ],
            required_skills=["housing_search", "decision_matrix", "email_followup"],
            required_tools=["BrowserTool(mock)", "GmailTool(draft)", "FileSystemTool"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Send Munich rental availability request",
                    "description": "Send the draft to landlords or agencies after user review.",
                    "risk_level": "medium",
                    "sensitivity_level": "personal",
                    "payload": {"template": "templates/emails/housing-request-en.md"},
                }
            ],
            expected_outputs=[
                "Search strategy",
                "Source schema",
                "Listing comparison table",
                "Email drafts",
                "Follow-up",
                "Shortlist",
                "Recommendation",
            ],
            followups=[
                {
                    "title": "Follow up with landlords or agencies with no reply",
                    "due_date": (datetime.now(UTC) + timedelta(days=3)).date().isoformat(),
                    "trigger_condition": "No reply after 3 days",
                    "action": "Prepare a follow-up email",
                    "approval_required": True,
                },
                {
                    "title": "Decide on budget and missing criteria",
                    "due_date": (datetime.now(UTC) + timedelta(days=1)).date().isoformat(),
                    "trigger_condition": "Budget or dates are missing",
                    "action": "Ask the user to confirm budget and dates",
                    "approval_required": False,
                },
            ],
            final_recommendation_placeholder="Recommend 2-3 options only after checking price, location, duration, risk, and terms.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "search_strategy": [
                "Query: furnished apartment Munich 6 months city center",
                "Query: temporary rental München 6 Monate möbliert Zentrum",
                "Sources: rental portals, serviced apartments, local agencies, relocation services, verified groups.",
            ],
            "comparison_columns": [
                "name",
                "url",
                "area",
                "drive_time_to_center_min",
                "monthly_price",
                "deposit",
                "furnished",
                "Wi-Fi",
                "parking",
                "minimum_duration",
                "required_documents",
                "risks",
                "next_action",
            ],
            "drafts": {
                "en": "I would like to ask whether the apartment is available for an approximately 6-month temporary rental...",
            },
            "recommendation_next": "Confirm budget and dates before sending requests.",
        }
