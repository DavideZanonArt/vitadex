from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from vitadex.core.ids import new_id
from vitadex.core.time import now_iso


class LogRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("log"))
    timestamp: str = Field(default_factory=now_iso)
    event_type: str
    task_id: str | None = None
    actor: str = "system"
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    risk_level: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
