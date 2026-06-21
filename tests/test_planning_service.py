from __future__ import annotations

from private_os.models.task import TaskRecord
from private_os.services.planning_service import PlanningService


def test_housing_task_plan_and_execute_dry_run(conn, memory, tasks):
    task = tasks.create(
        TaskRecord(
            title="Find a 6-month rental in Munich",
            area="home",
            goal="Find real options in Munich",
        )
    )
    service = PlanningService(conn, memory, tasks)
    plan = service.create_plan(task.id)
    assert "housing_search" in plan.required_skills
    result = service.execute(task.id, dry_run=True)
    assert result["dry_run"] is True
    assert tasks.get(task.id).approval_required is True
