from __future__ import annotations

from vitadex.models.task import TaskRecord
from vitadex.services.skill_service import SkillService


def test_skill_matching_for_housing_task():
    task = TaskRecord(
        title="Find a 6-month rental in Munich", area="home", goal="Find temporary housing"
    )
    skill = SkillService().match(task)
    assert skill.manifest.id == "housing_search"


def test_skill_matching_for_asset_reconciliation_task():
    task = TaskRecord(
        title="Reconcile GitHub repositories with domains and Vercel projects",
        area="private_projects",
        goal="Map portfolio assets without forcing weak matches",
    )
    skill = SkillService().match(task)
    assert skill.manifest.id == "asset_reconciliation"
