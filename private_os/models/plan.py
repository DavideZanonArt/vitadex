from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from private_os.core.ids import new_id
from private_os.core.time import now_iso


class PlanStep(BaseModel):
    id: str = Field(default_factory=lambda: new_id("step"))
    title: str
    description: str
    autonomy_level: str = "A2"
    requires_approval: bool = False
    tool: str | None = None
    output: str | None = None


class PlanRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("plan"))
    task_id: str
    objective: str
    known_context: list[str] = Field(default_factory=list)
    relevant_memories: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_strategy: str
    steps: list[PlanStep] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    approval_points: list[dict[str, Any]] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    followups: list[dict[str, Any]] = Field(default_factory=list)
    final_recommendation_placeholder: str
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
