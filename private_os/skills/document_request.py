from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class DocumentRequestSkill(Skill):
    manifest = SkillManifest(
        id="document_request",
        name="Richiesta documenti",
        description="Organizza richieste, checklist e tracking documenti.",
        area="bureaucracy",
        trigger_examples=["documento", "documenti", "certificato", "richiedere"],
        outputs=["checklist documenti", "email richiesta", "tracker", "follow-up"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["ente/persona destinataria", "scadenza", "formato richiesto"],
            risks=["Documenti sensibili: non caricare o inviare senza approvazione esplicita."],
            recommended_strategy="Creare checklist e bozza richiesta; ogni invio resta approvato manualmente.",
            steps=[
                PlanStep(title="Checklist", description="Elencare documenti e stato."),
                PlanStep(
                    title="Bozza richiesta", description="Preparare email.", requires_approval=True
                ),
            ],
            required_skills=["document_request", "email_followup"],
            required_tools=["GmailTool(draft)", "DriveTool(mock_local)"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Invio richiesta documenti",
                    "description": "Inviare richiesta dopo verifica dati.",
                }
            ],
            expected_outputs=["checklist", "tracker", "bozza"],
            final_recommendation_placeholder="Procedere solo con destinatario e scadenza confermati.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/emails/document-request-it.md"}
