from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class TravelPlanningSkill(Skill):
    manifest = SkillManifest(
        id="travel_planning",
        name="Pianificazione viaggi",
        description="Organizza viaggi personali con vincoli pratici.",
        area="travel",
        trigger_examples=["viaggio", "hotel", "itinerario", "trasporto"],
        outputs=[
            "itinerario",
            "criteri alloggio",
            "trasporti",
            "budget",
            "workability check",
            "raccomandazione",
        ],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title, task.description],
            assumptions=[
                "Preferire opzioni verificabili e cancellabili se i dati sono incompleti."
            ],
            missing_info=["date", "budget", "preferenze trasporto"],
            risks=["Prenotazioni non rimborsabili, Wi-Fi insufficiente, parcheggio mancante."],
            recommended_strategy="Costruire opzioni confrontabili e bloccare le prenotazioni dietro approvazione.",
            steps=[
                PlanStep(
                    title="Criteri viaggio",
                    description="Definire date, trasporto, alloggio, lavoro remoto.",
                ),
                PlanStep(title="Itinerario", description="Preparare piano giorno per giorno."),
            ],
            required_skills=["travel_planning", "decision_matrix"],
            required_tools=["BrowserTool(mock)", "CalendarTool(draft)"],
            approval_points=[
                {
                    "action_type": "create_calendar_event",
                    "title": "Creazione evento calendario viaggio",
                    "description": "Creare evento solo dopo approvazione.",
                }
            ],
            expected_outputs=["checklist viaggio", "budget", "raccomandazione"],
            final_recommendation_placeholder="Scegliere l'opzione più robusta su costi, logistica e flessibilità.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "template": "templates/tables/decision-matrix.md",
            "checklist": "templates/reviews/weekly-private-review.md",
        }
