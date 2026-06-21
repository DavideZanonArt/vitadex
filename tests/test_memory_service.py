from __future__ import annotations

from private_os.models.memory import MemoryRecord


def test_memory_add_search_deactivate(memory):
    record = memory.add(
        MemoryRecord(
            text="I prefer temporary rentals in Munich with Wi-Fi.",
            type="preference",
            area="home",
            tags=["munich"],
        )
    )
    assert memory.search("Munich")[0].id == record.id
    memory.deactivate(record.id)
    assert memory.search("Munich") == []
    assert memory.list(active_only=False)[0].active is False
