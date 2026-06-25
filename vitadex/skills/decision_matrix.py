from __future__ import annotations

from typing import Any

from vitadex.models.plan import PlanRecord, PlanStep
from vitadex.models.skill import SkillManifest
from vitadex.models.task import TaskRecord
from vitadex.skills.base import Skill, SkillContext


class DecisionMatrixSkill(Skill):
    manifest = SkillManifest(
        id="decision_matrix",
        name="Decision matrix",
        description="Turn messy options into a clear recommendation.",
        area="decisions",
        trigger_examples=["decision", "choose", "matrix", "comparison", "recommendation"],
        outputs=["criteria", "weighted scoring", "recommendation", "risks", "decision log"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["options", "criteria weights"],
            risks=["False precision when the data is incomplete."],
            recommended_strategy="Use explicit weights and separate facts, assumptions, and preferences.",
            steps=[
                PlanStep(title="Criteria", description="Define the weights."),
                PlanStep(title="Scoring", description="Calculate the scores."),
            ],
            required_skills=["decision_matrix"],
            required_tools=["FileSystemTool"],
            approval_points=[],
            expected_outputs=["matrix", "recommendation"],
            final_recommendation_placeholder="Recommendation with a fallback option and clear risks.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/tables/decision-matrix.md"}
