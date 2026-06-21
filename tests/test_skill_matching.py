from __future__ import annotations

from private_os.models.task import TaskRecord
from private_os.services.skill_service import SkillService


def test_skill_matching_for_housing_task():
    task = TaskRecord(
        title="Cercare affitto 6 mesi a Monaco", area="home", goal="Trovare casa temporanea"
    )
    skill = SkillService().match(task)
    assert skill.manifest.id == "housing_search"
