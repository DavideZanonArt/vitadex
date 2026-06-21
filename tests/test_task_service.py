from __future__ import annotations

from private_os.models.task import TaskRecord


def test_task_create_and_update(tasks):
    task = tasks.create(TaskRecord(title="Cercare affitto", area="home", goal="Trovare casa"))
    assert task.status == "inbox"
    updated = tasks.update_status(task.id, "active")
    assert updated.status == "active"
    noted = tasks.add_note(task.id, "Budget da confermare")
    assert "Budget da confermare" in noted.decision_log
