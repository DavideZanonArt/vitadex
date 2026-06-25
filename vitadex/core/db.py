from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

TABLES = ["memory", "tasks", "plans", "approvals", "followups", "logs", "usage_logs", "panels"]


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    for table in TABLES:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
        USING fts5(id UNINDEXED, text, area, type, tags)
        """
    )
    conn.commit()


def upsert(conn: sqlite3.Connection, table: str, item_id: str, data: dict[str, Any]) -> None:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True)
    created_at = data.get("created_at") or data.get("timestamp") or ""
    updated_at = data.get("updated_at") or created_at
    conn.execute(
        f"""
        INSERT INTO {table} (id, data, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at
        """,
        (item_id, payload, created_at, updated_at),
    )
    conn.commit()


def get(conn: sqlite3.Connection, table: str, item_id: str) -> dict[str, Any] | None:
    row = conn.execute(f"SELECT data FROM {table} WHERE id = ?", (item_id,)).fetchone()
    return json.loads(row["data"]) if row else None


def list_rows(conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        f"SELECT data FROM {table} ORDER BY updated_at DESC, created_at DESC, rowid DESC"
    ).fetchall()
    return [json.loads(row["data"]) for row in rows]


def delete(conn: sqlite3.Connection, table: str, item_id: str) -> None:
    conn.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
    conn.commit()
