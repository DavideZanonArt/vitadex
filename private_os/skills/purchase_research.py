from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class PurchaseResearchSkill(Skill):
    manifest = SkillManifest(
        id="purchase_research",
        name="Purchase research",
        description="Research and compare important personal purchases.",
        area="finance",
        trigger_examples=["buy", "purchase", "product", "compare"],
        outputs=[
            "criteria",
            "comparison table",
            "pros and cons",
            "risk checks",
            "recommendation",
        ],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["budget", "must-have features", "purchase timing"],
            risks=["Scams, weak warranty, unclear total cost."],
            recommended_strategy="Compare options and keep purchase or payment outside automation.",
            steps=[
                PlanStep(title="Criteria", description="Define criteria and weights."),
                PlanStep(title="Comparison", description="Prepare the options table."),
            ],
            required_skills=["purchase_research", "decision_matrix"],
            required_tools=["BrowserTool(mock)"],
            approval_points=[],
            expected_outputs=["matrix", "recommendation"],
            final_recommendation_placeholder="Suggest the purchase only as a recommendation and never execute payment.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "risk_checks": ["verified seller", "warranty", "return policy", "total price"],
        }
