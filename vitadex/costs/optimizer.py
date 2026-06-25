from __future__ import annotations

from collections import Counter

from vitadex.costs.budget import BudgetDecision, TokenBudget, UsageLog
from vitadex.costs.policy import default_policy


class CostOptimizer:
    def evaluate_subagent(self, budget: TokenBudget, requested_subagents: int = 1) -> BudgetDecision:
        if requested_subagents > budget.max_subagents:
            return BudgetDecision(
                allowed=False,
                reason="Subagents are blocked by the task budget.",
                suggested_actions=["Use a single main agent or increase the cost profile."],
            )
        return BudgetDecision(allowed=True, reason="Subagents are within budget.")

    def cap_output(self, text: str, max_lines: int) -> str:
        lines = text.splitlines()
        if len(lines) <= max_lines:
            return text
        return "\n".join([*lines[:max_lines], "[Output truncated by budget]"])

    def optimize(self, budget: TokenBudget, usage_logs: list[UsageLog]) -> BudgetDecision:
        policy = default_policy()
        suggestions: list[str] = []
        warnings: list[str] = []
        repeated = Counter(log.prompt_fingerprint for log in usage_logs if log.prompt_fingerprint)
        if any(count >= policy.suggest_skill_after_repeated_prompts for count in repeated.values()):
            suggestions.append("Extract a skill: similar prompts are repeating.")
        if len(usage_logs) >= policy.suggest_agents_update_after_repeated_instructions:
            suggestions.append("Consider updating AGENTS.md: operational instructions are repeating.")
        if sum(log.turns for log in usage_logs) >= policy.suggest_compaction_after_turns:
            suggestions.append("Compact the context before continuing.")
        if budget.require_plan_first:
            warnings.append("This task requires a plan before execution.")
        if budget.require_compaction:
            warnings.append("This task requires compaction if the session grows long.")
        return BudgetDecision(
            allowed=True,
            reason="Budget evaluated.",
            warnings=warnings,
            suggested_actions=suggestions or ["No urgent optimization needed."],
        )
