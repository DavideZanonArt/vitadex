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
    return Path(os.getenv("VITADEX_ROOT") or os.getenv("PRIVATE_OS_ROOT") or Path.cwd()).resolve()


def _resolve_path(value: str | os.PathLike[str] | None, *, base: Path) -> Path | None:
    if value is None or value == "":
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _load_local_env(base: Path) -> dict[str, str]:
    for candidate in [base / ".env.local", base / ".env"]:
        if not candidate.exists():
            continue
        values: dict[str, str] = {}
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key:
                values[key] = value
        return values
    return {}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def get_settings(root: Path | None = None) -> Settings:
    base = (root or project_root()).resolve()
    file_env = _load_local_env(base)

    def env(name: str, legacy: str | None = None, default: str | None = None) -> str | None:
        return os.getenv(name) or (os.getenv(legacy) if legacy else None) or file_env.get(name) or (
            file_env.get(legacy) if legacy else None
        ) or default

    state_root = _resolve_path(env("VITADEX_STATE_ROOT", "PRIVATE_OS_STATE_ROOT"), base=base) or base
    data_dir = _resolve_path(env("VITADEX_DATA_DIR", "PRIVATE_OS_DATA_DIR"), base=state_root) or (state_root / "data")
    logs_dir = _resolve_path(env("VITADEX_LOG_DIR", "PRIVATE_OS_LOG_DIR"), base=state_root) or (state_root / "logs")
    memory_dir = _resolve_path(env("VITADEX_MEMORY_DIR", "PRIVATE_OS_MEMORY_DIR"), base=state_root) or (state_root / "memory")
    workspace_dir = _resolve_path(env("VITADEX_WORKSPACE_DIR", "PRIVATE_OS_WORKSPACE_DIR"), base=state_root) or (
        state_root / "workspace"
    )
    db_path = _resolve_path(env("VITADEX_DB_PATH", "PRIVATE_OS_DB_PATH"), base=state_root) or (data_dir / "vitadex.sqlite")
    allowed_root = _resolve_path(env("VITADEX_ALLOWED_ROOT", "PRIVATE_OS_ALLOWED_ROOT"), base=base) or base
    safe_value = env("VITADEX_SAFE_MODE", "PRIVATE_OS_SAFE_MODE", "true") or "true"
    language = env("VITADEX_LANGUAGE", "PRIVATE_OS_LANGUAGE", "it") or "it"
    safe = safe_value.lower() in {"1", "true", "yes", "on"}
    return Settings(
        root=base,
        state_root=state_root,
        data_dir=data_dir,
        logs_dir=logs_dir,
        memory_dir=memory_dir,
        workspace_dir=workspace_dir,
        db_path=db_path.resolve(),
        safe_mode=safe,
        language=language,
        allowed_root=allowed_root.resolve(),
    )
