from __future__ import annotations

from private_os.models.task import TaskRecord


def test_task_create_and_update(tasks):
    task = tasks.create(TaskRecord(title="Find a rental", area="home", goal="Find a home"))
    assert task.status == "inbox"
    updated = tasks.update_status(task.id, "active")
    assert updated.status == "active"
    noted = tasks.add_note(task.id, "Budget to confirm")
    assert "Budget to confirm" in noted.decision_log
