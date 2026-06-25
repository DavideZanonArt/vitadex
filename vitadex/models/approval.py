from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from vitadex.core.ids import new_id
from vitadex.core.time import now_iso


class ApprovalRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("appr"))
    task_id: str
    action_type: str
    title: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict)
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"
    sensitivity_level: Literal["public", "personal", "sensitive", "highly_sensitive"] = "personal"
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    status: Literal["pending", "approved", "rejected", "expired"] = "pending"
    approved_at: str | None = None
    rejected_at: str | None = None
    user_notes: str | None = None
