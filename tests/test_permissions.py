from __future__ import annotations

from private_os.models.action import ActionRequest
from private_os.permissions.evaluator import PermissionEvaluator


def test_permission_blocks_payment_and_signature():
    evaluator = PermissionEvaluator()
    assert evaluator.evaluate(ActionRequest(action_type="payment", title="Paga caparra")).forbidden
    assert evaluator.evaluate(
        ActionRequest(action_type="signature", title="Firma contratto")
    ).forbidden
    assert evaluator.evaluate(
        ActionRequest(action_type="legal_commitment", title="Accetta contratto")
    ).forbidden


def test_send_message_requires_approval():
    evaluator = PermissionEvaluator()
    decision = evaluator.evaluate(ActionRequest(action_type="send_message", title="Invia email"))
    assert decision.requires_approval
    assert not decision.allowed
    assert evaluator.evaluate(
        ActionRequest(action_type="send_message", title="Invia email"), approved=True
    ).allowed
