from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class PurchaseResearchSkill(Skill):
    manifest = SkillManifest(
        id="purchase_research",
        name="Ricerca acquisti",
        description="Ricerca e confronta acquisti personali importanti.",
        area="finance",
        trigger_examples=["comprare", "acquisto", "prodotto", "confronta"],
        outputs=[
            "criteri",
            "tabella confronto",
            "pro/contro",
            "controlli rischio",
            "raccomandazione",
        ],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["budget", "must-have", "tempistica acquisto"],
            risks=["Scam, garanzia debole, costo totale non chiaro."],
            recommended_strategy="Confrontare opzioni e lasciare acquisto/pagamento fuori automazione.",
            steps=[
                PlanStep(title="Criteri", description="Definire criteri e pesi."),
                PlanStep(title="Confronto", description="Preparare tabella opzioni."),
            ],
            required_skills=["purchase_research", "decision_matrix"],
            required_tools=["BrowserTool(mock)"],
            approval_points=[],
            expected_outputs=["matrice", "raccomandazione"],
            final_recommendation_placeholder="Suggerire acquisto solo come raccomandazione, mai eseguire pagamento.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "risk_checks": ["venditore verificato", "garanzia", "reso", "prezzo totale"],
        }
