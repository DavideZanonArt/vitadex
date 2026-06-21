from __future__ import annotations

from private_os.models.memory import MemoryRecord


def test_memory_add_search_deactivate(memory):
    record = memory.add(
        MemoryRecord(
            text="Preferisco affitti temporanei a Monaco con Wi-Fi.",
            type="preference",
            area="home",
            tags=["monaco"],
        )
    )
    assert memory.search("Monaco")[0].id == record.id
    memory.deactivate(record.id)
    assert memory.search("Monaco") == []
    assert memory.list(active_only=False)[0].active is False
