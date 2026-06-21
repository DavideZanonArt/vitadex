from __future__ import annotations

# ruff: noqa: B008
import secrets
import sqlite3
from collections.abc import AsyncIterator, Generator
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response, StreamingResponse

from private_os.core.config import Settings, get_settings
from private_os.core.db import connect, init_db
from private_os.web.knowledge import KnowledgeIndex, KnowledgeScope, KnowledgeSource
from private_os.web.read_model import EntityKind, PrivateOpsReadModel
from private_os.web.stream import stream_dashboard

SESSION_COOKIE_NAME = "private_os_session"
ACCESS_TOKEN_QUERY_PARAM = "access_token"


def create_web_app(
    *,
    root: Path | None = None,
    state_root: Path | None = None,
    db_path: Path | None = None,
    access_token: str | None = None,
) -> FastAPI:
    settings = _resolve_settings(root=root, state_root=state_root, db_path=db_path)
    session_token = access_token or secrets.token_urlsafe(32)
    app = FastAPI(
        title="Private Ops Dashboard API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
    )
    app.state.access_token = session_token

    def get_conn() -> Generator[sqlite3.Connection, None, None]:
        conn = connect(settings.db_path)
        init_db(conn)
        try:
            yield conn
        finally:
            conn.close()

    def get_read_model(conn: sqlite3.Connection = Depends(get_conn)) -> PrivateOpsReadModel:
        return PrivateOpsReadModel(conn, settings.state_root, settings.db_path)

    def get_knowledge_index() -> KnowledgeIndex:
        return KnowledgeIndex(
            public_root=settings.root,
            state_root=settings.state_root,
            memory_root=settings.memory_dir,
            workspace_root=settings.workspace_dir,
        )

    def require_web_access(request: Request) -> None:
        if _is_authorized(request, session_token):
            return
        raise HTTPException(status_code=401, detail="Access token required")

    @app.get("/api/dashboard/snapshot", dependencies=[Depends(require_web_access)])
    def dashboard_snapshot(read_model: PrivateOpsReadModel = Depends(get_read_model)) -> dict[str, object]:
        return read_model.dashboard_snapshot()

    @app.get("/api/operations", dependencies=[Depends(require_web_access)])
    def operations(
        kind: EntityKind | None = Query(default=None),
        status: str | None = Query(default=None),
        search: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
        read_model: PrivateOpsReadModel = Depends(get_read_model),
    ) -> dict[str, object]:
        items = read_model.operations(kind=kind, status=status, search=search, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/knowledge/snapshot", dependencies=[Depends(require_web_access)])
    def knowledge_snapshot(knowledge_index: KnowledgeIndex = Depends(get_knowledge_index)) -> dict[str, object]:
        return knowledge_index.snapshot()

    @app.get("/api/knowledge/items", dependencies=[Depends(require_web_access)])
    def knowledge_items(
        scope: KnowledgeScope | None = Query(default=None),
        source: KnowledgeSource | None = Query(default=None),
        search: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
        knowledge_index: KnowledgeIndex = Depends(get_knowledge_index),
    ) -> dict[str, object]:
        items = knowledge_index.items(scope=scope, source=source, search=search, limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/knowledge/content", dependencies=[Depends(require_web_access)])
    def knowledge_content(
        item_id: str = Query(...),
        knowledge_index: KnowledgeIndex = Depends(get_knowledge_index),
    ) -> dict[str, object]:
        try:
            return knowledge_index.content(item_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Malformed knowledge item identifier") from exc
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Knowledge item not found") from exc

    @app.get("/api/stream", dependencies=[Depends(require_web_access)])
    async def stream(once: bool = Query(default=False)) -> StreamingResponse:
        async def event_stream() -> AsyncIterator[str]:
            conn = connect(settings.db_path)
            init_db(conn)
            try:
                read_model = PrivateOpsReadModel(conn, settings.state_root, settings.db_path)
                async for chunk in stream_dashboard(read_model, once=once):
                    yield chunk
            finally:
                conn.close()

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    @app.get("/api/entities/{kind}/{entity_id}", dependencies=[Depends(require_web_access)])
    def entity(
        kind: EntityKind,
        entity_id: str,
        read_model: PrivateOpsReadModel = Depends(get_read_model),
    ) -> dict[str, object]:
        try:
            return read_model.entity(kind, entity_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Entity not found: {kind}/{entity_id}") from exc

    @app.get("/api/health", dependencies=[Depends(require_web_access)])
    def health(read_model: PrivateOpsReadModel = Depends(get_read_model)) -> JSONResponse:
        return JSONResponse(
            {
                "ok": True,
                "mode": "read_only",
                "signature": read_model.snapshot_signature(),
            }
        )

    frontend_dist = settings.root / "dashboard-web" / "dist"
    if frontend_dist.exists():
        @app.get("/", include_in_schema=False)
        def web_root(request: Request) -> Response:
            bootstrap = _bootstrap_session(request, session_token)
            if bootstrap:
                return bootstrap
            if not _is_authorized(request, session_token):
                raise HTTPException(status_code=401, detail="Access token required")
            return FileResponse(frontend_dist / "index.html")

        @app.get("/{full_path:path}", include_in_schema=False)
        def web_assets(full_path: str, request: Request) -> Response:
            bootstrap = _bootstrap_session(request, session_token)
            if bootstrap:
                return bootstrap
            if not _is_authorized(request, session_token):
                raise HTTPException(status_code=401, detail="Access token required")
            candidate = frontend_dist / full_path
            if full_path and candidate.exists() and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(frontend_dist / "index.html")

    return app


def _resolve_settings(*, root: Path | None, state_root: Path | None, db_path: Path | None) -> Settings:
    settings = get_settings(root)
    effective_state_root = state_root.resolve() if state_root is not None else settings.state_root
    data_dir = effective_state_root / settings.data_dir.name
    logs_dir = effective_state_root / settings.logs_dir.name
    memory_dir = effective_state_root / settings.memory_dir.name
    workspace_dir = effective_state_root / settings.workspace_dir.name
    effective_db_path = (data_dir / settings.db_path.name) if db_path is None else db_path.resolve()
    if db_path is None:
        return Settings(
            root=settings.root,
            state_root=effective_state_root,
            data_dir=data_dir,
            logs_dir=logs_dir,
            memory_dir=memory_dir,
            workspace_dir=workspace_dir,
            db_path=effective_db_path,
            safe_mode=settings.safe_mode,
            language=settings.language,
            allowed_root=settings.allowed_root,
        )
    return Settings(
        root=settings.root,
        state_root=effective_state_root,
        data_dir=data_dir,
        logs_dir=logs_dir,
        memory_dir=memory_dir,
        workspace_dir=workspace_dir,
        db_path=effective_db_path,
        safe_mode=settings.safe_mode,
        language=settings.language,
        allowed_root=settings.allowed_root,
    )


def _is_authorized(request: Request, access_token: str) -> bool:
    bearer = request.headers.get("Authorization", "")
    if bearer.startswith("Bearer "):
        provided = bearer.removeprefix("Bearer ").strip()
        if secrets.compare_digest(provided, access_token):
            return True
    cookie_value = request.cookies.get(SESSION_COOKIE_NAME, "")
    if cookie_value and secrets.compare_digest(cookie_value, access_token):
        return True
    return False


def _bootstrap_session(request: Request, access_token: str) -> RedirectResponse | None:
    provided = request.query_params.get(ACCESS_TOKEN_QUERY_PARAM)
    if not provided or not secrets.compare_digest(provided, access_token):
        return None
    response = RedirectResponse(url=request.url.path or "/", status_code=307)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        access_token,
        httponly=True,
        samesite="strict",
        secure=False,
        path="/",
        max_age=8 * 60 * 60,
    )
    return response
