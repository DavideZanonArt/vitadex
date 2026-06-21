from __future__ import annotations

import json

from private_os.panels.base import Panel


class PanelRenderer:
    def markdown(self, panel: Panel) -> str:
        lines = [f"# {panel.title}", "", f"- Type: {panel.type}", f"- Status: {panel.status}"]
        if panel.related_task_id:
            lines.append(f"- Task: `{panel.related_task_id}`")
        lines.append("")
        if isinstance(panel.content, str):
            lines.append(panel.content)
        elif panel.type == "dashboard":
            lines.extend(self._dashboard(panel.content))
        elif panel.type == "approval":
            lines.extend(self._approval(panel.content))
        elif panel.type == "decision":
            lines.extend(self._decision(panel.content))
        elif panel.type == "task":
            lines.extend(self._task(panel.content))
        else:
            lines.append("```json")
            lines.append(json.dumps(panel.content, ensure_ascii=False, indent=2))
            lines.append("```")
        return "\n".join(lines)

    def json(self, panel: Panel) -> str:
        return panel.model_dump_json(indent=2)

    def _task(self, content: dict) -> list[str]:
        return [
            f"## Obiettivo\n{content.get('goal', '')}",
            f"## Stato\n{content.get('status', '')}",
            "## Prossime azioni",
            *[f"- {item}" for item in content.get("next_actions", [])],
        ]

    def _approval(self, content: dict) -> list[str]:
        return [
            "## Approval",
            f"- Azione: {content.get('action_type', '')}",
            f"- Rischio: {content.get('risk_level', '')}",
            f"- Stato: {content.get('status', '')}",
            f"- Descrizione: {content.get('description', '')}",
        ]

    def _decision(self, content: dict) -> list[str]:
        return [
            "## Decisione",
            f"- Raccomandazione: {content.get('recommendation', '')}",
            f"- Rischi: {content.get('risks', '')}",
            f"- Prossima azione: {content.get('next_action', '')}",
        ]

    def _dashboard(self, content: dict) -> list[str]:
        return [
            "## Dashboard",
            f"- Task attive: {content.get('active_tasks', 0)}",
            f"- Approval pendenti: {content.get('pending_approvals', 0)}",
            f"- Follow-up pendenti: {content.get('pending_followups', 0)}",
        ]
