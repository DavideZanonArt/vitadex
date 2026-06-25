from __future__ import annotations

from typing import Any, cast

from vitadex.costs.budget import CostPolicy, TaskCostProfile, TokenBudget

DEFAULT_BUDGETS: dict[TaskCostProfile, dict[str, object]] = {
    "trivial": {
        "max_turns": 2,
        "max_file_reads": 3,
        "max_subagents": 0,
        "max_tool_calls": 5,
        "max_output_lines": 40,
        "max_context_files": 3,
        "reasoning_level": "low",
        "require_plan_first": False,
    },
    "normal": {
        "max_turns": 5,
        "max_file_reads": 10,
        "max_subagents": 0,
        "max_tool_calls": 15,
        "max_output_lines": 80,
        "max_context_files": 8,
        "reasoning_level": "medium",
        "require_plan_first": False,
    },
    "complex": {
        "max_turns": 8,
        "max_file_reads": 20,
        "max_subagents": 1,
        "max_tool_calls": 30,
        "max_output_lines": 120,
        "max_context_files": 12,
        "reasoning_level": "medium_or_high",
        "allow_high_reasoning": True,
        "require_plan_first": True,
    },
    "expensive": {
        "max_turns": 12,
        "max_file_reads": 35,
        "max_subagents": 2,
        "max_tool_calls": 50,
        "max_output_lines": 160,
        "max_context_files": 20,
        "reasoning_level": "high",
        "allow_high_reasoning": True,
        "require_plan_first": True,
        "require_compaction": True,
    },
}


def default_policy() -> CostPolicy:
    return CostPolicy()


def budget_for_profile(task_id: str, profile: TaskCostProfile) -> TokenBudget:
    return TokenBudget(task_id=task_id, **cast(dict[str, Any], DEFAULT_BUDGETS[profile]))
