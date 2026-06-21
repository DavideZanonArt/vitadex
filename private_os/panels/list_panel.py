from __future__ import annotations

from private_os.panels.base import Panel


def list_panel(title: str, items: list[str]) -> Panel:
    return Panel(title=title, type="list", content={"items": items}, source="list")
