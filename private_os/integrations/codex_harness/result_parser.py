from __future__ import annotations

from private_os.integrations.codex_harness.session import CodexExecutionResult


class CodexResultParser:
    def parse_logs(self, result: CodexExecutionResult) -> list[dict[str, object]]:
        return [
            {
                "event_type": "codex.output",
                "summary": line,
                "payload": result.payload,
            }
            for line in result.logs
        ]
