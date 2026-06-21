from __future__ import annotations

import sqlite3
from collections import Counter

from private_os.core.db import list_rows, upsert
from private_os.core.logging import audit
from private_os.core.time import now_iso
from private_os.costs.budget import UsageLog


class UsageLogService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def record(self, log: UsageLog) -> UsageLog:
        upsert(self.conn, "usage_logs", log.id, log.model_dump())
        audit(
            self.conn,
            "costs.usage_logged",
            f"Uso registrato per task {log.task_id}",
            task_id=log.task_id,
            payload=log.model_dump(),
        )
        return log

    def list(self) -> list[UsageLog]:
        return [UsageLog(**row) for row in list_rows(self.conn, "usage_logs")]

    def report(self) -> dict[str, object]:
        logs = self.list()
        repeated = Counter(log.prompt_fingerprint for log in logs if log.prompt_fingerprint)
        return {
            "tasks": len({log.task_id for log in logs}),
            "entries": len(logs),
            "turns": sum(log.turns for log in logs),
            "file_reads": sum(log.file_reads for log in logs),
            "subagents": sum(log.subagents for log in logs),
            "tool_calls": sum(log.tool_calls for log in logs),
            "output_lines": sum(log.output_lines for log in logs),
            "repeated_prompts": {k: v for k, v in repeated.items() if v > 1},
            "updated_at": now_iso(),
        }
