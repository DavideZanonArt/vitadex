from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    root: Path
    state_root: Path
    data_dir: Path
    logs_dir: Path
    memory_dir: Path
    workspace_dir: Path
    db_path: Path
    safe_mode: bool = True
    language: str = "it"
    allowed_root: Path


def project_root() -> Path:
    return Path(os.getenv("PRIVATE_OS_ROOT", Path.cwd())).resolve()


def _resolve_path(value: str | os.PathLike[str] | None, *, base: Path) -> Path | None:
    if value is None or value == "":
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def get_settings(root: Path | None = None) -> Settings:
    base = (root or project_root()).resolve()
    state_root = _resolve_path(os.getenv("PRIVATE_OS_STATE_ROOT"), base=base) or base
    data_dir = _resolve_path(os.getenv("PRIVATE_OS_DATA_DIR"), base=state_root) or (state_root / "data")
    logs_dir = _resolve_path(os.getenv("PRIVATE_OS_LOG_DIR"), base=state_root) or (state_root / "logs")
    memory_dir = _resolve_path(os.getenv("PRIVATE_OS_MEMORY_DIR"), base=state_root) or (state_root / "memory")
    workspace_dir = _resolve_path(os.getenv("PRIVATE_OS_WORKSPACE_DIR"), base=state_root) or (state_root / "workspace")
    db_path = _resolve_path(os.getenv("PRIVATE_OS_DB_PATH"), base=state_root) or (data_dir / "private_os.sqlite")
    allowed_root = _resolve_path(os.getenv("PRIVATE_OS_ALLOWED_ROOT"), base=base) or base
    safe = os.getenv("PRIVATE_OS_SAFE_MODE", "true").lower() in {"1", "true", "yes", "on"}
    return Settings(
        root=base,
        state_root=state_root,
        data_dir=data_dir,
        logs_dir=logs_dir,
        memory_dir=memory_dir,
        workspace_dir=workspace_dir,
        db_path=db_path.resolve(),
        safe_mode=safe,
        language=os.getenv("PRIVATE_OS_LANGUAGE", "it"),
        allowed_root=allowed_root.resolve(),
    )
