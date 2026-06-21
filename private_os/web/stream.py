from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from private_os.web.read_model import PrivateOpsReadModel


def sse_frame(event: str, data: dict[str, object]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


async def stream_dashboard(
    read_model: PrivateOpsReadModel,
    *,
    poll_interval: float = 1.0,
    once: bool = False,
) -> AsyncIterator[str]:
    previous_signature = read_model.snapshot_signature()
    yield sse_frame("health", {"mode": "read_only", "status": "connected"})
    yield sse_frame("snapshot:update", read_model.dashboard_snapshot())
    if once:
        return
    while True:
        await asyncio.sleep(poll_interval)
        current_signature = read_model.snapshot_signature()
        if current_signature != previous_signature:
            previous_signature = current_signature
            yield sse_frame("snapshot:update", read_model.dashboard_snapshot())
