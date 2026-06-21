from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from private_os.core.ids import new_id
from private_os.core.time import now_iso


class FollowupRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("fu"))
    task_id: str
    title: str
    due_date: str
    cadence: str | None = None
    status: Literal["pending", "done", "cancelled"] = "pending"
    trigger_condition: str
    action: str
    approval_required: bool = False
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
