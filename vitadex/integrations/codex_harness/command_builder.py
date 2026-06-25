from __future__ import annotations

from pathlib import Path

from vitadex.integrations.codex_harness.config import CodexHarnessConfig
from vitadex.integrations.codex_harness.session import CodexCommand
from vitadex.models.task import TaskRecord


class CodexCommandBuilder:
    def __init__(self, root: Path, config: CodexHarnessConfig):
        self.root = root.resolve()
        self.config = config

    def build(self, task: TaskRecord, dry_run: bool = True) -> CodexCommand:
        prompt = (
            f"Private task: {task.title}\n"
            f"Goal: {task.goal}\n"
            "Respect memory, the approval queue, safe mode, and separation from business systems."
        )
        return CodexCommand(
            task_id=task.id,
            prompt=prompt,
            project_path=str(self.root),
            dry_run=dry_run,
            approval_policy=self.config.approval_policy,
            allowed_paths=[str((self.root / item).resolve()) for item in self.config.allowed_paths],
            denied_paths=self.config.denied_paths,
        )
