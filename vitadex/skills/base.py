from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from vitadex.core.ids import new_id
from vitadex.models.approval import ApprovalRecord
from vitadex.models.plan import PlanRecord
from vitadex.models.skill import SkillManifest
from vitadex.models.task import TaskRecord


class SkillContext(dict[str, Any]):
    """Execution context passed to skills, usually including retrieved memories."""


class Skill(ABC):
    manifest: SkillManifest

    def can_handle(self, task: TaskRecord, context: SkillContext) -> int:
        haystack = f"{task.title} {task.goal} {task.description} {task.area}".lower()
        score = sum(1 for term in self.manifest.trigger_examples if term.lower() in haystack)
        if self.manifest.area.lower() in haystack:
            score += 2
        return score

    @abstractmethod
    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        raise NotImplementedError

    def produce_outputs(self, task: TaskRecord, result: dict[str, Any]) -> dict[str, Any]:
        return result

    def required_approvals(self, task: TaskRecord, plan: PlanRecord) -> list[ApprovalRecord]:
        approvals: list[ApprovalRecord] = []
        for point in plan.approval_points:
            payload = dict(point.get("payload", {}))
            payload.setdefault("action_id", new_id("act"))
            approvals.append(
                ApprovalRecord(
                    task_id=task.id,
                    action_type=point.get("action_type", "send_message"),
                    title=point.get("title", "Approval required"),
                    description=point.get("description", ""),
                    payload=payload,
                    risk_level=point.get("risk_level", "medium"),
                    sensitivity_level=point.get("sensitivity_level", "personal"),
                )
            )
        return approvals
