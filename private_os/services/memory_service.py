from __future__ import annotations

import builtins
import sqlite3
from pathlib import Path

from private_os.core.db import get, list_rows, upsert
from private_os.core.logging import audit
from private_os.core.time import now_iso
from private_os.memory.compaction import compact_records, find_duplicates
from private_os.memory.exporter import export_markdown
from private_os.memory.importer import import_markdown_file
from private_os.memory.markdown_store import MarkdownMemoryStore
from private_os.memory.reflection import (
    low_confidence_needing_review,
    reflection_summary,
    stale_records,
)
from private_os.memory.search import external_safe
from private_os.memory.sqlite_store import SQLiteMemoryStore
from private_os.models.memory import MemoryRecord


class MemoryService:
    def __init__(self, conn: sqlite3.Connection, root: Path, *, memory_dir: Path | None = None):
        self.conn = conn
        self.root = root
        self.memory_dir = memory_dir or (root / "memory")
        self.sqlite = SQLiteMemoryStore(conn)
        self.markdown = MarkdownMemoryStore(self.memory_dir)

    def add(self, record: MemoryRecord) -> MemoryRecord:
        self.sqlite.save(record)
        self._index(record)
        self.markdown.append_record(record)
        audit(
            self.conn,
            "memory.created",
            f"Memoria aggiunta: {record.area}/{record.type}",
            payload=record.model_dump(),
        )
        return record

    def list(self, active_only: bool = True) -> builtins.list[MemoryRecord]:
        records = [MemoryRecord(**row) for row in list_rows(self.conn, "memory")]
        return [r for r in records if r.active] if active_only else records

    def search(self, query: str) -> builtins.list[MemoryRecord]:
        query = query.strip()
        if not query:
            return self.list()
        try:
            rows = self.conn.execute(
                "SELECT id FROM memory_fts WHERE memory_fts MATCH ? LIMIT 20",
                (query.replace('"', ""),),
            ).fetchall()
            ids = [row["id"] for row in rows]
        except sqlite3.OperationalError:
            ids = []
        records = self.list()
        if ids:
            by_id = {r.id: r for r in records}
            return [by_id[i] for i in ids if i in by_id]
        needle = query.lower()
        return [
            r
            for r in records
            if needle in r.text.lower()
            or needle in r.area.lower()
            or any(needle in tag.lower() for tag in r.tags)
        ]

    def deactivate(self, memory_id: str) -> MemoryRecord:
        row = get(self.conn, "memory", memory_id)
        if not row:
            raise KeyError(memory_id)
        record = MemoryRecord(**row)
        record.active = False
        record.updated_at = now_iso()
        upsert(self.conn, "memory", record.id, record.model_dump())
        audit(
            self.conn,
            "memory.deactivated",
            f"Memoria disattivata: {memory_id}",
            payload={"id": memory_id},
        )
        return record

    def export_markdown(self) -> Path:
        path = export_markdown(self.memory_dir, self.list(active_only=False))
        audit(
            self.conn,
            "memory.exported",
            "Memoria esportata in Markdown",
            payload={"path": str(path)},
        )
        return path

    def review(self) -> builtins.list[MemoryRecord]:
        return low_confidence_needing_review(self.list(active_only=False))

    def compact(self) -> Path:
        self.markdown.ensure_files()
        path = self.memory_dir / "MAINMEMORY.md"
        path.write_text(compact_records(self.list(active_only=False)), encoding="utf-8")
        audit(self.conn, "memory.compacted", "Memoria compatta aggiornata", payload={"path": str(path)})
        return path

    def reflect(self) -> Path:
        self.markdown.ensure_files()
        path = self.memory_dir / "REFLECTION.md"
        path.write_text(reflection_summary(self.list(active_only=False)), encoding="utf-8")
        audit(self.conn, "memory.reflected", "Reflection memoria generata", payload={"path": str(path)})
        return path

    def import_markdown(self, path: Path) -> builtins.list[MemoryRecord]:
        records = import_markdown_file(path)
        for record in records:
            self.add(record)
        return records

    def diff(self) -> dict[str, object]:
        records = self.list(active_only=False)
        markdown = self.markdown.read_all()
        markdown_text = "\n".join(markdown.values())
        missing = [record.id for record in records if record.id not in markdown_text]
        return {"sqlite_records": len(records), "markdown_files": len(markdown), "missing_in_markdown": missing}

    def stale(self) -> builtins.list[MemoryRecord]:
        return stale_records(self.list(active_only=False))

    def duplicates(self) -> builtins.list[tuple[str, str]]:
        return find_duplicates(self.list(active_only=False))

    def external_safe_search(self, query: str) -> builtins.list[MemoryRecord]:
        return external_safe(self.search(query))

    def promote_from_task(self, task_id: str) -> MemoryRecord:
        record = MemoryRecord(
            text=f"Pattern operativo derivato dalla task {task_id}.",
            canonical_text=f"Pattern operativo derivato dalla task {task_id}.",
            type="task_pattern",
            area="task_patterns",
            source="assistant_inferred",
            confidence="low",
            related_task_id=task_id,
            review_status="needs_review",
        )
        return self.add(record)

    def _index(self, record: MemoryRecord) -> None:
        self.conn.execute("DELETE FROM memory_fts WHERE id = ?", (record.id,))
        self.conn.execute(
            "INSERT INTO memory_fts (id, text, area, type, tags) VALUES (?, ?, ?, ?, ?)",
            (record.id, record.text, record.area, record.type, " ".join(record.tags)),
        )
        self.conn.commit()
