from __future__ import annotations

from typing import Any

from private_os.models.plan import PlanRecord, PlanStep
from private_os.models.skill import SkillManifest
from private_os.models.task import TaskRecord
from private_os.skills.base import Skill, SkillContext


class DashboardDigestSkill(Skill):
    manifest = SkillManifest(
        id="dashboard_digest",
        name="Digest private ops",
        description="Crea sintesi giornaliera o settimanale delle operazioni private.",
        area="private_projects",
        trigger_examples=["dashboard", "digest", "riepilogo", "settimana"],
        outputs=["task urgenti", "waiting", "approvazioni", "decisioni", "azioni suggerite"],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title],
            recommended_strategy="Riassumere stato operativo e prossime azioni.",
            steps=[
                PlanStep(title="Raccolta", description="Leggere task, follow-up, approvazioni."),
                PlanStep(title="Sintesi", description="Produrre digest pratico."),
            ],
            required_skills=["dashboard_digest"],
            required_tools=["FileSystemTool"],
            expected_outputs=["digest"],
            final_recommendation_placeholder="Concentrarsi su blocchi, approvazioni e prossima azione.",
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {"dry_run": dry_run, "digest": "Usare private-os dashboard per stato aggiornato."}
