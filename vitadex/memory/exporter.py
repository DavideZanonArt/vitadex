from __future__ import annotations

from pathlib import Path

from vitadex.memory.markdown_store import MarkdownMemoryStore
from vitadex.models.memory import MemoryRecord


def export_markdown(memory_dir: Path, records: list[MemoryRecord]) -> Path:
    return MarkdownMemoryStore(memory_dir).export_records(records)
