from __future__ import annotations

from datetime import UTC, datetime

from vitadex.models.memory import MemoryRecord


def low_confidence_needing_review(records: list[MemoryRecord]) -> list[MemoryRecord]:
    return [
        record
        for record in records
        if record.active and (record.confidence == "low" or record.review_status == "needs_review")
    ]


def stale_records(records: list[MemoryRecord]) -> list[MemoryRecord]:
    now = datetime.now(UTC).isoformat()
    return [record for record in records if record.active and record.expires_at and record.expires_at <= now]


def reflection_summary(records: list[MemoryRecord]) -> str:
    review = low_confidence_needing_review(records)
    stale = stale_records(records)
    return (
        "# Memory Reflection\n\n"
        f"- Memorie da rivedere: {len(review)}\n"
        f"- Memorie stale: {len(stale)}\n"
        "- Regola: non promuovere inferenze sensibili senza approvazione.\n"
    )
