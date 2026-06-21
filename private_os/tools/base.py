from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from private_os.models.action import ActionRequest
from private_os.permissions.evaluator import PermissionEvaluator


@dataclass(frozen=True)
class ApprovalToken:
    approval_id: str
    action_id: str


class Tool(ABC):
    name: str

    def __init__(self) -> None:
        self.permissions = PermissionEvaluator()

    def check(self, action: ActionRequest, approval: ApprovalToken | None = None) -> None:
        approved = isinstance(approval, ApprovalToken) and approval.action_id == action.id
        decision = self.permissions.evaluate(action, approved=approved)
        if not decision.allowed:
            raise PermissionError(decision.reason)

    @abstractmethod
    def run(self, action: ActionRequest, approval: ApprovalToken | None = None) -> dict[str, Any]:
        raise NotImplementedError
