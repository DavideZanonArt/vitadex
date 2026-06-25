from __future__ import annotations

from collections.abc import Iterable


def bullet_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
