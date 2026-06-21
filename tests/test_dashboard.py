from __future__ import annotations

from private_os.models.task import TaskRecord
from private_os.services.dashboard_service import DashboardService


def test_dashboard_output(conn, tasks):
    tasks.create(
        TaskRecord(
            title="Cercare affitto 6 mesi a Monaco",
            area="home",
            goal="Trovare casa",
            status="active",
        )
    )
    output = DashboardService(conn).render()
    assert "PRIVATE OPS DASHBOARD" in output
    assert "Cercare affitto" in output
