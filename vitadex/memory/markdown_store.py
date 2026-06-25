from __future__ import annotations

from pathlib import Path

from vitadex.models.memory import MemoryRecord

MEMORY_FILES = {
    "main": "MAINMEMORY.md",
    "shared": "SHAREDMEMORY.md",
    "private_profile": "PRIVATE_PROFILE.md",
    "preferences": "PREFERENCES.md",
    "decisions": "DECISIONS.md",
    "relationships": "RELATIONSHIPS.md",
    "places": "PLACES.md",
    "task_patterns": "TASK_PATTERNS.md",
    "do_not_do": "DO_NOT_DO.md",
}


class MarkdownMemoryStore:
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir

    def ensure_files(self) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        for filename in MEMORY_FILES.values():
            path = self.memory_dir / filename
            if not path.exists():
                path.write_text(f"# {filename.removesuffix('.md')}\n\n", encoding="utf-8")

    def append_record(self, record: MemoryRecord) -> Path:
        self.ensure_files()
        path = self.memory_dir / MEMORY_FILES.get(record.area, "MAINMEMORY.md")
        line = (
            f"- `{record.id}` [{record.review_status}] ({record.confidence}, "
            f"{record.sensitivity}) {record.canonical_text or record.text}\n"
        )
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
        return path

    def export_records(self, records: list[MemoryRecord], filename: str = "EXPORT.md") -> Path:
        self.ensure_files()
        path = self.memory_dir / filename
        lines = ["# Memory Export", ""]
        for record in records:
            lines.extend(
                [
                    f"## {record.id}",
                    f"- Area: {record.area}",
                    f"- Type: {record.type}",
                    f"- Review: {record.review_status}",
                    f"- Sensitivity: {record.sensitivity}",
                    f"- Text: {record.canonical_text or record.text}",
                    "",
                ]
            )
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def read_all(self) -> dict[str, str]:
        self.ensure_files()
        return {
            filename: (self.memory_dir / filename).read_text(encoding="utf-8")
            for filename in MEMORY_FILES.values()
        }
