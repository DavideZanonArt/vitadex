from __future__ import annotations

import sqlite3
from typing import Any

from private_os.core.db import get, list_rows
from private_os.core.logging import audit


class AuditService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def record(self, event_type: str, summary: str, **kwargs: Any) -> dict[str, Any]:
        return audit(self.conn, event_type, summary, **kwargs)

    def list(self) -> list[dict[str, Any]]:
        return list_rows(self.conn, "logs")

    def show(self, log_id: str) -> dict[str, Any] | None:
        return get(self.conn, "logs", log_id)
