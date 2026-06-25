from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class CodexHarnessConfig(BaseModel):
    enabled: bool = False
    mode: Literal["disabled", "dry_run", "enabled"] = "dry_run"
    runtime_policy: Literal["fail_closed", "fallback_to_local"] = "fail_closed"
    default_model: str = "codex-default"
    working_directory: str = "."
    skills_directory: str = "vitadex/skills"
    approval_policy: str = "vitadex_approval_queue"
    allow_native_code_mode: bool = False
    allow_browser_use: bool = False
    allow_shell: bool = False
    allowed_paths: list[str] = Field(default_factory=lambda: ["."])
    denied_paths: list[str] = Field(default_factory=lambda: ["../", "~", "/tmp", "/var", "/etc"])


def load_codex_config(root: Path) -> CodexHarnessConfig:
    path = root / "config" / "codex-harness.yaml"
    if not path.exists():
        return CodexHarnessConfig()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return CodexHarnessConfig(**data)
