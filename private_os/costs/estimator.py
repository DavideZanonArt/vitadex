from __future__ import annotations

from private_os.costs.budget import TaskCostProfile, UsageEstimate
from private_os.models.task import TaskRecord

TRIVIAL_TERMS = {"rinomina", "template", "classifica", "inspect", "piccolo", "nota"}
COMPLEX_TERMS = {"architettura", "permission", "sicurezza", "refactor", "integrazione"}
EXPENSIVE_TERMS = {"audit completo", "tutto il repository", "multi-agent", "browser", "grande refactor"}


class CostEstimator:
    def classify(self, task: TaskRecord) -> TaskCostProfile:
        text = f"{task.title} {task.description} {task.goal}".lower()
        if any(term in text for term in EXPENSIVE_TERMS):
            return "expensive"
        if any(term in text for term in COMPLEX_TERMS):
            return "complex"
        if any(term in text for term in TRIVIAL_TERMS):
            return "trivial"
        return "normal"

    def estimate(self, task: TaskRecord) -> UsageEstimate:
        profile = task.cost_profile or self.classify(task)
        base = {
            "trivial": (2, 1, 20, 0),
            "normal": (6, 4, 50, 0),
            "complex": (15, 12, 90, 1),
            "expensive": (25, 24, 140, 2),
        }[profile]
        warnings = []
        if profile == "expensive":
            warnings.append("Profilo expensive: richiede piano e approvazione esplicita.")
        return UsageEstimate(
            task_id=task.id,
            profile=profile,
            estimated_tool_calls=base[0],
            estimated_file_reads=base[1],
            estimated_output_lines=base[2],
            estimated_subagents=base[3],
            warnings=warnings,
        )
