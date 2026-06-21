from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class DecisionMatrixSkill(Skill):
    manifest = SkillManifest(
        id="decision_matrix",
        name="Matrice decisionale",
        description="Trasforma opzioni disordinate in raccomandazione chiara.",
        area="decisions",
        trigger_examples=["decisione", "scegliere", "matrice", "confronto", "raccomandazione"],
        outputs=["criteri", "scoring pesato", "raccomandazione", "rischi", "decision log"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["opzioni", "pesi criteri"],
            risks=["Falsa precisione se i dati sono incompleti."],
            recommended_strategy="Usare pesi espliciti e separare fatti, assunzioni e preferenze.",
            steps=[
                PlanStep(title="Criteri", description="Definire pesi."),
                PlanStep(title="Scoring", description="Calcolare punteggi."),
            ],
            required_skills=["decision_matrix"],
            required_tools=["FileSystemTool"],
            approval_points=[],
            expected_outputs=["matrice", "raccomandazione"],
            final_recommendation_placeholder="Raccomandazione con alternativa di backup e rischi.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/tables/decision-matrix.md"}
