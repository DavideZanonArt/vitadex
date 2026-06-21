from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class ComplaintManagementSkill(Skill):
    manifest = SkillManifest(
        id="complaint_management",
        name="Gestione reclami",
        description="Prepara reclami fattuali evitando linguaggio diffamatorio o legalmente rischioso.",
        area="bureaucracy",
        trigger_examples=["reclamo", "lamentela", "rimborso", "contestazione"],
        outputs=["timeline fattuale", "bozza neutra", "piano escalation", "checklist prove"],
        risk_level="high",
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            missing_info=["timeline verificabile", "prove", "risultato richiesto"],
            risks=["Accuse non provate, toni aggressivi, impegni legali non voluti."],
            recommended_strategy="Usare solo fatti verificabili, richiesta chiara e escalation prudente.",
            steps=[
                PlanStep(title="Timeline", description="Raccogliere date e prove."),
                PlanStep(
                    title="Bozza neutra",
                    description="Scrivere reclamo fattuale.",
                    requires_approval=True,
                ),
            ],
            required_skills=["complaint_management"],
            required_tools=["GmailTool(draft)", "FileSystemTool"],
            approval_points=[
                {
                    "action_type": "send_message",
                    "title": "Invio reclamo",
                    "description": "Invio solo dopo revisione del contenuto.",
                }
            ],
            expected_outputs=["timeline", "bozza", "escalation"],
            final_recommendation_placeholder="Inviare solo se fatti e richiesta sono chiari.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "template": "templates/emails/complaint-neutral-it.md"}
