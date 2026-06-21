from __future__ import annotations

FORBIDDEN_ACTIONS = {"payment", "signature", "legal_commitment"}
APPROVAL_REQUIRED_ACTIONS = {
    "submit_external",
    "send_message",
    "create_calendar_event",
    "upload_document",
}
ALLOWED_ACTIONS = {"read", "write_local", "draft_external"}
