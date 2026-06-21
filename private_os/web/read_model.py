from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from private_os.panels.base import Panel
from private_os.panels.renderer import PanelRenderer
from private_os.services.approval_service import ApprovalService
from private_os.services.audit_service import AuditService
from private_os.services.followup_service import FollowupService
from private_os.services.panel_service import PanelService
from private_os.services.task_service import TaskService

EntityKind = Literal["task", "approval", "followup", "panel", "log"]


class PrivateOpsReadModel:
    def __init__(self, conn: sqlite3.Connection, root: Path, db_path: Path):
        self.conn = conn
        self.root = root
        self.db_path = db_path
        self.tasks = TaskService(conn)
        self.approvals = ApprovalService(conn)
        self.followups = FollowupService(conn)
        self.audit = AuditService(conn)
        self.panels = PanelService(conn, root)
        self.panel_renderer = PanelRenderer()

    def dashboard_snapshot(self) -> dict[str, Any]:
        tasks = self.tasks.list()
        approvals = self.approvals.list()
        followups = self.followups.list()
        logs = self.audit.list()
        panels = self.panels.list()
        priorities = self.operations(limit=8)
        timeline = self.timeline(limit=20)
        active_tasks = [task for task in tasks if task.status in {"active", "needs_approval", "waiting"}]
        due_followups = [item for item in followups if item.status == "pending" and item.due_date]
        decision_requests = [task for task in tasks if task.missing_info or task.status == "needs_approval"]
        return {
            "generatedAt": self._latest_timestamp(tasks, approvals, followups, logs, panels),
            "summary": {
                "activeTasks": len(active_tasks),
                "pendingApprovals": len([item for item in approvals if item.status == "pending"]),
                "dueFollowups": len(due_followups),
                "decisionRequests": len(decision_requests),
                "recentEvents": len(timeline),
                "panels": len(panels),
                "logs": len(logs),
            },
            "priorities": priorities,
            "timeline": timeline,
            "health": {
                "mode": "read_only",
                "realtime": "polling",
                "source": "local_sqlite",
                "workspaceRoot": str(self.root),
            },
        }

    def operations(
        self,
        *,
        kind: EntityKind | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        items = [
            *[self._task_item(task) for task in self.tasks.list()],
            *[self._approval_item(approval) for approval in self.approvals.list()],
            *[self._followup_item(followup) for followup in self.followups.list()],
            *[self._panel_item(panel) for panel in self.panels.list()],
            *[self._log_item(log) for log in self.audit.list()],
        ]
        filtered = items
        if kind:
            filtered = [item for item in filtered if item["kind"] == kind]
        if status:
            filtered = [item for item in filtered if item["status"] == status]
        if search:
            term = search.casefold()
            filtered = [
                item
                for item in filtered
                if term in item["title"].casefold()
                or term in item["preview"].casefold()
                or any(term in tag.casefold() for tag in item["tags"])
            ]
        ordered = sorted(filtered, key=lambda item: item["updatedAt"], reverse=True)
        return ordered[:limit]

    def timeline(self, *, limit: int = 20) -> list[dict[str, Any]]:
        events = [self._timeline_event(log) for log in self.audit.list()]
        return sorted(events, key=lambda item: item["at"], reverse=True)[:limit]

    def logs_list(self, *, limit: int = 50) -> list[dict[str, Any]]:
        logs = [self._log_item(log) for log in self.audit.list()]
        return sorted(logs, key=lambda item: item["updatedAt"], reverse=True)[:limit]

    def panels_list(self, *, limit: int = 50) -> list[dict[str, Any]]:
        panels = [self._panel_item(panel) for panel in self.panels.list()]
        return sorted(panels, key=lambda item: item["updatedAt"], reverse=True)[:limit]

    def entity(self, kind: EntityKind, entity_id: str) -> dict[str, Any]:
        if kind == "task":
            task = self.tasks.get(entity_id)
            data = task.model_dump()
            return self._entity_response(
                kind=kind,
                entity_id=entity_id,
                title=task.title,
                status=task.status,
                data=data,
                related_task_id=task.id,
            )
        if kind == "approval":
            approval = self.approvals.get(entity_id)
            data = approval.model_dump()
            return self._entity_response(
                kind=kind,
                entity_id=entity_id,
                title=approval.title,
                status=approval.status,
                data=data,
                related_task_id=approval.task_id,
            )
        if kind == "followup":
            followup = self.followups.get(entity_id)
            data = followup.model_dump()
            return self._entity_response(
                kind=kind,
                entity_id=entity_id,
                title=followup.title,
                status=followup.status,
                data=data,
                related_task_id=followup.task_id,
            )
        if kind == "panel":
            panel = self.panels.get(entity_id)
            rendered = self.panel_renderer.markdown(panel)
            return self._entity_response(
                kind=kind,
                entity_id=entity_id,
                title=panel.title,
                status=panel.status,
                data=panel.model_dump(),
                related_task_id=panel.related_task_id,
                rendered=rendered,
            )
        log = self.audit.show(entity_id)
        if not log:
            raise KeyError(entity_id)
        return self._entity_response(
            kind=kind,
            entity_id=entity_id,
            title=log["summary"],
            status=log.get("risk_level") or "info",
            data=log,
            related_task_id=log.get("task_id"),
        )

    def snapshot_signature(self) -> str:
        payload = json.dumps(self.dashboard_snapshot(), ensure_ascii=False, sort_keys=True)
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    def _entity_response(
        self,
        *,
        kind: EntityKind,
        entity_id: str,
        title: str,
        status: str,
        data: dict[str, Any],
        related_task_id: str | None,
        rendered: str | None = None,
    ) -> dict[str, Any]:
        return {
            "id": entity_id,
            "kind": kind,
            "title": title,
            "status": status,
            "relatedTaskId": related_task_id,
            "data": data,
            "rendered": rendered,
        }

    def _task_item(self, task: Any) -> dict[str, Any]:
        preview = task.goal or task.description or ", ".join(task.next_actions[:2])
        return {
            "id": task.id,
            "kind": "task",
            "title": task.title,
            "status": task.status,
            "updatedAt": task.updated_at,
            "relatedTaskId": task.id,
            "tags": [task.area, task.priority, task.autonomy_level],
            "preview": preview,
        }

    def _approval_item(self, approval: Any) -> dict[str, Any]:
        return {
            "id": approval.id,
            "kind": "approval",
            "title": approval.title,
            "status": approval.status,
            "updatedAt": approval.updated_at,
            "relatedTaskId": approval.task_id,
            "tags": [approval.action_type, approval.risk_level, approval.sensitivity_level],
            "preview": approval.description,
        }

    def _followup_item(self, followup: Any) -> dict[str, Any]:
        return {
            "id": followup.id,
            "kind": "followup",
            "title": followup.title,
            "status": followup.status,
            "updatedAt": followup.updated_at,
            "relatedTaskId": followup.task_id,
            "tags": [followup.cadence or "once", followup.trigger_condition],
            "preview": followup.action,
        }

    def _panel_item(self, panel: Panel) -> dict[str, Any]:
        preview = panel.content if isinstance(panel.content, str) else json.dumps(panel.content, ensure_ascii=False)
        return {
            "id": panel.id,
            "kind": "panel",
            "title": panel.title,
            "status": panel.status,
            "updatedAt": panel.updated_at,
            "relatedTaskId": panel.related_task_id,
            "tags": [panel.type, panel.source, *panel.tags],
            "preview": preview[:280],
        }

    def _log_item(self, log: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": log["id"],
            "kind": "log",
            "title": log["summary"],
            "status": log.get("risk_level") or "info",
            "updatedAt": log["updated_at"],
            "relatedTaskId": log.get("task_id"),
            "tags": [log["event_type"], log.get("actor") or "system"],
            "preview": json.dumps(log.get("payload") or {}, ensure_ascii=False)[:280],
        }

    def _timeline_event(self, log: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": log["id"],
            "at": log["timestamp"],
            "kind": self._kind_from_event(log["event_type"]),
            "label": log["summary"],
            "severity": self._severity(log),
            "entityId": log.get("task_id") or log["id"],
            "entityKind": "task" if log.get("task_id") else "log",
        }

    def _kind_from_event(self, event_type: str) -> str:
        prefix = event_type.split(".", 1)[0]
        return prefix if prefix in {"task", "approval", "followup", "panel"} else "system"

    def _severity(self, log: dict[str, Any]) -> str:
        risk = log.get("risk_level")
        if risk == "critical":
            return "critical"
        if risk in {"high", "medium"}:
            return "warning"
        return "info"

    def _latest_timestamp(self, *collections: list[Any]) -> str:
        timestamps = [
            item.updated_at
            for collection in collections
            for item in collection
            if hasattr(item, "updated_at")
        ]
        timestamps.extend(
            [
                item["updated_at"]
                for collection in collections
                for item in collection
                if isinstance(item, dict) and "updated_at" in item
            ]
        )
        return max(timestamps, default=self._fallback_timestamp())

    def _fallback_timestamp(self) -> str:
        target = self.db_path if self.db_path.exists() else self.root
        return datetime.fromtimestamp(target.stat().st_mtime, tz=UTC).isoformat()
