from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class QuoteRequestSkill(Skill):
    manifest = SkillManifest(
        id="quote_request",
        name="Richiesta preventivi",
        description="Prepara richieste preventivo e confronto fornitori.",
        area="bureaucracy",
        trigger_examples=["preventivo", "quote", "fornitore", "assicurazione"],
        outputs=[
            "schema fornitori",
            "template messaggio",
            "follow-up",
            "matrice confronto",
            "raccomandazione",
        ],
        required_tools=["GmailTool(draft)", "FileSystemTool"],
        approval_requirements=["Invio richieste a fornitori"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title, task.description],
            assumptions=["Richiesta gestita in bozza; nessun invio senza approvazione."],
            missing_info=["lista fornitori", "criteri economici", "scadenza decisione"],
            risks=["Condivisione dati personali e condizioni poco comparabili."],
            recommended_strategy="Standardizzare la richiesta e confrontare preventivi su criteri identici.",
            steps=[
                PlanStep(title="Criteri", description="Definire cosa chiedere e vincoli."),
                PlanStep(title="Fornitori", description="Preparare lista fornitori."),
                PlanStep(
                    title="Bozza",
                    description="Creare email richiesta preventivo.",
                    requires_approval=True,
                    autonomy_level="A3",
                ),
            ],
            required_skills=["quote_request", "decision_matrix", "email_followup"],
            required_tools=["GmailTool(draft)", "FileSystemTool"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Invio richiesta preventivo",
                    "description": "Inviare email ai fornitori selezionati.",
                }
            ],
            expected_outputs=["template richiesta", "matrice confronto", "raccomandazione"],
            final_recommendation_placeholder="Raccomandare il fornitore con miglior equilibrio prezzo/rischio/qualità.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "template": "templates/emails/quote-request-it.md",
            "matrix": "templates/tables/supplier-comparison.md",
        }
