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
            text="Per Monaco preferire zona centrale e Wi-Fi affidabile.",
            type="preference",
            area="home",
            tags=["monaco", "affitto"],
        )
    )
    service = AgentIntakeService(conn, memory, tasks)

    result = service.intake(
        "Trovami preventivi per stare 6 mesi a Monaco, centro o massimo 10 minuti auto."
    )

    assert result["task"]["id"].startswith("task_")
    assert result["task"]["area"] == "home"
    assert result["selected_skill"] == "housing_search"
    assert result["plan"]["required_skills"][0] == "housing_search"
    assert result["execution"]["dry_run"] is True
    assert result["approvals"][0]["action_type"] == "send_message"
    assert result["approvals"][0]["payload"]["action_id"].startswith("act_")
    assert result["followups"]
    assert "budget massimo mensile" in result["plan"]["missing_info"]
    assert "*Private OS - intake completato*" in result["markdown"]
    assert "*Invio email*" in result["markdown"]
    assert "Non eseguito" in result["markdown"]
    assert "agent.intake.completed" in [log["event_type"] for log in AuditService(conn).list()]


def test_agent_intake_cli_outputs_markdown_and_json(tmp_path):
    runner = CliRunner()
    env = {
        "PRIVATE_OS_ROOT": str(tmp_path),
        "PRIVATE_OS_DB_PATH": str(tmp_path / "data" / "private_os.sqlite"),
        "PRIVATE_OS_SAFE_MODE": "true",
        "PRIVATE_OS_IGNORE_CONSTITUTION": "true",
    }
    message = "Trovami preventivi per stare 6 mesi a Monaco, centro o massimo 10 minuti auto."

    markdown = runner.invoke(app, ["agent", "intake", message], env=env)

    assert markdown.exit_code == 0, markdown.output
    assert "*Task creata:*" in markdown.output
    assert "*Skill selezionata:* `housing_search`" in markdown.output
    assert "*Approval da confermare*" in markdown.output
    assert re.search(r"appr_[a-f0-9]+", markdown.output)

    json_result = runner.invoke(app, ["agent", "intake", message, "--json"], env=env)

    assert json_result.exit_code == 0, json_result.output
    payload = json.loads(json_result.output)
    assert payload["selected_skill"] == "housing_search"
    assert payload["task"]["id"].startswith("task_")
    assert payload["approvals"][0]["status"] == "pending"
    assert "markdown" in payload
