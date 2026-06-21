from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from private_os.core.ids import new_id
from private_os.core.time import now_iso

TaskCostProfile = Literal["trivial", "normal", "complex", "expensive"]
ReasoningLevel = Literal["low", "medium", "medium_or_high", "high"]


class TokenBudget(BaseModel):
    task_id: str
    max_turns: int
    max_file_reads: int
    max_subagents: int
    max_tool_calls: int
    max_output_lines: int
    max_context_files: int = 5
    reasoning_level: ReasoningLevel
    allow_high_reasoning: bool = False
    allow_fast_mode: bool = False
    require_plan_first: bool = False
    require_compaction: bool = False
    stop_on_budget_exceeded: bool = True


class CostPolicy(BaseModel):
    default_profile: TaskCostProfile = "normal"
    warn_before_expensive: bool = True
    prefer_local_mock_adapters: bool = True
    suggest_skill_after_repeated_prompts: int = 3
    suggest_agents_update_after_repeated_instructions: int = 3
    suggest_compaction_after_turns: int = 8


class UsageEstimate(BaseModel):
    task_id: str
    profile: TaskCostProfile
    estimated_tool_calls: int = 0
    estimated_file_reads: int = 0
    estimated_output_lines: int = 0
    estimated_subagents: int = 0
    warnings: list[str] = Field(default_factory=list)


class UsageLog(BaseModel):
    id: str = Field(default_factory=lambda: new_id("usage"))
    task_id: str
    turns: int = 0
    file_reads: int = 0
    subagents: int = 0
    tool_calls: int = 0
    output_lines: int = 0
    context_files: int = 0
    estimated: bool = False
    prompt_fingerprint: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


class BudgetDecision(BaseModel):
    allowed: bool
    reason: str
    warnings: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
