from __future__ import annotations

from private_os.models.memory import MemoryRecord
from private_os.panels.base import Panel


def memory_panel(record: MemoryRecord) -> Panel:
    return Panel(
        title=f"Memoria {record.area}",
        type="note",
        content=record.model_dump(),
        tags=[record.area, record.type],
        source="memory",
    )
