from __future__ import annotations

from private_os.costs.budget import UsageLog
from private_os.costs.optimizer import CostOptimizer
from private_os.costs.policy import budget_for_profile
from private_os.costs.usage_log import UsageLogService
from private_os.models.task import TaskRecord


def test_trivial_task_gets_low_budget(tasks):
    task = tasks.create(
        TaskRecord(
            title="Update a small template",
            area="private_projects",
            goal="Update a short note",
        )
    )

    assert task.cost_profile == "trivial"
    assert task.token_budget is not None
    assert task.token_budget["reasoning_level"] == "low"
    assert task.token_budget["max_file_reads"] == 3


def test_expensive_task_requires_plan_first(tasks):
    task = tasks.create(
        TaskRecord(
            title="Full audit of the entire repository",
            area="private_projects",
            goal="Run a full audit",
        )
    )

    assert task.cost_profile == "expensive"
    assert task.token_budget is not None
    assert task.token_budget["require_plan_first"] is True
    assert task.token_budget["require_compaction"] is True


def test_subagent_blocked_when_budget_is_zero():
    budget = budget_for_profile("task_1", "normal")
    decision = CostOptimizer().evaluate_subagent(budget, requested_subagents=1)

    assert decision.allowed is False
    assert "Subagents are blocked" in decision.reason


def test_output_lines_are_capped():
    text = "\n".join(f"line {idx}" for idx in range(5))
    capped = CostOptimizer().cap_output(text, max_lines=3)

    assert capped.splitlines() == ["line 0", "line 1", "line 2", "[Output truncated by budget]"]


def test_cost_report_aggregates_usage_logs(conn):
    service = UsageLogService(conn)
    service.record(UsageLog(task_id="task_1", turns=2, file_reads=3, tool_calls=4, output_lines=10))
    service.record(UsageLog(task_id="task_2", turns=1, file_reads=2, tool_calls=1, output_lines=5))

    report = service.report()

    assert report["tasks"] == 2
    assert report["turns"] == 3
    assert report["file_reads"] == 5
    assert report["tool_calls"] == 5
    assert report["output_lines"] == 15


def test_optimizer_suggests_skill_extraction_for_repeated_prompts():
    logs = [
        UsageLog(task_id="task_1", prompt_fingerprint="housing_munich"),
        UsageLog(task_id="task_1", prompt_fingerprint="housing_munich"),
        UsageLog(task_id="task_1", prompt_fingerprint="housing_munich"),
    ]

    decision = CostOptimizer().optimize(budget_for_profile("task_1", "normal"), logs)

    assert any("Extract a skill" in suggestion for suggestion in decision.suggested_actions)
