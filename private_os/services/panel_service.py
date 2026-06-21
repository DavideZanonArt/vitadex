from __future__ import annotations

import sqlite3
from pathlib import Path

from private_os.core.db import get, list_rows, upsert
from private_os.core.logging import audit
from private_os.core.time import now_iso
from private_os.panels.base import Panel
from private_os.panels.dashboard_panel import dashboard_panel
from private_os.panels.renderer import PanelRenderer
from private_os.panels.task_panel import task_panel
from private_os.services.approval_service import ApprovalService
from private_os.services.followup_service import FollowupService
from private_os.services.task_service import TaskService


class PanelService:
    def __init__(self, conn: sqlite3.Connection, root: Path, *, workspace_dir: Path | None = None):
        self.conn = conn
        self.root = root
        self.workspace_dir = workspace_dir or (root / "workspace")
        self.renderer = PanelRenderer()

    def ensure_workspace(self) -> None:
        for folder in ["panels", "notes", "lists", "outputs", "decisions"]:
            (self.workspace_dir / folder).mkdir(parents=True, exist_ok=True)

    def create(self, panel: Panel) -> Panel:
        self.ensure_workspace()
        upsert(self.conn, "panels", panel.id, panel.model_dump())
        self.write_markdown(panel)
        audit(self.conn, "panel.created", f"Panel creato: {panel.title}", task_id=panel.related_task_id, payload=panel.model_dump())
        return panel

    def get(self, panel_id: str) -> Panel:
        row = get(self.conn, "panels", panel_id)
        if not row:
            raise KeyError(panel_id)
        return Panel(**row)

    def list(self) -> list[Panel]:
        return [Panel(**row) for row in list_rows(self.conn, "panels")]

    def update(self, panel_id: str, content: str | None = None, status: str | None = None) -> Panel:
        panel = self.get(panel_id)
        if content is not None:
            panel.content = content
        if status is not None:
            panel.status = status
        panel.updated_at = now_iso()
        return self.create(panel)

    def from_task(self, task_id: str) -> Panel:
        task = TaskService(self.conn).get(task_id)
        return self.create(task_panel(task))

    def dashboard(self) -> Panel:
        tasks = TaskService(self.conn).list()
        approvals = ApprovalService(self.conn).list("pending")
        followups = FollowupService(self.conn).list("pending")
        active = len([task for task in tasks if task.status in {"active", "needs_approval", "waiting"}])
        return self.create(dashboard_panel(active, len(approvals), len(followups)))

    def write_markdown(self, panel: Panel) -> Path:
        target = self.workspace_dir / "panels" / f"{panel.id}.md"
        target.write_text(self.renderer.markdown(panel), encoding="utf-8")
        return target

    def render_json(self, panel_id: str) -> str:
        return self.renderer.json(self.get(panel_id))

    def serve_static(self) -> Path:
        self.ensure_workspace()
        panels = self.list()
        items = "\n".join(f"<li><a href='panels/{panel.id}.md'>{panel.title}</a> ({panel.type})</li>" for panel in panels)
        html = f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><title>Private OS Panels</title></head>
<body><h1>Private OS Panels</h1><p>Locale: 127.0.0.1. Non esporre su rete pubblica.</p><ul>{items}</ul></body></html>
"""
        path = self.workspace_dir / "index.html"
        path.write_text(html, encoding="utf-8")
        return path
