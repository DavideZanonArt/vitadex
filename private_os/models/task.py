from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from private_os.core.ids import new_id
from private_os.core.time import now_iso


class TaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("task"))
    title: str
    description: str = ""
    area: str
    status: Literal[
        "inbox",
        "active",
        "waiting",
        "needs_approval",
        "blocked",
        "done",
        "archived",
        "cancelled",
    ] = "inbox"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    autonomy_level: Literal["A0", "A1", "A2", "A3", "A4", "A5"] = "A2"
    goal: str
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    waiting_on: str | None = None
    due_date: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    completed_at: str | None = None
    relevant_memories: list[str] = Field(default_factory=list)
    selected_skill: str | None = None
    plan_id: str | None = None
    approval_required: bool = False
    outputs: dict[str, Any] = Field(default_factory=dict)
    decision_log: list[str] = Field(default_factory=list)
    followups: list[str] = Field(default_factory=list)
    cost_profile: Literal["trivial", "normal", "complex", "expensive"] | None = None
    token_budget: dict[str, Any] | None = None
    codex_thread: dict[str, Any] | None = None
