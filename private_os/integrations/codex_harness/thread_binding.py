from __future__ import annotations

from private_os.integrations.codex_harness.session import CodexSessionBinding, CodexThreadRef
from private_os.models.task import TaskRecord


def binding_from_task(task: TaskRecord) -> CodexSessionBinding | None:
    if not task.codex_thread:
        return None
    thread = CodexThreadRef(**task.codex_thread["thread"])
    return CodexSessionBinding(
        id=task.codex_thread["id"],
        task_id=task.id,
        thread=thread,
        project_path=task.codex_thread["project_path"],
        created_at=task.codex_thread["created_at"],
        updated_at=task.codex_thread["updated_at"],
    )
