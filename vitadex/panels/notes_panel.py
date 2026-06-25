from __future__ import annotations

from vitadex.panels.base import Panel


def note_panel(title: str, content: str) -> Panel:
    return Panel(title=title, type="note", content=content, source="note")
