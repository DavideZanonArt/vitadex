from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
import yaml
from rich import print

from private_os.constitution import Constitution, ConstitutionMissingError
from private_os.core.config import get_settings
from private_os.core.db import connect, init_db
from private_os.costs.budget import UsageLog
from private_os.costs.estimator import CostEstimator
from private_os.costs.optimizer import CostOptimizer
from private_os.costs.policy import budget_for_profile
from private_os.costs.usage_log import UsageLogService
from private_os.integrations.codex_harness.adapter import CodexHarnessAdapter
from private_os.integrations.codex_harness.config import load_codex_config
from private_os.models.memory import MemoryRecord
from private_os.models.task import TaskRecord
from private_os.panels.base import Panel
from private_os.services.agent_intake_service import AgentIntakeService
from private_os.services.approval_service import ApprovalService
from private_os.services.audit_service import AuditService
from private_os.services.dashboard_service import DashboardService
from private_os.services.followup_service import FollowupService
from private_os.services.memory_service import MemoryService
from private_os.services.panel_service import PanelService
from private_os.services.planning_service import PlanningService
from private_os.services.skill_service import SkillService
from private_os.services.task_service import TaskService
from private_os.skills.exporter import SkillExporter
from private_os.skills.validator import validate_exportable_manifests
from private_os.web.app import create_web_app

app = typer.Typer(help="Private OS locale-first per workflow personali.")
memory_app = typer.Typer(help="Memoria strutturata.")
task_app = typer.Typer(help="Task operative.")
skills_app = typer.Typer(help="Skill disponibili.")
approvals_app = typer.Typer(help="Coda approvazioni.")
followups_app = typer.Typer(help="Follow-up.")
logs_app = typer.Typer(help="Log audit.")
agent_app = typer.Typer(help="Flussi agentici end-to-end.")
costs_app = typer.Typer(help="Budget token e ottimizzazione costi.")
codex_app = typer.Typer(help="Integrazione Codex harness.")
constitution_app = typer.Typer(help="Costituzione operativa del progetto.")
panel_app = typer.Typer(help="Workspace a pannelli.")
app.add_typer(memory_app, name="memory")
app.add_typer(task_app, name="task")
app.add_typer(skills_app, name="skills")
app.add_typer(approvals_app, name="approvals")
app.add_typer(followups_app, name="followups")
app.add_typer(logs_app, name="logs")
app.add_typer(agent_app, name="agent")
app.add_typer(costs_app, name="costs")
app.add_typer(codex_app, name="codex")
app.add_typer(constitution_app, name="constitution")
app.add_typer(panel_app, name="panel")


def _conn():
    settings = get_settings()
    if os.getenv("PRIVATE_OS_IGNORE_CONSTITUTION", "false").lower() not in {"1", "true", "yes"}:
        try:
            Constitution(settings.root, settings.state_root).load()
        except ConstitutionMissingError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=2) from exc
    conn = connect(settings.db_path)
    init_db(conn)
    return conn


def _services():
    conn = _conn()
    settings = get_settings()
    memory = MemoryService(conn, settings.state_root, memory_dir=settings.memory_dir)
    tasks = TaskService(conn)
    return conn, settings, memory, tasks


@app.command()
def init() -> None:
    """Inizializza database e cartelle locali."""
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    for folder in [settings.data_dir, settings.logs_dir, settings.memory_dir, settings.workspace_dir]:
        folder.mkdir(parents=True, exist_ok=True)
    print(f"[green]Private OS inizializzato[/green]: {settings.db_path}")
    print(f"Runtime locale: {settings.state_root}")
    print("Safe mode attivo: nessun invio esterno, nessun pagamento, nessuna firma.")


@app.command()
def dashboard() -> None:
    conn = _conn()
    print(DashboardService(conn).render())


@app.command("serve")
def serve() -> None:
    conn, settings, _, _ = _services()
    path = PanelService(conn, settings.state_root, workspace_dir=settings.workspace_dir).serve_static()
    print(f"Dashboard locale inizializzata: {path}")
    print("Aprila localmente. Rischio: non esporre questa cartella su rete pubblica.")


