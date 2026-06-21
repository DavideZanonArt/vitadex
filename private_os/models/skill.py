from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SkillManifest(BaseModel):
    id: str
    name: str
    description: str
    area: str
    trigger_examples: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    optional_inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    max_autonomy_level: str = "A3"
    required_tools: list[str] = Field(default_factory=list)
    approval_requirements: list[str] = Field(default_factory=list)
    risk_level: str = "medium"
    runbook: list[str] = Field(default_factory=list)
    test_examples: list[dict[str, Any]] = Field(default_factory=list)
