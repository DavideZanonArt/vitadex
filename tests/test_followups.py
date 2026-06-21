from __future__ import annotations

from datetime import date

from private_os.models.followup import FollowupRecord
from private_os.services.followup_service import FollowupService


def test_followup_creation_due_complete(conn):
    service = FollowupService(conn)
    followup = service.create(
        FollowupRecord(
            task_id="task_1",
            title="Ricontattare",
            due_date=date.today().isoformat(),
            trigger_condition="no reply",
            action="draft",
        )
    )
    assert service.due()[0].id == followup.id
    assert service.complete(followup.id).status == "done"
