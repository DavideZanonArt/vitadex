from __future__ import annotations

from vitadex.models.memory import MemoryRecord


def compact_records(records: list[MemoryRecord]) -> str:
    accepted = [record for record in records if record.active and record.review_status == "accepted"]
    lines = ["# Compacted Memory", ""]
    for record in accepted:
        lines.append(f"- ({record.area}/{record.type}) {record.canonical_text or record.text}")
    return "\n".join(lines)


def find_duplicates(records: list[MemoryRecord]) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    duplicates: list[tuple[str, str]] = []
    for record in records:
        key = (record.canonical_text or record.text).strip().lower()
        if key in seen:
            duplicates.append((seen[key], record.id))
        else:
            seen[key] = record.id
    return duplicates
