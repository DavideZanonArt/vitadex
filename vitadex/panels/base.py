from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from vitadex.core.ids import new_id
from vitadex.core.time import now_iso

PanelType = Literal["task", "note", "list", "decision", "approval", "followup", "dashboard", "output"]


class Panel(BaseModel):
    id: str = Field(default_factory=lambda: new_id("panel"))
    title: str
    type: PanelType
    content: dict[str, Any] | str
    related_task_id: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    status: str = "active"
    tags: list[str] = Field(default_factory=list)
    source: str = "vitadex"
