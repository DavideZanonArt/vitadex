from __future__ import annotations

from vitadex.models.task import TaskRecord
from vitadex.services.skill_service import SkillService


def test_asset_reconciliation_plan_keeps_weak_matches_unresolved():
    skill = SkillService().get("asset_reconciliation")
    task = TaskRecord(
        title="Map repositories to domains",
        area="private_projects",
        goal="Build a conservative asset reconciliation plan",
    )

    plan = skill.plan(task, {})

    assert "asset_reconciliation" in plan.required_skills
    assert any("weak matches" in risk or "weak" in risk.lower() for risk in plan.risks)
    assert any(step.output == "missing-link queue" for step in plan.steps)
    assert plan.approval_points[0]["action_type"] == "write_file"


def test_asset_reconciliation_execute_returns_confidence_rules():
    skill = SkillService().get("asset_reconciliation")
    task = TaskRecord(
        title="Map repositories to domains",
        area="private_projects",
        goal="Build a conservative asset reconciliation plan",
    )
    plan = skill.plan(task, {})

    result = skill.execute(task, plan, {}, dry_run=True)

    assert result["dry_run"] is True
    assert "github_repository" in result["asset_kinds"]
    assert result["link_confidence_rules"]["candidate"].startswith("strong name similarity")
