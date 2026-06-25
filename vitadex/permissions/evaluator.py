from __future__ import annotations

from vitadex.models.action import ActionRequest, PermissionDecision
from vitadex.permissions.policy import (
    ALLOWED_ACTIONS,
    APPROVAL_REQUIRED_ACTIONS,
    FORBIDDEN_ACTIONS,
)


class PermissionEvaluator:
    def evaluate(self, action: ActionRequest, approved: bool = False) -> PermissionDecision:
        if action.action_type in FORBIDDEN_ACTIONS:
            return PermissionDecision(
                allowed=False,
                forbidden=True,
                reason="Action forbidden by CONSTITUTION.md §5: payments, signatures, and legal commitments are not autonomous.",
            )
        if (
            action.action_type == "upload_document"
            and action.sensitivity_level in {"sensitive", "highly_sensitive"}
            and not approved
        ):
            return PermissionDecision(
                allowed=False,
                requires_approval=True,
                reason="Uploading sensitive documents requires explicit approval.",
            )
        if action.action_type in APPROVAL_REQUIRED_ACTIONS:
            return PermissionDecision(
                allowed=approved,
                requires_approval=not approved,
                reason="External action allowed only with approval."
                if not approved
                else "Approval is valid.",
            )
        if action.action_type in ALLOWED_ACTIONS:
            if action.action_type == "draft_external" and action.autonomy_level not in {
                "A0",
                "A1",
                "A2",
                "A3",
            }:
                return PermissionDecision(
                    allowed=False,
                    requires_approval=True,
                    reason="Autonomy level is too high for an external draft.",
                )
            return PermissionDecision(allowed=True, reason="Local action or draft is allowed.")
        return PermissionDecision(
            allowed=False, requires_approval=True, reason="Unrecognized action."
        )
