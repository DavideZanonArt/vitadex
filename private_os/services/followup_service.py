from __future__ import annotations

import builtins
import sqlite3
from datetime import date

from private_os.core.db import get, list_rows, upsert
from private_os.core.logging import audit
from private_os.core.time import now_iso
from private_os.models.followup import FollowupRecord


class FollowupService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, followup: FollowupRecord) -> FollowupRecord:
        upsert(self.conn, "followups", followup.id, followup.model_dump())
        audit(
            self.conn,
            "followup.created",
            followup.title,
            task_id=followup.task_id,
            payload=followup.model_dump(),
        )
        return followup

    def get(self, followup_id: str) -> FollowupRecord:
        row = get(self.conn, "followups", followup_id)
        if not row:
            raise KeyError(followup_id)
        return FollowupRecord(**row)

    def list(self, status: str | None = None) -> builtins.list[FollowupRecord]:
        followups = [FollowupRecord(**row) for row in list_rows(self.conn, "followups")]
        return [f for f in followups if f.status == status] if status else followups

    def due(self) -> builtins.list[FollowupRecord]:
        today = date.today().isoformat()
        return [f for f in self.list("pending") if f.due_date <= today]

    def complete(self, followup_id: str) -> FollowupRecord:
        followup = self.get(followup_id)
        followup.status = "done"
        followup.updated_at = now_iso()
        upsert(self.conn, "followups", followup.id, followup.model_dump())
        audit(self.conn, "followup.completed", followup.title, task_id=followup.task_id)
        return followup

    def cancel(self, followup_id: str) -> FollowupRecord:
        followup = self.get(followup_id)
        followup.status = "cancelled"
        followup.updated_at = now_iso()
        upsert(self.conn, "followups", followup.id, followup.model_dump())
        audit(self.conn, "followup.cancelled", followup.title, task_id=followup.task_id)
        return followup
