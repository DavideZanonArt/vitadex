from __future__ import annotations

from private_os.panels.base import Panel


def decision_panel(title: str, recommendation: str, risks: str = "", next_action: str = "") -> Panel:
    return Panel(
        title=title,
        type="decision",
        content={"recommendation": recommendation, "risks": risks, "next_action": next_action},
        source="decision",
    )
