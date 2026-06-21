from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from private_os.core.db import connect, init_db
from private_os.models.approval import ApprovalRecord
from private_os.models.followup import FollowupRecord
from private_os.models.task import TaskRecord
from private_os.panels.base import Panel
from private_os.services.approval_service import ApprovalService
from private_os.services.audit_service import AuditService
from private_os.services.followup_service import FollowupService
from private_os.services.panel_service import PanelService
from private_os.services.task_service import TaskService
from private_os.web.app import create_web_app


def _client(tmp_path: Path, db_path: Path, *, access_token: str = "test-token") -> TestClient:
    client = TestClient(create_web_app(root=tmp_path, db_path=db_path, access_token=access_token))
    client.cookies.set("private_os_session", access_token)
    return client


def _seed_dashboard(root: Path, db_path: Path) -> None:
    conn = connect(db_path)
    init_db(conn)
    task = TaskRecord(
        title="Organize rental documents",
        area="home",
        goal="Gather everything for the landlord submission",
        status="active",
        priority="high",
        missing_info=["Need confirmation of the latest pay slips"],
    )
    TaskService(conn).create(task)
    ApprovalService(conn).create(
        ApprovalRecord(
            task_id=task.id,
            action_type="email_draft",
            title="Landlord email draft",
            description="Review the text before sending",
        )
    )
    FollowupService(conn).create(
        FollowupRecord(
            task_id=task.id,
            title="Follow up with agency",
            due_date="2026-06-21",
            trigger_condition="No reply within 48h",
            action="Prepare a follow-up in English",
        )
    )
    PanelService(conn, root).create(
        Panel(
            title="Rental summary",
            type="note",
            content="Documents collected, only one attachment is missing.",
            related_task_id=task.id,
        )
    )
    AuditService(conn).record("system.snapshot_ready", "Initial snapshot available", task_id=task.id)
    conn.close()


def test_dashboard_snapshot_exposes_summary(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = _client(tmp_path, db_path)

    response = client.get("/api/dashboard/snapshot")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["activeTasks"] == 1
    assert payload["summary"]["pendingApprovals"] == 1
    assert payload["summary"]["dueFollowups"] == 1
    assert payload["health"]["mode"] == "read_only"
    assert payload["priorities"]
    assert payload["timeline"]


def test_operations_support_kind_and_search_filters(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = _client(tmp_path, db_path)

    response = client.get("/api/operations", params={"kind": "approval", "search": "landlord"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["kind"] == "approval"
    assert payload["items"][0]["title"] == "Landlord email draft"


def test_entity_returns_rendered_panel_detail(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = _client(tmp_path, db_path)
    panels_response = client.get("/api/panels")
    panel_id = panels_response.json()["items"][0]["id"]

    response = client.get(f"/api/entities/panel/{panel_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "panel"
    assert "Rental summary" in payload["rendered"]
    assert payload["relatedTaskId"]


def test_stream_emits_initial_health_and_snapshot(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = _client(tmp_path, db_path)

    with client.stream("GET", "/api/stream", params={"once": "true"}) as response:
        chunks: list[str] = []
        for line in response.iter_lines():
            if line:
                chunks.append(line)
            if len(chunks) >= 4:
                break

    joined = "\n".join(chunks)
    assert response.status_code == 200
    assert "event: health" in joined
    assert "event: snapshot:update" in joined
    assert '"mode": "read_only"' in joined


def test_operations_status_filter_orders_by_updated_at_and_honors_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    conn = connect(db_path)
    TaskService(conn).create(
        TaskRecord(
            title="Wait for bank confirmation",
            area="finance",
            goal="Verify the final transfer",
            status="waiting",
            created_at="2026-06-20T08:00:00+00:00",
            updated_at="2026-06-20T08:00:00+00:00",
        )
    )
    TaskService(conn).create(
        TaskRecord(
            title="Wait for signed contract",
            area="home",
            goal="Receive the signed copy of the contract",
            status="waiting",
            created_at="2026-06-21T08:00:00+00:00",
            updated_at="2026-06-21T08:00:00+00:00",
        )
    )
    conn.close()
    client = _client(tmp_path, db_path)

    limited = client.get("/api/operations", params={"kind": "task", "status": "waiting", "limit": 1})
    full = client.get("/api/operations", params={"kind": "task", "status": "waiting", "limit": 2})

    assert limited.status_code == 200
    assert full.status_code == 200
    assert limited.json()["items"][0]["title"] == "Wait for signed contract"
    assert [item["title"] for item in full.json()["items"]] == [
        "Wait for signed contract",
        "Wait for bank confirmation",
    ]


def test_api_requires_authentication(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = TestClient(create_web_app(root=tmp_path, db_path=db_path, access_token="test-token"))

    snapshot_response = client.get("/api/dashboard/snapshot")
    logs_response = client.get("/api/archive/logs")

    assert snapshot_response.status_code == 401
    assert logs_response.status_code == 401


def test_logs_endpoint_and_log_entity_redact_payload_and_preserve_risk_level(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    conn = connect(db_path)
    critical_log = AuditService(conn).record(
        "approval.blocked",
        "Send blocked for final review",
        payload={"channel": "email", "reason": "missing_attachment"},
        risk_level="critical",
    )
    conn.close()
    client = _client(tmp_path, db_path)

    logs_response = client.get("/api/archive/logs", params={"limit": 10})
    entity_response = client.get(f"/api/entities/log/{critical_log['id']}")

    assert logs_response.status_code == 200
    assert entity_response.status_code == 200
    log_item = next(item for item in logs_response.json()["items"] if item["id"] == critical_log["id"])
    assert log_item["id"] == critical_log["id"]
    assert log_item["status"] == "critical"
    assert "missing_attachment" not in log_item["preview"]
    assert "email" not in log_item["preview"]
    assert entity_response.json()["data"]["payload"]["redacted"] is True
    assert entity_response.json()["data"]["payload"]["keys"] == ["channel", "reason"]


def test_health_signature_changes_when_snapshot_changes(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = _client(tmp_path, db_path)

    first_signature = client.get("/api/health").json()["signature"]

    conn = connect(db_path)
    TaskService(conn).create(
        TaskRecord(
            title="New urgent reminder",
            area="bureaucracy",
            goal="Upload a newly requested document",
            status="active",
            created_at="2026-06-21T12:00:00+00:00",
            updated_at="2026-06-21T12:00:00+00:00",
        )
    )
    conn.close()

    second_signature = client.get("/api/health").json()["signature"]

    assert first_signature != second_signature


def test_root_bootstrap_sets_session_cookie_from_access_token(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "private_os.sqlite"
    _seed_dashboard(tmp_path, db_path)
    dist = tmp_path / "dashboard-web" / "dist"
    dist.mkdir(parents=True)
    (dist / "index.html").write_text("INDEX", encoding="utf-8")
    client = TestClient(create_web_app(root=tmp_path, db_path=db_path, access_token="test-token"))

    response = client.get("/?access_token=test-token", follow_redirects=False)

    assert response.status_code == 307
    assert "private_os_session=" in response.headers["set-cookie"]
