from __future__ import annotations

from pathlib import Path

from vitadex.models.memory import MemoryRecord


def import_markdown_file(path: Path, *, area: str = "main") -> list[MemoryRecord]:
    if not path.exists():
        return []
    records: list[MemoryRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip().removeprefix("-").strip()
        if text:
            records.append(
                MemoryRecord(
                    text=text,
                    canonical_text=text,
                    type="imported_note",
                    area=area,  # type: ignore[arg-type]
                    source="imported",
                    review_status="needs_review",
                )
            )
    return records
