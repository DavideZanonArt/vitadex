from __future__ import annotations

from vitadex.models.memory import MemoryRecord


def external_safe(records: list[MemoryRecord]) -> list[MemoryRecord]:
    return [
        record
        for record in records
        if record.sensitivity in {"public", "personal"} and record.review_status == "accepted"
    ]
