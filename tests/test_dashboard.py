from __future__ import annotations

from vitadex.models.task import TaskRecord
from vitadex.services.dashboard_service import DashboardService


def test_dashboard_output(conn, tasks):
    tasks.create(
        TaskRecord(
            title="Find a 6-month rental in Munich",
            area="home",
            goal="Find a home",
            status="active",
        )
    )
    output = DashboardService(conn).render()
    assert "VITADEX DASHBOARD" in output
    assert "Find a 6-month rental" in output
