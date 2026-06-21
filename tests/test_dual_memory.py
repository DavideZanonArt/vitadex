from __future__ import annotations

from private_os.models.memory import MemoryRecord


def test_markdown_export_works(memory, root):
    memory.add(
        MemoryRecord(
            text="Preferisco Wi-Fi affidabile quando viaggio.",
            type="preference",
            area="preferences",
        )
    )

    path = memory.export_markdown()

    assert path.exists()
    assert "Preferisco Wi-Fi affidabile" in path.read_text(encoding="utf-8")


def test_sqlite_memory_remains_source_of_truth(memory):
    record = memory.add(
        MemoryRecord(
            text="Budget massimo da confermare prima di inviare richieste.",
            type="constraint",
            area="constraints",
        )
    )

    diff = memory.diff()

    assert memory.search("Budget massimo")[0].id == record.id
    assert diff["sqlite_records"] == 1


def test_inferred_memories_require_review(memory):
    record = memory.add(
        MemoryRecord(
            text="L'utente forse preferisce quartieri centrali.",
            type="preference",
            area="preferences",
            source="assistant_inferred",
        )
    )

    assert record.review_status == "needs_review"
    assert memory.review()[0].id == record.id


def test_sensitive_memories_are_blocked_from_external_output(memory):
    safe = memory.add(
        MemoryRecord(text="Preferisce email concise.", type="preference", area="preferences")
    )
    sensitive = memory.add(
        MemoryRecord(
            text="Dato personale sensibile.",
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
            text="Non inviare email senza approvazione.",
            canonical_text="Non inviare email senza approvazione.",
            type="constraint",
            area="constraints",
        )
    )

    path = memory.compact()

    assert "Non inviare email senza approvazione." in path.read_text(encoding="utf-8")
