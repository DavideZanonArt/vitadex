from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from vitadex.core.ids import new_id
from vitadex.core.time import now_iso

ActionType = Literal[
    "read",
    "write_local",
    "draft_external",
    "submit_external",
    "send_message",
    "create_calendar_event",
    "upload_document",
    "payment",
    "signature",
    "legal_commitment",
]


class ActionRequest(BaseModel):
    id: str = Field(default_factory=lambda: new_id("act"))
    task_id: str | None = None
    action_type: ActionType
    title: str
    payload: dict[str, Any] = Field(default_factory=dict)
    sensitivity_level: str = "personal"
    autonomy_level: str = "A2"
    created_at: str = Field(default_factory=now_iso)


class PermissionDecision(BaseModel):
    allowed: bool
    requires_approval: bool = False
    forbidden: bool = False
    reason: str
