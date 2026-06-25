from __future__ import annotations

import sqlite3

from vitadex.core.db import get, list_rows, upsert
from vitadex.core.logging import audit
from vitadex.core.time import now_iso
from vitadex.costs.estimator import CostEstimator
from vitadex.costs.policy import budget_for_profile
from vitadex.models.task import TaskRecord


class TaskService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, task: TaskRecord) -> TaskRecord:
        if task.cost_profile is None:
            task.cost_profile = CostEstimator().classify(task)
        if task.token_budget is None:
            task.token_budget = budget_for_profile(task.id, task.cost_profile).model_dump()
        upsert(self.conn, "tasks", task.id, task.model_dump())
        audit(
            self.conn,
            "task.created",
            f"Task creata: {task.title}",
            task_id=task.id,
            payload=task.model_dump(),
        )
        return task

    def get(self, task_id: str) -> TaskRecord:
        row = get(self.conn, "tasks", task_id)
        if not row:
            raise KeyError(task_id)
        return TaskRecord(**row)

    def list(self) -> list[TaskRecord]:
        return [TaskRecord(**row) for row in list_rows(self.conn, "tasks")]

    def save(self, task: TaskRecord) -> TaskRecord:
        task.updated_at = now_iso()
        upsert(self.conn, "tasks", task.id, task.model_dump())
        return task

    def update_status(self, task_id: str, status: str) -> TaskRecord:
        task = self.get(task_id)
        task.status = status  # type: ignore[assignment]
        if status == "done":
            task.completed_at = now_iso()
        self.save(task)
        audit(self.conn, "task.status_updated", f"Task {task_id} -> {status}", task_id=task_id)
        return task

    def add_note(self, task_id: str, note: str) -> TaskRecord:
        task = self.get(task_id)
        task.decision_log.append(note)
        self.save(task)
        audit(
            self.conn,
            "task.note_added",
            "Nota aggiunta alla task",
            task_id=task_id,
            payload={"note": note},
        )
        return task
