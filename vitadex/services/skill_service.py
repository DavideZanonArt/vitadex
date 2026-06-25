from __future__ import annotations

from vitadex.models.skill import SkillManifest
from vitadex.models.task import TaskRecord
from vitadex.skills import ALL_SKILLS
from vitadex.skills.base import Skill, SkillContext


class SkillService:
    def __init__(self, skills: list[Skill] | None = None):
        self.skills = skills or ALL_SKILLS

    def list(self) -> list[SkillManifest]:
        return [skill.manifest for skill in self.skills]

    def get(self, skill_id: str) -> Skill:
        for skill in self.skills:
            if skill.manifest.id == skill_id:
                return skill
        raise KeyError(skill_id)

    def match(self, task: TaskRecord, context: SkillContext | None = None) -> Skill:
        context = context or SkillContext()
        ranked = sorted(
            ((skill.can_handle(task, context), skill) for skill in self.skills),
            key=lambda item: item[0],
            reverse=True,
        )
        if ranked[0][0] <= 0:
            return self.get("decision_matrix")
        return ranked[0][1]