@app.command("web")
def web(
    host: Annotated[str, typer.Option("--host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port")] = 8765,
) -> None:
    """Avvia la dashboard web locale in sola lettura."""
    settings = get_settings()
    access_token = secrets.token_urlsafe(24)
    app_instance = create_web_app(
        root=settings.root,
        state_root=settings.state_root,
        db_path=settings.db_path,
        access_token=access_token,
    )
    print(f"Dashboard web locale: http://{host}:{port}/?access_token={access_token}")
    print("Modalita' sola lettura attiva. Non esporre questa porta su rete pubblica.")
    uvicorn.run(app_instance, host=host, port=port, log_level="warning")


@panel_app.command("list")
def panel_list() -> None:
    conn, settings, _, _ = _services()
    for panel in PanelService(conn, settings.state_root, workspace_dir=settings.workspace_dir).list():
        print(f"{panel.id} | {panel.type} | {panel.status} | {panel.title}")


@panel_app.command("show")
def panel_show(panel_id: str, json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    conn, settings, _, _ = _services()
    service = PanelService(conn, settings.state_root, workspace_dir=settings.workspace_dir)
    panel = service.get(panel_id)
    if json_output:
        typer.echo(service.render_json(panel_id))
    else:
        typer.echo(service.renderer.markdown(panel))


@panel_app.command("create")
def panel_create(
    type: Annotated[str, typer.Option("--type")],
    title: Annotated[str, typer.Option("--title")],
    content: Annotated[str, typer.Option("--content")] = "",
) -> None:
    conn, settings, _, _ = _services()
    panel = Panel(title=title, type=type, content=content)  # type: ignore[arg-type]
    created = PanelService(conn, settings.state_root, workspace_dir=settings.workspace_dir).create(panel)
    print(f"Panel creato: {created.id}")


@panel_app.command("update")
def panel_update(
    panel_id: str,
    content: Annotated[str | None, typer.Option("--content")] = None,
    status: Annotated[str | None, typer.Option("--status")] = None,
) -> None:
    conn, settings, _, _ = _services()
    updated = PanelService(conn, settings.state_root, workspace_dir=settings.workspace_dir).update(
        panel_id, content=content, status=status
    )
    print(f"Panel aggiornato: {updated.id}")


@panel_app.command("from-task")
def panel_from_task(task_id: str) -> None:
    conn, settings, _, _ = _services()
    panel = PanelService(conn, settings.state_root, workspace_dir=settings.workspace_dir).from_task(task_id)
    print(f"Panel task creato: {panel.id}")


@panel_app.command("dashboard")
def panel_dashboard() -> None:
    conn, settings, _, _ = _services()
    service = PanelService(conn, settings.state_root, workspace_dir=settings.workspace_dir)
    panel = service.dashboard()
    typer.echo(service.renderer.markdown(panel))


@constitution_app.command("show")
def constitution_show() -> None:
    settings = get_settings()
    typer.echo(Constitution(settings.root, settings.state_root).load())


@constitution_app.command("check")
def constitution_check() -> None:
    settings = get_settings()
    result = Constitution(settings.root, settings.state_root).check()
    print_json(result)
    if not result["ok"]:
        raise typer.Exit(code=1)


@constitution_app.command("update-proposal")
def constitution_update_proposal() -> None:
    settings = get_settings()
    typer.echo(Constitution(settings.root, settings.state_root).update_proposal())


def _codex_adapter() -> CodexHarnessAdapter:
    conn = _conn()
    settings = get_settings()
    return CodexHarnessAdapter(conn, settings.root, load_codex_config(settings.root))


@codex_app.command("status")
def codex_status() -> None:
    status = _codex_adapter().status()
    print(f"Codex harness: mode={status['mode']} enabled={status['enabled']} fail_closed={status['fail_closed']}")


@codex_app.command("bind")
def codex_bind(task_id: str) -> None:
    binding = _codex_adapter().bind_task(task_id)
    print(f"Task collegata a thread Codex: {binding.thread.id}")


@codex_app.command("resume")
def codex_resume(task_id: str) -> None:
    result = _codex_adapter().resume_thread(task_id)
    print(f"Ripresa Codex: {result.status}. {result.summary}")


@codex_app.command("run")
def codex_run(task_id: str, dry_run: Annotated[bool, typer.Option("--dry-run")] = True) -> None:
    result = _codex_adapter().run_task(task_id, dry_run=dry_run)
    print(f"Esecuzione Codex: {result.status}. {result.summary}")


@codex_app.command("threads")
def codex_threads() -> None:
    threads = _codex_adapter().list_threads()
    if not threads:
        print("Nessun thread Codex collegato.")
        return
    for thread in threads:
        print(f"{thread.id} | task={thread.task_id} | {thread.title}")


@codex_app.command("export-context")
def codex_export_context(task_id: str) -> None:
    print_json(_codex_adapter().export_context(task_id))


@costs_app.command("estimate")
def costs_estimate(task_id: str) -> None:
    conn, _, _, tasks = _services()
    estimate = CostEstimator().estimate(tasks.get(task_id))
    UsageLogService(conn).record(
        UsageLog(
            task_id=task_id,
            file_reads=estimate.estimated_file_reads,
            subagents=estimate.estimated_subagents,
            tool_calls=estimate.estimated_tool_calls,
            output_lines=estimate.estimated_output_lines,
            estimated=True,
        )
    )
    print_json(estimate.model_dump())


@costs_app.command("budget")
def costs_budget(task_id: str) -> None:
    _, _, _, tasks = _services()
    task = tasks.get(task_id)
    print_json(task.token_budget or {})


@costs_app.command("set-profile")
def costs_set_profile(task_id: str, profile: str) -> None:
    _, _, _, tasks = _services()
    if profile not in {"trivial", "normal", "complex", "expensive"}:
        raise typer.BadParameter("Profilo valido: trivial|normal|complex|expensive")
    task = tasks.get(task_id)
    task.cost_profile = profile  # type: ignore[assignment]
    task.token_budget = budget_for_profile(task.id, task.cost_profile).model_dump()
    tasks.save(task)
    if profile == "expensive":
        print("Profilo expensive: richiede piano e approvazione esplicita prima dell'esecuzione.")
    print_json({"task_id": task.id, "cost_profile": task.cost_profile, "token_budget": task.token_budget})


@costs_app.command("report")
def costs_report() -> None:
    print_json(UsageLogService(_conn()).report())


@costs_app.command("optimize")
def costs_optimize(task_id: str) -> None:
    _, _, _, tasks = _services()
    task = tasks.get(task_id)
    if not task.token_budget:
        task.token_budget = budget_for_profile(task.id, task.cost_profile or "normal").model_dump()
        tasks.save(task)
    logs = [log for log in UsageLogService(_conn()).list() if log.task_id == task_id]
    decision = CostOptimizer().optimize(budget_for_profile(task.id, task.cost_profile or "normal"), logs)
    print_json(decision.model_dump())


@agent_app.command("intake")
def agent_intake(
    message: str,
    json_output: Annotated[bool, typer.Option("--json", help="Stampa JSON invece di Markdown.")] = False,
) -> None:
    """Trasforma un messaggio libero in task, piano, dry-run, approval e follow-up."""
    conn, _, memory, tasks = _services()
    result = AgentIntakeService(conn, memory, tasks).intake(message)
    if json_output:
        print_json(result)
    else:
        typer.echo(result["markdown"])


@memory_app.command("add")
def memory_add(
    text: Annotated[str, typer.Option("--text")],
    type: Annotated[str, typer.Option("--type")],
    area: Annotated[str, typer.Option("--area")],
    confidence: Annotated[str, typer.Option("--confidence")] = "medium",
    source: Annotated[str, typer.Option("--source")] = "user_explicit",
    sensitivity: Annotated[str, typer.Option("--sensitivity")] = "personal",
    scope: Annotated[str, typer.Option("--scope")] = "private_life",
    tags: Annotated[str, typer.Option("--tags")] = "",
) -> None:
    _, _, memory, _ = _services()
    record = MemoryRecord(
        text=text,
        type=type,
        area=area,  # type: ignore[arg-type]
        confidence=confidence,  # type: ignore[arg-type]
        source=source,  # type: ignore[arg-type]
        sensitivity=sensitivity,  # type: ignore[arg-type]
        scope=scope,  # type: ignore[arg-type]
        tags=[t.strip() for t in tags.split(",") if t.strip()],
    )
    memory.add(record)
    print(f"Memoria aggiunta: {record.id}")


@memory_app.command("list")
def memory_list(all: Annotated[bool, typer.Option("--all")] = False) -> None:
    _, _, memory, _ = _services()
    for record in memory.list(active_only=not all):
        print(f"{record.id} | {record.area} | {record.type} | {record.text}")


@memory_app.command("search")
def memory_search(query: str) -> None:
    _, _, memory, _ = _services()
    for record in memory.search(query):
        print(f"{record.id} | {record.area} | {record.text}")


@memory_app.command("export")
def memory_export() -> None:
    _, _, memory, _ = _services()
    print(f"Export creato: {memory.export_markdown()}")


@memory_app.command("review")
def memory_review() -> None:
    _, _, memory, _ = _services()
    for record in memory.review():
        print(f"{record.id} | {record.review_status} | {record.confidence} | {record.text}")


@memory_app.command("compact")
def memory_compact() -> None:
    _, _, memory, _ = _services()
    print(f"Compaction aggiornata: {memory.compact()}")


@memory_app.command("reflect")
def memory_reflect() -> None:
    _, _, memory, _ = _services()
    print(f"Reflection generata: {memory.reflect()}")


@memory_app.command("export-markdown")
def memory_export_markdown() -> None:
    _, _, memory, _ = _services()
    print(f"Export Markdown creato: {memory.export_markdown()}")


@memory_app.command("import-markdown")
def memory_import_markdown(path: Path) -> None:
    _, _, memory, _ = _services()
    records = memory.import_markdown(path)
    print(f"Memorie importate: {len(records)}")


@memory_app.command("diff")
def memory_diff() -> None:
    _, _, memory, _ = _services()
    print_json(memory.diff())


@memory_app.command("stale")
def memory_stale() -> None:
    _, _, memory, _ = _services()
    for record in memory.stale():
        print(f"{record.id} | expires={record.expires_at} | {record.text}")


@memory_app.command("promote-from-task")
def memory_promote_from_task(task_id: str) -> None:
    _, _, memory, _ = _services()
    record = memory.promote_from_task(task_id)
    print(f"Memoria promossa da task in review: {record.id}")


@memory_app.command("deactivate")
def memory_deactivate(memory_id: str) -> None:
    _, _, memory, _ = _services()
    memory.deactivate(memory_id)
    print(f"Memoria disattivata: {memory_id}")


@task_app.command("create")
def task_create(
    title: Annotated[str, typer.Option("--title")],
    area: Annotated[str, typer.Option("--area")],
    goal: Annotated[str, typer.Option("--goal")],
    description: Annotated[str, typer.Option("--description")] = "",
    priority: Annotated[str, typer.Option("--priority")] = "medium",
    autonomy_level: Annotated[str, typer.Option("--autonomy-level")] = "A2",
) -> None:
    _, _, _, tasks = _services()
    task = TaskRecord(
        title=title,
        area=area,
        goal=goal,
        description=description,
        priority=priority,  # type: ignore[arg-type]
        autonomy_level=autonomy_level,  # type: ignore[arg-type]
    )
    tasks.create(task)
    print(f"Task creata: {task.id}")


@task_app.command("list")
def task_list() -> None:
    _, _, _, tasks = _services()
    for task in tasks.list():
        print(f"{task.id} | {task.status} | {task.priority} | {task.title}")


@task_app.command("show")
def task_show(task_id: str) -> None:
    _, _, _, tasks = _services()
    print_json(tasks.get(task_id).model_dump())


@task_app.command("plan")
def task_plan(task_id: str) -> None:
    conn, _, memory, tasks = _services()
    plan = PlanningService(conn, memory, tasks).create_plan(task_id)
    print_json(plan.model_dump())


@task_app.command("execute")
def task_execute(task_id: str, dry_run: Annotated[bool, typer.Option("--dry-run")] = True) -> None:
    conn, _, memory, tasks = _services()
    result = PlanningService(conn, memory, tasks).execute(task_id, dry_run=dry_run)
    print_json(result)


@task_app.command("update-status")
def task_update_status(task_id: str, status: str) -> None:
    _, _, _, tasks = _services()
    tasks.update_status(task_id, status)
    print(f"Stato aggiornato: {task_id} -> {status}")


@task_app.command("add-note")
def task_add_note(task_id: str, note: str) -> None:
    _, _, _, tasks = _services()
    tasks.add_note(task_id, note)
    print("Nota aggiunta.")


@task_app.command("close")
def task_close(task_id: str) -> None:
    _, _, _, tasks = _services()
    tasks.update_status(task_id, "done")
    print(f"Task chiusa: {task_id}")


@task_app.command("archive")
def task_archive(task_id: str) -> None:
    _, _, _, tasks = _services()
    tasks.update_status(task_id, "archived")
    print(f"Task archiviata: {task_id}")


@skills_app.command("list")
def skills_list() -> None:
    for skill in SkillService().list():
        print(f"{skill.id} | {skill.name} | max {skill.max_autonomy_level}")


@skills_app.command("show")
def skills_show(skill_id: str) -> None:
    print_json(SkillService().get(skill_id).manifest.model_dump())


@skills_app.command("match")
def skills_match(task_id: str) -> None:
    _, _, _, tasks = _services()
    skill = SkillService().match(tasks.get(task_id))
    print(f"Skill consigliata: {skill.manifest.id} - {skill.manifest.name}")


@skills_app.command("export")
def skills_export(
    target: Annotated[Path, typer.Option("--target")],
    skill: Annotated[str | None, typer.Option("--skill")] = None,
) -> None:
    exported = SkillExporter(target).export(skill)
    for path in exported:
        print(f"Skill esportata: {path}")


@skills_app.command("validate")
def skills_validate() -> None:
    result = validate_exportable_manifests()
    print_json(result)
    if any(errors for errors in result.values()):
        raise typer.Exit(code=1)


@skills_app.command("build")
def skills_build() -> None:
    result = validate_exportable_manifests()
    if any(errors for errors in result.values()):
        print_json(result)
        raise typer.Exit(code=1)
    print("Skill build OK: manifest esportabili validi.")


@approvals_app.command("list")
def approvals_list(status: Annotated[str | None, typer.Option("--status")] = None) -> None:
    service = ApprovalService(_conn())
    for approval in service.list(status):
        print(f"{approval.id} | {approval.status} | {approval.action_type} | {approval.title}")


@approvals_app.command("show")
def approvals_show(approval_id: str) -> None:
    print_json(ApprovalService(_conn()).get(approval_id).model_dump())


@approvals_app.command("approve")
def approvals_approve(
    approval_id: str, notes: Annotated[str | None, typer.Option("--notes")] = None
) -> None:
    ApprovalService(_conn()).approve(approval_id, notes)
    print(f"Approvazione concessa: {approval_id}")


@approvals_app.command("reject")
def approvals_reject(
    approval_id: str, notes: Annotated[str | None, typer.Option("--notes")] = None
) -> None:
    ApprovalService(_conn()).reject(approval_id, notes)
    print(f"Approvazione rifiutata: {approval_id}")


@followups_app.command("list")
def followups_list(status: Annotated[str | None, typer.Option("--status")] = None) -> None:
    for followup in FollowupService(_conn()).list(status):
        print(f"{followup.id} | {followup.status} | {followup.due_date} | {followup.title}")


@followups_app.command("due")
def followups_due() -> None:
    for followup in FollowupService(_conn()).due():
        print(f"{followup.id} | {followup.due_date} | {followup.title}")


@followups_app.command("complete")
def followups_complete(followup_id: str) -> None:
    FollowupService(_conn()).complete(followup_id)
    print(f"Follow-up completato: {followup_id}")


@followups_app.command("cancel")
def followups_cancel(followup_id: str) -> None:
    FollowupService(_conn()).cancel(followup_id)
    print(f"Follow-up cancellato: {followup_id}")


@logs_app.command("list")
def logs_list() -> None:
    for log in AuditService(_conn()).list():
        print(f"{log['id']} | {log['timestamp']} | {log['event_type']} | {log['summary']}")


@logs_app.command("show")
def logs_show(log_id: str) -> None:
    print_json(AuditService(_conn()).show(log_id) or {})


def print_json(data: object) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


def load_yaml_task(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))
