from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class AppointmentBookingSkill(Skill):
    manifest = SkillManifest(
        id="appointment_booking",
        name="Prenotazione appuntamenti",
        description="Prepara richieste appuntamento per servizi personali.",
        area="bureaucracy",
        trigger_examples=["appuntamento", "prenotare", "visita", "ufficio"],
        outputs=["bozza messaggio", "griglia disponibilità", "checklist documenti"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["disponibilità orarie", "documenti necessari"],
            risks=["Invio dati personali senza revisione."],
            recommended_strategy="Preparare richiesta e disponibilità, poi approvare invio.",
            steps=[
                PlanStep(title="Disponibilità", description="Creare griglia orari."),
                PlanStep(title="Bozza", description="Preparare richiesta.", requires_approval=True),
            ],
            required_skills=["appointment_booking"],
            required_tools=["GmailTool(draft)", "CalendarTool(draft)"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Invio richiesta appuntamento",
                    "description": "Inviare richiesta dopo revisione.",
                }
            ],
            expected_outputs=["bozza", "checklist"],
            final_recommendation_placeholder="Confermare slot più comodo prima dell'invio.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/emails/appointment-request-it.md"}
