from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from private_os.core.db import init_db
from private_os.services.memory_service import MemoryService
from private_os.services.task_service import TaskService


@pytest.fixture()
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_db(connection)
    return connection


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def memory(conn: sqlite3.Connection, root: Path) -> MemoryService:
    return MemoryService(conn, root)


@pytest.fixture()
def tasks(conn: sqlite3.Connection) -> TaskService:
    return TaskService(conn)
