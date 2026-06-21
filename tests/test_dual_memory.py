from __future__ import annotations

from private_os.models.memory import MemoryRecord


def test_markdown_export_works(memory, root):
    memory.add(
        MemoryRecord(
            text="I prefer reliable Wi-Fi when I travel.",
            type="preference",
            area="preferences",
        )
    )

    path = memory.export_markdown()

    assert path.exists()
    assert "I prefer reliable Wi-Fi" in path.read_text(encoding="utf-8")


def test_sqlite_memory_remains_source_of_truth(memory):
    record = memory.add(
        MemoryRecord(
            text="Maximum budget to confirm before sending requests.",
            type="constraint",
            area="constraints",
        )
    )

    diff = memory.diff()

    assert memory.search("Maximum budget")[0].id == record.id
    assert diff["sqlite_records"] == 1


def test_inferred_memories_require_review(memory):
    record = memory.add(
        MemoryRecord(
            text="The user may prefer central neighborhoods.",
            type="preference",
            area="preferences",
            source="assistant_inferred",
        )
    )

    assert record.review_status == "needs_review"
    assert memory.review()[0].id == record.id


def test_sensitive_memories_are_blocked_from_external_output(memory):
    safe = memory.add(
        MemoryRecord(text="Prefers concise emails.", type="preference", area="preferences")
    )
    sensitive = memory.add(
        MemoryRecord(
            text="Sensitive personal data.",
            type="profile",
            area="private_profile",
            sensitivity="sensitive",
            source="assistant_inferred",
        )
    )

    results = memory.external_safe_search("email")

    assert safe.id in [record.id for record in results]
    assert sensitive.id not in [record.id for record in results]


def test_compaction_preserves_constraints(memory, root):
    memory.add(
        MemoryRecord(
            text="Do not send email without approval.",
            canonical_text="Do not send email without approval.",
            type="constraint",
            area="constraints",
        )
    )

    path = memory.compact()

    assert "Do not send email without approval." in path.read_text(encoding="utf-8")
