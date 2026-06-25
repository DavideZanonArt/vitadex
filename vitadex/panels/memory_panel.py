from __future__ import annotations

from vitadex.models.memory import MemoryRecord
from vitadex.panels.base import Panel


def memory_panel(record: MemoryRecord) -> Panel:
    return Panel(
        title=f"Memory {record.area}",
        type="note",
        content=record.model_dump(),
        tags=[record.area, record.type],
        source="memory",
    )
