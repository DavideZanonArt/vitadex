from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

KnowledgeScope = Literal["public", "personal"]
KnowledgeSource = Literal["docs", "memory", "workspace"]

PUBLIC_ROOT_FILES = ("README.md", "ROADMAP.md", "CHANGELOG.md", "CONTRIBUTING.md")
PERSONAL_PRIORITY_FILES = (
    "MAINMEMORY.md",
    "PRIVATE_PROFILE.md",
    "preferences.md",
    "constraints.md",
    "decisions.md",
    "finance.md",
    "health.md",
    "travel.md",
)
WORKSPACE_SUBDIRECTORIES = ("notes", "lists", "outputs", "panels")


@dataclass(slots=True)
class KnowledgeItem:
    id: str
    title: str
    scope: KnowledgeScope
    source: KnowledgeSource
    kind: str
    path: str
    updated_at: str
    tags: list[str]
    preview: str
    content_path: Path

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "scope": self.scope,
            "source": self.source,
            "kind": self.kind,
            "path": self.path,
            "updatedAt": self.updated_at,
            "tags": self.tags,
            "preview": self.preview,
        }


class KnowledgeIndex:
    def __init__(
        self,
        *,
        public_root: Path,
        state_root: Path,
        memory_root: Path | None = None,
        workspace_root: Path | None = None,
    ) -> None:
        self.public_root = public_root.resolve()
        self.state_root = state_root.resolve()
        self.memory_root = (memory_root or (self.state_root / "memory")).resolve()
        self.workspace_root = (workspace_root or (self.state_root / "workspace")).resolve()

    def snapshot(self) -> dict[str, object]:
        indexed = self._indexed_items()
        public_items = [item for item in indexed if item.scope == "public"]
        personal_items = [item for item in indexed if item.source == "memory"]
        workspace_items = [item for item in indexed if item.source == "workspace"]
        return {
            "mainDocs": [item.as_dict() for item in public_items[:6]],
            "personalContext": [item.as_dict() for item in personal_items[:6]],
            "recentWorkspaceFiles": [item.as_dict() for item in workspace_items[:6]],
            "health": self._health(indexed),
        }

    def items(
        self,
        *,
        scope: KnowledgeScope | None = None,
        source: KnowledgeSource | None = None,
        search: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, object]]:
        indexed = self._indexed_items()
        filtered = indexed
        if scope is not None:
            filtered = [item for item in filtered if item.scope == scope]
        if source is not None:
            filtered = [item for item in filtered if item.source == source]
        if search:
            term = search.casefold()
            filtered = [item for item in filtered if self._matches(item, term)]
        ordered = sorted(filtered, key=lambda item: item.updated_at, reverse=True)
        return [item.as_dict() for item in ordered[:limit]]

    def content(self, item_id: str) -> dict[str, object]:
        if not item_id.startswith("kh_"):
            raise ValueError(item_id)
        item = self._items_by_id().get(item_id)
        if item is None:
            raise KeyError(item_id)
        if not item.content_path.exists() or not item.content_path.is_file():
            raise KeyError(item_id)
        content = self._read_text(item.content_path)
        return {
            **item.as_dict(),
            "content": content,
        }

    def _indexed_items(self) -> list[KnowledgeItem]:
        items = [
            *self._public_items(),
            *self._memory_items(),
            *self._workspace_items(),
        ]
        return sorted(items, key=lambda item: item.updated_at, reverse=True)

    def _items_by_id(self) -> dict[str, KnowledgeItem]:
        return {item.id: item for item in self._indexed_items()}

    def _public_items(self) -> list[KnowledgeItem]:
        items: list[KnowledgeItem] = []
        seen: set[Path] = set()
        for relative_path in PUBLIC_ROOT_FILES:
            candidate = self._resolve_inside(self.public_root, relative_path)
            if candidate is None:
                continue
            seen.add(candidate)
            items.append(self._build_item(candidate, scope="public", source="docs", relative_to=self.public_root))

        for directory in ("docs", "workflows"):
            base = self.public_root / directory
            if not base.exists():
                continue
            for candidate in sorted(base.rglob("*.md")):
                resolved = candidate.resolve()
                if resolved in seen or not resolved.is_file():
                    continue
                seen.add(resolved)
                items.append(self._build_item(resolved, scope="public", source="docs", relative_to=self.public_root))
        return items

    def _memory_items(self) -> list[KnowledgeItem]:
        if not self.memory_root.exists():
            return []
        items: list[KnowledgeItem] = []
        seen: set[Path] = set()
        for filename in PERSONAL_PRIORITY_FILES:
            candidate = self._resolve_inside(self.memory_root, filename)
            if candidate is None:
                continue
            seen.add(candidate)
            items.append(self._build_item(candidate, scope="personal", source="memory", relative_to=self.memory_root))

        for candidate in sorted(self.memory_root.glob("*.md")):
            resolved = candidate.resolve()
            if resolved in seen or not resolved.is_file():
                continue
            items.append(self._build_item(resolved, scope="personal", source="memory", relative_to=self.memory_root))
        return items

    def _workspace_items(self) -> list[KnowledgeItem]:
        if not self.workspace_root.exists():
            return []
        items: list[KnowledgeItem] = []
        for directory in WORKSPACE_SUBDIRECTORIES:
            base = self.workspace_root / directory
            if not base.exists():
                continue
            for candidate in sorted(base.rglob("*")):
                resolved = candidate.resolve()
                if not resolved.is_file():
                    continue
                items.append(self._build_item(resolved, scope="personal", source="workspace", relative_to=self.workspace_root))
        return items

    def _build_item(
        self,
        path: Path,
        *,
        scope: KnowledgeScope,
        source: KnowledgeSource,
        relative_to: Path,
    ) -> KnowledgeItem:
        relative_path = path.resolve().relative_to(relative_to.resolve()).as_posix()
        title, preview = self._extract_text_parts(path)
        updated_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
        kind = self._kind_for(path=path, source=source)
        tags = [scope, source, kind, *self._path_tags(relative_path)]
        return KnowledgeItem(
            id=self._item_id(scope=scope, source=source, relative_path=relative_path),
            title=title,
            scope=scope,
            source=source,
            kind=kind,
            path=relative_path,
            updated_at=updated_at,
            tags=tags,
            preview=preview,
            content_path=path.resolve(),
        )

    def _health(self, items: list[KnowledgeItem]) -> dict[str, object]:
        public_count = len([item for item in items if item.scope == "public"])
        personal_count = len([item for item in items if item.scope == "personal"])
        memory_count = len([item for item in items if item.source == "memory"])
        workspace_count = len([item for item in items if item.source == "workspace"])
        return {
            "publicAvailable": public_count > 0,
            "personalAvailable": self.memory_root.exists() or self.workspace_root.exists(),
            "counts": {
                "public": public_count,
                "personal": personal_count,
                "memory": memory_count,
                "workspace": workspace_count,
                "total": len(items),
            },
        }

    def _matches(self, item: KnowledgeItem, term: str) -> bool:
        haystacks = [item.title, item.path, item.preview, *item.tags]
        return any(term in value.casefold() for value in haystacks)

    def _item_id(self, *, scope: KnowledgeScope, source: KnowledgeSource, relative_path: str) -> str:
        digest = hashlib.sha1(f"{scope}:{source}:{relative_path}".encode("utf-8")).hexdigest()[:16]
        return f"kh_{digest}"

    def _extract_text_parts(self, path: Path) -> tuple[str, str]:
        content = self._read_text(path)
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        heading = next((line.lstrip("#").strip() for line in lines if line.startswith("#")), "")
        title = heading or path.stem.replace("-", " ").replace("_", " ").title()
        preview_source = " ".join(lines[:6])
        preview = self._preview(preview_source)
        return title, preview

    def _kind_for(self, *, path: Path, source: KnowledgeSource) -> str:
        if source == "docs":
            return "markdown"
        if source == "workspace" and "panels" in path.parts:
            return "panel"
        return "note"

    def _path_tags(self, relative_path: str) -> list[str]:
        tags: list[str] = []
        for part in Path(relative_path).parts:
            cleaned = part.replace(".md", "").replace("-", " ").replace("_", " ").strip()
            if cleaned:
                tags.append(cleaned)
        return tags

    def _preview(self, content: str, *, limit: int = 280) -> str:
        collapsed = " ".join(content.split())
        return collapsed[:limit]

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")

    def _resolve_inside(self, root: Path, relative_path: str) -> Path | None:
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            return None
        if not candidate.exists() or not candidate.is_file():
            return None
        return candidate
