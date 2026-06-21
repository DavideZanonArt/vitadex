from __future__ import annotations

import re
from pathlib import Path

from typer.testing import CliRunner

from private_os.cli import app


def _invoke(runner: CliRunner, root: Path, args: list[str]):
    result = runner.invoke(
        app,
        args,
        env={
            "PRIVATE_OS_ROOT": str(root),
            "PRIVATE_OS_DB_PATH": str(root / "data" / "private_os.sqlite"),
            "PRIVATE_OS_SAFE_MODE": "true",
            "PRIVATE_OS_IGNORE_CONSTITUTION": "true",
        },
    )
    assert result.exit_code == 0, result.output
    return result


def test_cli_main_private_ops_workflow(tmp_path):
    runner = CliRunner()
    root = tmp_path

    assert "Safe mode attivo" in _invoke(runner, root, ["init"]).output

    memory_output = _invoke(
        runner,
        root,
        [
            "memory",
            "add",
            "--type",
            "preference",
            "--area",
            "travel",
            "--text",
            "Preferisco viaggi in auto con Wi-Fi affidabile.",
        ],
    ).output
    memory_id = re.search(r"mem_[a-f0-9]+", memory_output).group(0)  # type: ignore[union-attr]
    assert "Wi-Fi" in _invoke(runner, root, ["memory", "search", "Wi-Fi"]).output
    assert "travel" in _invoke(runner, root, ["memory", "list"]).output
    assert "Export creato" in _invoke(runner, root, ["memory", "export"]).output
    assert "disattivata" in _invoke(runner, root, ["memory", "deactivate", memory_id]).output

    task_output = _invoke(
        runner,
        root,
        [
            "task",
            "create",
            "--title",
            "Cercare affitto 6 mesi a Monaco",
            "--area",
            "home",
            "--goal",
            "Trovare opzioni reali per affitto temporaneo a Monaco di Baviera",
            "--autonomy-level",
            "A3",
        ],
    ).output
    task_id = re.search(r"task_[a-f0-9]+", task_output).group(0)  # type: ignore[union-attr]
    assert task_id in _invoke(runner, root, ["task", "list"]).output
    assert "housing_search" in _invoke(runner, root, ["skills", "match", task_id]).output
    assert "housing_search" in _invoke(runner, root, ["task", "plan", task_id]).output
    assert "dry_run" in _invoke(runner, root, ["task", "execute", task_id, "--dry-run"]).output
    assert "needs_approval" in _invoke(runner, root, ["task", "show", task_id]).output

    approvals = _invoke(runner, root, ["approvals", "list"]).output
    approval_id = re.search(r"appr_[a-f0-9]+", approvals).group(0)  # type: ignore[union-attr]
    assert "send_message" in _invoke(runner, root, ["approvals", "show", approval_id]).output
    assert "concessa" in _invoke(runner, root, ["approvals", "approve", approval_id]).output

    followups = _invoke(runner, root, ["followups", "list"]).output
    followup_id = re.search(r"fu_[a-f0-9]+", followups).group(0)  # type: ignore[union-attr]
    assert "Follow-up completato" in _invoke(
        runner, root, ["followups", "complete", followup_id]
    ).output
    assert "PRIVATE OPS DASHBOARD" in _invoke(runner, root, ["dashboard"]).output
    assert "planning.created" in _invoke(runner, root, ["logs", "list"]).output

    second_task_output = _invoke(
        runner,
        root,
        [
            "task",
            "create",
            "--title",
            "Richiedere preventivo assicurazione",
            "--area",
            "bureaucracy",
            "--goal",
            "Preparare richiesta preventivo personale",
        ],
    ).output
    second_task_id = re.search(r"task_[a-f0-9]+", second_task_output).group(0)  # type: ignore[union-attr]
    assert "Stato aggiornato" in _invoke(
        runner, root, ["task", "update-status", second_task_id, "active"]
    ).output
    assert "Nota aggiunta" in _invoke(
        runner, root, ["task", "add-note", second_task_id, "Budget massimo da confermare"]
    ).output
    assert "Task chiusa" in _invoke(runner, root, ["task", "close", second_task_id]).output
    assert "Task archiviata" in _invoke(runner, root, ["task", "archive", second_task_id]).output

    third_task_output = _invoke(
        runner,
        root,
        [
            "task",
            "create",
            "--title",
            "Cercare altro affitto a Monaco",
            "--area",
            "home",
            "--goal",
            "Preparare secondo test approvazione",
        ],
    ).output
    third_task_id = re.search(r"task_[a-f0-9]+", third_task_output).group(0)  # type: ignore[union-attr]
    _invoke(runner, root, ["task", "plan", third_task_id])
    pending_approvals = _invoke(runner, root, ["approvals", "list", "--status", "pending"]).output
    reject_approval_id = re.search(r"appr_[a-f0-9]+", pending_approvals).group(0)  # type: ignore[union-attr]
    assert "rifiutata" in _invoke(
        runner, root, ["approvals", "reject", reject_approval_id]
    ).output

    remaining_followups = _invoke(runner, root, ["followups", "list", "--status", "pending"]).output
    cancel_followup_id = re.search(r"fu_[a-f0-9]+", remaining_followups).group(0)  # type: ignore[union-attr]
    assert "cancellato" in _invoke(
        runner, root, ["followups", "cancel", cancel_followup_id]
    ).output

    logs = _invoke(runner, root, ["logs", "list"]).output
    log_id = re.search(r"log_[a-f0-9]+", logs).group(0)  # type: ignore[union-attr]
    assert "event_type" in _invoke(runner, root, ["logs", "show", log_id]).output

    cost_task_output = _invoke(
        runner,
        root,
        [
            "task",
            "create",
            "--title",
            "Audit completo di tutto il repository",
            "--area",
            "private_projects",
            "--goal",
            "Fare audit completo",
        ],
    ).output
    cost_task_id = re.search(r"task_[a-f0-9]+", cost_task_output).group(0)  # type: ignore[union-attr]
    assert "expensive" in _invoke(runner, root, ["costs", "estimate", cost_task_id]).output
    assert "require_plan_first" in _invoke(runner, root, ["costs", "budget", cost_task_id]).output
    assert "trivial" in _invoke(
        runner, root, ["costs", "set-profile", cost_task_id, "trivial"]
    ).output
    assert "entries" in _invoke(runner, root, ["costs", "report"]).output
    assert "suggested_actions" in _invoke(runner, root, ["costs", "optimize", cost_task_id]).output
