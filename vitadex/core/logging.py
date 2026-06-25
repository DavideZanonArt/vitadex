from __future__ import annotations

import sqlite3
from typing import Any

from vitadex.core.db import upsert
from vitadex.core.ids import new_id
from vitadex.core.time import now_iso


def audit(
    conn: sqlite3.Connection,
    event_type: str,
    summary: str,
    *,
    task_id: str | None = None,
    actor: str = "system",
    payload: dict[str, Any] | None = None,
    risk_level: str | None = None,
) -> dict[str, Any]:
    log_id = new_id("log")
    timestamp = now_iso()
    record = {
        "id": log_id,
        "timestamp": timestamp,
        "event_type": event_type,
        "task_id": task_id,
        "actor": actor,
        "summary": summary,
        "payload": _redact_payload(payload),
        "risk_level": risk_level,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    upsert(conn, "logs", log_id, record)
    return record


def _redact_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {}
    return {
        "redacted": True,
        "type": "dict",
        "keys": sorted(str(key) for key in payload),
    }
