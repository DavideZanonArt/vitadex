from __future__ import annotations

from vitadex.models.action import ActionRequest
from vitadex.permissions.evaluator import PermissionEvaluator


def test_permission_blocks_payment_and_signature():
    evaluator = PermissionEvaluator()
    assert evaluator.evaluate(ActionRequest(action_type="payment", title="Pay deposit")).forbidden
    assert evaluator.evaluate(
        ActionRequest(action_type="signature", title="Sign contract")
    ).forbidden
    assert evaluator.evaluate(
        ActionRequest(action_type="legal_commitment", title="Accept contract")
    ).forbidden


def test_send_message_requires_approval():
    evaluator = PermissionEvaluator()
    decision = evaluator.evaluate(ActionRequest(action_type="send_message", title="Send email"))
    assert decision.requires_approval
    assert not decision.allowed
    assert evaluator.evaluate(
        ActionRequest(action_type="send_message", title="Send email"), approved=True
    ).allowed
