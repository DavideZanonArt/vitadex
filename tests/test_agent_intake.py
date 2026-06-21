from __future__ import annotations

import json
import re

from typer.testing import CliRunner

from private_os.cli import app
from private_os.models.memory import MemoryRecord
from private_os.services.agent_intake_service import AgentIntakeService
from private_os.services.audit_service import AuditService


def test_agent_intake_creates_housing_workflow(conn, memory, tasks):
    memory.add(
        MemoryRecord(
            text="For Munich, prefer a central area and reliable Wi-Fi.",
            type="preference",
            area="home",
            tags=["munich", "rental"],
        )
    )
    service = AgentIntakeService(conn, memory, tasks)

    result = service.intake("Find me housing options to stay 6 months in Munich, center or max 10 minutes by car.")

    assert result["task"]["id"].startswith("task_")
    assert result["task"]["area"] == "home"
    assert result["selected_skill"] == "housing_search"
    assert result["plan"]["required_skills"][0] == "housing_search"
    assert result["execution"]["dry_run"] is True
    assert result["approvals"][0]["action_type"] == "send_message"
    assert result["approvals"][0]["payload"]["action_id"].startswith("act_")
    assert result["followups"]
    assert "maximum monthly budget" in result["plan"]["missing_info"]
    assert "*Private OS - intake completed*" in result["markdown"]
    assert "*Email sending*" in result["markdown"]
    assert "Not executed" in result["markdown"]
    assert "agent.intake.completed" in [log["event_type"] for log in AuditService(conn).list()]


def test_agent_intake_cli_outputs_markdown_and_json(tmp_path):
    runner = CliRunner()
    env = {
        "PRIVATE_OS_ROOT": str(tmp_path),
        "PRIVATE_OS_DB_PATH": str(tmp_path / "data" / "private_os.sqlite"),
        "PRIVATE_OS_SAFE_MODE": "true",
        "PRIVATE_OS_IGNORE_CONSTITUTION": "true",
    }
    message = "Find me housing options to stay 6 months in Munich, center or max 10 minutes by car."

    markdown = runner.invoke(app, ["agent", "intake", message], env=env)

    assert markdown.exit_code == 0, markdown.output
    assert "*Task created:*" in markdown.output
    assert "*Selected skill:* `housing_search`" in markdown.output
    assert "*Approvals to confirm*" in markdown.output
    assert re.search(r"appr_[a-f0-9]+", markdown.output)

    json_result = runner.invoke(app, ["agent", "intake", message, "--json"], env=env)

    assert json_result.exit_code == 0, json_result.output
    payload = json.loads(json_result.output)
    assert payload["selected_skill"] == "housing_search"
    assert payload["task"]["id"].startswith("task_")
    assert payload["approvals"][0]["status"] == "pending"
    assert "markdown" in payload
