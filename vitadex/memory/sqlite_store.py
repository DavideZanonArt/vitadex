from __future__ import annotations

import sqlite3

from vitadex.core.db import get, list_rows, upsert
from vitadex.models.memory import MemoryRecord


class SQLiteMemoryStore:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, record: MemoryRecord) -> MemoryRecord:
        upsert(self.conn, "memory", record.id, record.model_dump())
        return record

    def get(self, memory_id: str) -> MemoryRecord | None:
        row = get(self.conn, "memory", memory_id)
        return MemoryRecord(**row) if row else None

    def list(self, active_only: bool = True) -> list[MemoryRecord]:
        records = [MemoryRecord(**row) for row in list_rows(self.conn, "memory")]
        return [record for record in records if record.active] if active_only else records
