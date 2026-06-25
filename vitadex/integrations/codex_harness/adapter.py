from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import cast

from vitadex.core.logging import audit
from vitadex.core.time import now_iso
from vitadex.integrations.codex_harness.command_builder import CodexCommandBuilder
from vitadex.integrations.codex_harness.config import CodexHarnessConfig
from vitadex.integrations.codex_harness.result_parser import CodexResultParser
from vitadex.integrations.codex_harness.session import (
    CodexExecutionResult,
    CodexSessionBinding,
    CodexThreadRef,
)
from vitadex.integrations.codex_harness.thread_binding import binding_from_task
from vitadex.services.task_service import TaskService


class CodexHarnessAdapter:
    def __init__(self, conn: sqlite3.Connection, root: Path, config: CodexHarnessConfig):
        self.conn = conn
        self.root = root.resolve()
        self.config = config
        self.tasks = TaskService(conn)
        self.parser = CodexResultParser()

    def status(self) -> dict[str, object]:
        return {
            "enabled": self.config.enabled,
            "mode": self.config.mode,
            "runtime_policy": self.config.runtime_policy,
            "working_directory": str((self.root / self.config.working_directory).resolve()),
            "fail_closed": self.config.runtime_policy == "fail_closed",
        }

    def bind_task(self, task_id: str) -> CodexSessionBinding:
        task = self.tasks.get(task_id)
        existing = binding_from_task(task)
        if existing:
            return existing
        binding = CodexSessionBinding(
            task_id=task.id,
            thread=CodexThreadRef(title=task.title, task_id=task.id),
            project_path=str(self.root),
        )
        task.codex_thread = binding.model_dump()
        self.tasks.save(task)
        audit(
            self.conn,
            "codex.thread_bound",
            f"Task bound to Codex thread: {binding.thread.id}",
            task_id=task.id,
            payload=binding.model_dump(),
        )
        return binding

    def list_threads(self) -> list[CodexThreadRef]:
        refs: list[CodexThreadRef] = []
        for task in self.tasks.list():
            binding = binding_from_task(task)
            if binding:
                refs.append(binding.thread)
        return refs

    def export_context(self, task_id: str) -> dict[str, object]:
        task = self.tasks.get(task_id)
        binding = binding_from_task(task)
        return {
            "task": task.model_dump(),
            "codex_binding": binding.model_dump() if binding else None,
            "ownership_split": {
                "codex": ["agent session", "thread continuation", "workspace changes"],
                "vitadex": ["tasks", "memory", "approvals", "logs", "dashboard", "summary"],
            },
            "safety": self.status(),
        }

    def resume_thread(self, task_id: str) -> CodexExecutionResult:
        binding = self.bind_task(task_id)
        if not self.config.enabled or self.config.mode == "disabled":
            return self._fail_closed(task_id, binding.thread.id, "Codex unavailable: runtime disabled.")
        return CodexExecutionResult(
            task_id=task_id,
            thread_id=binding.thread.id,
            status="dry_run",
            executed=False,
            summary="Codex thread ready. No external action executed.",
            logs=["Resume thread in dry-run mode."],
        )

    def run_task(self, task_id: str, dry_run: bool = True) -> CodexExecutionResult:
        binding = self.bind_task(task_id)
        if not self._path_allowed(self.root):
            return self._fail_closed(task_id, binding.thread.id, "Project path blocked by Codex policy.")
        if not self.config.enabled and self.config.runtime_policy == "fail_closed":
            return self._fail_closed(task_id, binding.thread.id, "Codex unavailable: fail closed.")
        if dry_run or self.config.mode == "dry_run":
            command = CodexCommandBuilder(self.root, self.config).build(self.tasks.get(task_id), dry_run=True)
            result = CodexExecutionResult(
                task_id=task_id,
                thread_id=binding.thread.id,
                status="dry_run",
                executed=False,
                summary="Codex dry-run: command prepared, no action executed.",
                logs=["Codex dry-run completed without shell, browser, or external sends."],
                payload={"command": command.model_dump()},
            )
            self.log_result(result)
            return result
        if not self.config.allow_shell:
            return self._fail_closed(task_id, binding.thread.id, "Shell not allowed by Codex policy.")
        return self._fail_closed(task_id, binding.thread.id, "Live execution is not implemented in safe mode.")

    def log_result(self, result: CodexExecutionResult) -> None:
        audit(
            self.conn,
            "codex.execution_result",
            result.summary,
            task_id=result.task_id,
            payload=result.model_dump(),
        )
        for item in self.parser.parse_logs(result):
            audit(
                self.conn,
                str(item["event_type"]),
                str(item["summary"]),
                task_id=result.task_id,
                payload=cast(dict[str, object], item["payload"]),
            )

    def _fail_closed(self, task_id: str, thread_id: str | None, summary: str) -> CodexExecutionResult:
        result = CodexExecutionResult(
            task_id=task_id,
            thread_id=thread_id,
            status="failed_closed",
            executed=False,
            summary=summary,
            logs=[summary],
            created_at=now_iso(),
        )
        self.log_result(result)
        return result

    def _path_allowed(self, path: Path) -> bool:
        resolved = path.resolve()
        root_text = str(self.root)
        if not str(resolved).startswith(root_text):
            return False
        for denied in self.config.denied_paths:
            if denied and denied in str(resolved):
                return False
        return True
