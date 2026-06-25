from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from vitadex.core.ids import new_id
from vitadex.core.time import now_iso


class CodexThreadRef(BaseModel):
    id: str = Field(default_factory=lambda: new_id("codex_thread"))
    title: str
    task_id: str | None = None
    created_at: str = Field(default_factory=now_iso)


class CodexSessionBinding(BaseModel):
    id: str = Field(default_factory=lambda: new_id("codex_binding"))
    task_id: str
    thread: CodexThreadRef
    project_path: str
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


class CodexCommand(BaseModel):
    task_id: str
    prompt: str
    project_path: str
    dry_run: bool = True
    approval_policy: str = "vitadex_approval_queue"
    allowed_paths: list[str] = Field(default_factory=list)
    denied_paths: list[str] = Field(default_factory=list)


class CodexExecutionResult(BaseModel):
    task_id: str
    thread_id: str | None = None
    status: Literal["dry_run", "completed", "failed_closed", "blocked"] = "dry_run"
    executed: bool = False
    summary: str
    logs: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_iso)
