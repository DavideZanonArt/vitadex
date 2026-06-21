from __future__ import annotations

from private_os.models.action import ActionRequest, PermissionDecision
from private_os.permissions.policy import (
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
                reason="Azione vietata da CONSTITUTION.md §5: pagamenti, firme e impegni legali non sono autonomi.",
            )
        if (
            action.action_type == "upload_document"
            and action.sensitivity_level in {"sensitive", "highly_sensitive"}
            and not approved
        ):
            return PermissionDecision(
                allowed=False,
                requires_approval=True,
                reason="Caricamento documenti sensibili richiede approvazione esplicita.",
            )
        if action.action_type in APPROVAL_REQUIRED_ACTIONS:
            return PermissionDecision(
                allowed=approved,
                requires_approval=not approved,
                reason="Azione esterna consentita solo con approvazione."
                if not approved
                else "Approvazione valida.",
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
                    reason="Autonomia troppo alta per bozza esterna.",
                )
            return PermissionDecision(allowed=True, reason="Azione locale o bozza consentita.")
        return PermissionDecision(
            allowed=False, requires_approval=True, reason="Azione non riconosciuta."
        )
