from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class EmailFollowupSkill(Skill):
    manifest = SkillManifest(
        id="email_followup",
        name="Follow-up email",
        description="Traccia email attese e prepara follow-up.",
        area="communication",
        trigger_examples=["follow-up", "followup", "risposta", "email"],
        outputs=["cadenza", "bozza follow-up", "stato waiting", "criteri chiusura"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["destinatario", "data primo invio"],
            risks=["Messaggi ripetuti o inviati senza contesto."],
            recommended_strategy="Preparare cadenza e bozze, invio solo approvato.",
            steps=[
                PlanStep(title="Cadenza", description="Definire 3/7/14 giorni."),
                PlanStep(title="Bozza", description="Preparare follow-up.", requires_approval=True),
            ],
            required_skills=["email_followup"],
            required_tools=["GmailTool(draft)"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Invio follow-up",
                    "description": "Inviare follow-up dopo approvazione.",
                }
            ],
            expected_outputs=["bozza", "follow-up"],
            final_recommendation_placeholder="Chiudere se nessuna risposta dopo 14 giorni o se non conviene insistere.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "cadence": ["3 giorni", "7 giorni", "14 giorni"],
            "template": "templates/emails/followup-it.md",
        }
