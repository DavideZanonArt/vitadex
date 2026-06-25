from __future__ import annotations

import sqlite3

from vitadex.core.db import get, list_rows, upsert
from vitadex.core.logging import audit
from vitadex.core.time import now_iso
from vitadex.models.approval import ApprovalRecord


class ApprovalService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, approval: ApprovalRecord) -> ApprovalRecord:
        upsert(self.conn, "approvals", approval.id, approval.model_dump())
        audit(
            self.conn,
            "approval.created",
            approval.title,
            task_id=approval.task_id,
            payload=approval.model_dump(),
            risk_level=approval.risk_level,
        )
        return approval

    def get(self, approval_id: str) -> ApprovalRecord:
        row = get(self.conn, "approvals", approval_id)
        if not row:
            raise KeyError(approval_id)
        return ApprovalRecord(**row)

    def list(self, status: str | None = None) -> list[ApprovalRecord]:
        approvals = [ApprovalRecord(**row) for row in list_rows(self.conn, "approvals")]
        return [a for a in approvals if a.status == status] if status else approvals

    def approve(self, approval_id: str, notes: str | None = None) -> ApprovalRecord:
        approval = self.get(approval_id)
        approval.status = "approved"
        approval.approved_at = now_iso()
        approval.updated_at = now_iso()
        approval.user_notes = notes
        upsert(self.conn, "approvals", approval.id, approval.model_dump())
        audit(
            self.conn,
            "approval.approved",
            approval.title,
            task_id=approval.task_id,
            payload={"notes": notes},
            risk_level=approval.risk_level,
        )
        return approval

    def reject(self, approval_id: str, notes: str | None = None) -> ApprovalRecord:
        approval = self.get(approval_id)
        approval.status = "rejected"
        approval.rejected_at = now_iso()
        approval.updated_at = now_iso()
        approval.user_notes = notes
        upsert(self.conn, "approvals", approval.id, approval.model_dump())
        audit(
            self.conn,
            "approval.rejected",
            approval.title,
            task_id=approval.task_id,
            payload={"notes": notes},
            risk_level=approval.risk_level,
        )
        return approval
