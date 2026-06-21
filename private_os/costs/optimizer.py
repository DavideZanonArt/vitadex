from __future__ import annotations

from collections import Counter

from private_os.costs.budget import BudgetDecision, TokenBudget, UsageLog
from private_os.costs.policy import default_policy


class CostOptimizer:
    def evaluate_subagent(self, budget: TokenBudget, requested_subagents: int = 1) -> BudgetDecision:
        if requested_subagents > budget.max_subagents:
            return BudgetDecision(
                allowed=False,
                reason="Subagent bloccati dal budget della task.",
                suggested_actions=["Usa un solo agente principale o aumenta il profilo costi."],
            )
        return BudgetDecision(allowed=True, reason="Subagent dentro budget.")

    def cap_output(self, text: str, max_lines: int) -> str:
        lines = text.splitlines()
        if len(lines) <= max_lines:
            return text
        return "\n".join([*lines[:max_lines], "[Output troncato dal budget]"])

    def optimize(self, budget: TokenBudget, usage_logs: list[UsageLog]) -> BudgetDecision:
        policy = default_policy()
        suggestions: list[str] = []
        warnings: list[str] = []
        repeated = Counter(log.prompt_fingerprint for log in usage_logs if log.prompt_fingerprint)
        if any(count >= policy.suggest_skill_after_repeated_prompts for count in repeated.values()):
            suggestions.append("Estrai una skill: prompt simili si stanno ripetendo.")
        if len(usage_logs) >= policy.suggest_agents_update_after_repeated_instructions:
            suggestions.append("Valuta aggiornamento AGENTS.md: istruzioni operative ripetute.")
        if sum(log.turns for log in usage_logs) >= policy.suggest_compaction_after_turns:
            suggestions.append("Compatta il contesto prima di continuare.")
        if budget.require_plan_first:
            warnings.append("Questa task richiede un piano prima dell'esecuzione.")
        if budget.require_compaction:
            warnings.append("Questa task richiede compaction se la sessione si allunga.")
        return BudgetDecision(
            allowed=True,
            reason="Budget valutato.",
            warnings=warnings,
            suggested_actions=suggestions or ["Nessuna ottimizzazione urgente."],
        )
