# Unified Dashboard Knowledge Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only knowledge hub in the dashboard that exposes curated public docs, personal context, and recent workspace files without weakening filesystem safety.

**Architecture:** Add a dedicated filesystem-backed knowledge index in the FastAPI web layer, then extend the React dashboard with a new `Knowledge` route plus curated home sections. Keep operational entities and knowledge items separate so the existing SQLite-backed operations flow remains unchanged while the new feature reads only from approved roots.

**Tech Stack:** Python, FastAPI, Pydantic, pytest, React, TypeScript, Zustand, Vite, Tailwind CSS

---

## File Map

- Create: `vitadex/web/knowledge.py`
- Modify: `vitadex/web/app.py`
- Modify: `tests/test_web_api.py`
- Modify: `dashboard-web/src/types.ts`
- Modify: `dashboard-web/src/store/useOpsStore.ts`
- Create: `dashboard-web/src/components/ScopeBadge.tsx`
- Create: `dashboard-web/src/components/KnowledgeCard.tsx`
- Create: `dashboard-web/src/components/KnowledgeDetail.tsx`
- Create: `dashboard-web/src/components/KnowledgeList.tsx`
- Create: `dashboard-web/src/pages/KnowledgePage.tsx`
- Modify: `dashboard-web/src/components/AppShell.tsx`
- Modify: `dashboard-web/src/pages/DashboardPage.tsx`
- Modify: `dashboard-web/src/App.tsx`

## Task 1: Add backend tests for knowledge indexing and safety

**Files:**
- Modify: `tests/test_web_api.py`
- Test: `tests/test_web_api.py`

- [ ] **Step 1: Write the failing tests**

```python
def _write_knowledge_fixtures(root: Path) -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "workflows").mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("# Public README\n\nMain repo entrypoint.\n", encoding="utf-8")
    (root / "docs" / "architecture.md").write_text("# Architecture\n\nSystem map.\n", encoding="utf-8")
    (root / "workflows" / "housing-search.md").write_text("# Housing Search\n\nChecklist.\n", encoding="utf-8")
    state_root = root / "state"
    (state_root / "memory").mkdir(parents=True, exist_ok=True)
    (state_root / "workspace" / "notes").mkdir(parents=True, exist_ok=True)
    (state_root / "workspace" / "outputs").mkdir(parents=True, exist_ok=True)
    (state_root / "memory" / "MAINMEMORY.md").write_text("# Main Memory\n\nImportant personal context.\n", encoding="utf-8")
    (state_root / "memory" / "preferences.md").write_text("# Preferences\n\nQuiet places.\n", encoding="utf-8")
    (state_root / "workspace" / "notes" / "today.md").write_text("# Today\n\nFocus list.\n", encoding="utf-8")


def test_knowledge_snapshot_returns_public_and_personal_sections(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "vitadex.sqlite"
    _seed_dashboard(tmp_path, db_path)
    _write_knowledge_fixtures(tmp_path)
    client = _client(tmp_path, db_path)

    response = client.get("/api/knowledge/snapshot")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mainDocs"]
    assert payload["personalContext"]
    assert payload["recentWorkspaceFiles"]
    assert payload["health"]["personalAvailable"] is True


def test_knowledge_items_filters_by_scope_and_search(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "vitadex.sqlite"
    _seed_dashboard(tmp_path, db_path)
    _write_knowledge_fixtures(tmp_path)
    client = _client(tmp_path, db_path)

    response = client.get("/api/knowledge/items", params={"scope": "personal", "search": "quiet"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["scope"] == "personal"
    assert payload["items"][0]["title"] == "Preferences"


def test_knowledge_snapshot_degrades_when_personal_roots_are_missing(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "vitadex.sqlite"
    _seed_dashboard(tmp_path, db_path)
    (tmp_path / "README.md").write_text("# Public README\n", encoding="utf-8")
    client = _client(tmp_path, db_path)

    response = client.get("/api/knowledge/snapshot")

    assert response.status_code == 200
    payload = response.json()
    assert payload["health"]["personalAvailable"] is False
    assert payload["personalContext"] == []


def test_knowledge_content_returns_preview_for_allowed_item(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "vitadex.sqlite"
    _seed_dashboard(tmp_path, db_path)
    _write_knowledge_fixtures(tmp_path)
    client = _client(tmp_path, db_path)
    item_id = client.get("/api/knowledge/items", params={"scope": "public"}).json()["items"][0]["id"]

    response = client.get("/api/knowledge/content", params={"item_id": item_id})

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == item_id
    assert payload["content"]


def test_knowledge_content_rejects_unknown_item_identifier(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "vitadex.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = _client(tmp_path, db_path)

    response = client.get("/api/knowledge/content", params={"item_id": "public:../../secrets.txt"})

    assert response.status_code in {400, 404}
```

- [ ] **Step 2: Run the targeted tests to verify they fail**

Run: `pytest tests/test_web_api.py -k knowledge -v`

Expected: FAIL with missing route assertions such as `404 Not Found` for `/api/knowledge/...`.

- [ ] **Step 3: Add minimal fixture plumbing if the temporary root needs a local state override**

```python
def _client(
    tmp_path: Path,
    db_path: Path,
    *,
    access_token: str = "test-token",
    state_root: Path | None = None,
) -> TestClient:
    client = TestClient(
        create_web_app(
            root=tmp_path,
            state_root=state_root,
            db_path=db_path,
            access_token=access_token,
        )
    )
    client.cookies.set("vitadex_session", access_token)
    return client
```

- [ ] **Step 4: Run the targeted tests again and keep them failing only on missing implementation**

Run: `pytest tests/test_web_api.py -k knowledge -v`

Expected: FAIL on route behavior, not on broken test fixtures.

- [ ] **Step 5: Commit the red tests in an isolated worktree**

```bash
git add tests/test_web_api.py
git commit -m "test: add knowledge hub api coverage"
```

## Task 2: Implement the filesystem-backed knowledge index

**Files:**
- Create: `vitadex/web/knowledge.py`
- Test: `tests/test_web_api.py`

- [ ] **Step 1: Write the failing unit through the existing API tests**

Run: `pytest tests/test_web_api.py -k "knowledge_snapshot or knowledge_items or knowledge_content" -v`

Expected: FAIL because `vitadex.web.knowledge` does not exist and routes are not wired.

- [ ] **Step 2: Create the knowledge index module with approved roots and item models**

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import hashlib


PUBLIC_DOCS = ("README.md", "ROADMAP.md", "CHANGELOG.md", "CONTRIBUTING.md")
PERSONAL_MEMORY = (
    "MAINMEMORY.md",
    "PRIVATE_PROFILE.md",
    "preferences.md",
    "constraints.md",
    "decisions.md",
    "finance.md",
    "health.md",
    "travel.md",
)
WORKSPACE_DIRS = ("notes", "lists", "outputs", "panels")


@dataclass(slots=True)
class KnowledgeItem:
    id: str
    title: str
    scope: str
    source: str
    kind: str
    path: str
    updated_at: str
    tags: list[str]
    preview: str
```

- [ ] **Step 3: Implement safe file discovery and stable identifiers**

```python
def _item_id(scope: str, relative_path: str) -> str:
    digest = hashlib.sha1(f"{scope}:{relative_path}".encode("utf-8")).hexdigest()[:12]
    return f"{scope}:{digest}"


def _resolve_under(root: Path, relative_path: str) -> Path | None:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate if candidate.exists() and candidate.is_file() else None
```

- [ ] **Step 4: Implement snapshot, list, and content helpers**

```python
class KnowledgeIndex:
    def __init__(self, *, public_root: Path, state_root: Path, memory_root: Path, workspace_root: Path):
        self.public_root = public_root
        self.state_root = state_root
        self.memory_root = memory_root
        self.workspace_root = workspace_root

    def snapshot(self) -> dict[str, object]:
        items = self.items(limit=200)
        return {
            "mainDocs": [item for item in items if item["scope"] == "public"][:6],
            "personalContext": [item for item in items if item["source"] == "memory"][:6],
            "recentWorkspaceFiles": [item for item in items if item["source"] == "workspace"][:6],
            "health": self.health(items),
        }
```

- [ ] **Step 5: Run the targeted API tests to verify the backend behavior passes**

Run: `pytest tests/test_web_api.py -k knowledge -v`

Expected: PASS for the new knowledge tests.

- [ ] **Step 6: Commit the backend knowledge index**

```bash
git add vitadex/web/knowledge.py tests/test_web_api.py
git commit -m "feat: add read-only knowledge index"
```

## Task 3: Wire the new knowledge endpoints into the FastAPI app

**Files:**
- Modify: `vitadex/web/app.py`
- Test: `tests/test_web_api.py`

- [ ] **Step 1: Write the failing route-level expectation**

```python
def test_knowledge_routes_require_authentication(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "vitadex.sqlite"
    _seed_dashboard(tmp_path, db_path)
    client = TestClient(create_web_app(root=tmp_path, db_path=db_path, access_token="test-token"))

    assert client.get("/api/knowledge/snapshot").status_code == 401
    assert client.get("/api/knowledge/items").status_code == 401
```

- [ ] **Step 2: Run the focused test to see it fail**

Run: `pytest tests/test_web_api.py -k "knowledge_routes_require_authentication" -v`

Expected: FAIL until the new routes are protected exactly like the existing API.

- [ ] **Step 3: Import and mount the knowledge endpoints**

```python
from vitadex.web.knowledge import KnowledgeIndex


def get_knowledge_index() -> KnowledgeIndex:
    return KnowledgeIndex(
        public_root=settings.root,
        state_root=settings.state_root,
        memory_root=settings.memory_dir,
        workspace_root=settings.workspace_dir,
    )


@app.get("/api/knowledge/snapshot", dependencies=[Depends(require_web_access)])
def knowledge_snapshot() -> dict[str, object]:
    return get_knowledge_index().snapshot()


@app.get("/api/knowledge/items", dependencies=[Depends(require_web_access)])
def knowledge_items(
    scope: str | None = Query(default=None),
    source: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, object]:
    items = get_knowledge_index().items(scope=scope, source=source, search=search, limit=limit)
    return {"items": items, "count": len(items)}


@app.get("/api/knowledge/content", dependencies=[Depends(require_web_access)])
def knowledge_content(item_id: str = Query(...)) -> dict[str, object]:
    return get_knowledge_index().content(item_id)
```

- [ ] **Step 4: Run the whole web API test file**

Run: `pytest tests/test_web_api.py -v`

Expected: PASS, including the new knowledge cases and the existing dashboard API tests.

- [ ] **Step 5: Commit the API wiring**

```bash
git add vitadex/web/app.py tests/test_web_api.py
git commit -m "feat: expose knowledge hub api"
```

## Task 4: Extend frontend types and store for knowledge state

**Files:**
- Modify: `dashboard-web/src/types.ts`
- Modify: `dashboard-web/src/store/useOpsStore.ts`
- Test: `dashboard-web/src/App.test.tsx`

- [ ] **Step 1: Add a lightweight failing route smoke expectation for the new page**

```tsx
it('renders the knowledge route', async () => {
  renderWithRouter('/knowledge')
  expect(await screen.findByText(/knowledge/i)).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the frontend smoke test**

Run: `npm run test -- App.test.tsx`

Expected: FAIL because the route and store state do not exist yet.

- [ ] **Step 3: Add the new shared types**

```ts
export type KnowledgeScope = 'public' | 'personal'
export type KnowledgeSource = 'docs' | 'memory' | 'workspace'

export type KnowledgeItem = {
  id: string
  title: string
  scope: KnowledgeScope
  source: KnowledgeSource
  kind: 'markdown' | 'note' | 'panel'
  path: string
  updatedAt: string
  tags: string[]
  preview: string
}

export type KnowledgeSnapshot = {
  mainDocs: KnowledgeItem[]
  personalContext: KnowledgeItem[]
  recentWorkspaceFiles: KnowledgeItem[]
  health: {
    publicAvailable: boolean
    personalAvailable: boolean
    indexedCount: number
  }
}
```

- [ ] **Step 4: Extend the Zustand store with knowledge fetches and selection**

```ts
type KnowledgeFilters = {
  scope: 'all' | KnowledgeScope
  source: 'all' | KnowledgeSource
  search: string
}

type OpsState = {
  knowledgeSnapshot: KnowledgeSnapshot | null
  knowledgeItems: KnowledgeItem[]
  selectedKnowledgeItem: KnowledgeDetail | null
  knowledgeFilters: KnowledgeFilters
  refreshKnowledgeSnapshot: () => Promise<void>
  refreshKnowledgeItems: () => Promise<void>
  selectKnowledgeItem: (itemId: string) => Promise<void>
}
```

- [ ] **Step 5: Run the frontend smoke test again**

Run: `npm run test -- App.test.tsx`

Expected: still FAIL on missing route or component rendering, but pass type-level compilation for the store changes.

- [ ] **Step 6: Commit the state model changes**

```bash
git add dashboard-web/src/types.ts dashboard-web/src/store/useOpsStore.ts dashboard-web/src/App.test.tsx
git commit -m "feat: add knowledge hub frontend state"
```

## Task 5: Build the Knowledge page and navigation

**Files:**
- Create: `dashboard-web/src/components/ScopeBadge.tsx`
- Create: `dashboard-web/src/components/KnowledgeCard.tsx`
- Create: `dashboard-web/src/components/KnowledgeDetail.tsx`
- Create: `dashboard-web/src/components/KnowledgeList.tsx`
- Create: `dashboard-web/src/pages/KnowledgePage.tsx`
- Modify: `dashboard-web/src/components/AppShell.tsx`
- Modify: `dashboard-web/src/App.tsx`
- Test: `dashboard-web/src/App.test.tsx`

- [ ] **Step 1: Write the failing UI expectation for navigation**

```tsx
it('shows Knowledge in the app navigation', async () => {
  render(<App />)
  expect(await screen.findByRole('link', { name: /knowledge/i })).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the frontend smoke tests**

Run: `npm run test -- App.test.tsx`

Expected: FAIL because the route and link are not mounted yet.

- [ ] **Step 3: Add focused UI components**

```tsx
export function ScopeBadge({ scope }: { scope: 'public' | 'personal' }) {
  return (
    <span className={scope === 'public' ? 'bg-sky-100 text-sky-900' : 'bg-amber-100 text-amber-900'}>
      {scope}
    </span>
  )
}
```

```tsx
export default function KnowledgePage() {
  const snapshot = useOpsStore((state) => state.knowledgeSnapshot)
  const items = useOpsStore((state) => state.knowledgeItems)
  const refreshSnapshot = useOpsStore((state) => state.refreshKnowledgeSnapshot)
  const refreshItems = useOpsStore((state) => state.refreshKnowledgeItems)

  useEffect(() => {
    void Promise.all([refreshSnapshot(), refreshItems()])
  }, [refreshSnapshot, refreshItems])

  return <div className="space-y-6">...</div>
}
```

- [ ] **Step 4: Wire the route and sidebar link**

```tsx
const links = [
  { to: '/', label: 'Dashboard', icon: Activity, end: true },
  { to: '/knowledge', label: 'Knowledge', icon: BookOpen },
  { to: '/operations', label: 'Operations', icon: PanelLeftOpen },
  { to: '/archive', label: 'Archive', icon: Archive },
]
```

```tsx
<Routes>
  <Route path="/" element={<DashboardPage />} />
  <Route path="/knowledge" element={<KnowledgePage />} />
  <Route path="/operations" element={<OperationsPage />} />
  <Route path="/archive" element={<ArchivePage />} />
</Routes>
```

- [ ] **Step 5: Run the frontend smoke tests until they pass**

Run: `npm run test -- App.test.tsx`

Expected: PASS for the navigation and route rendering checks.

- [ ] **Step 6: Commit the new route and components**

```bash
git add dashboard-web/src/components/ScopeBadge.tsx dashboard-web/src/components/KnowledgeCard.tsx dashboard-web/src/components/KnowledgeDetail.tsx dashboard-web/src/components/KnowledgeList.tsx dashboard-web/src/pages/KnowledgePage.tsx dashboard-web/src/components/AppShell.tsx dashboard-web/src/App.tsx dashboard-web/src/App.test.tsx
git commit -m "feat: add knowledge hub page"
```

## Task 6: Integrate curated knowledge sections into the home dashboard

**Files:**
- Modify: `dashboard-web/src/pages/DashboardPage.tsx`
- Modify: `dashboard-web/src/store/useOpsStore.ts`
- Test: `dashboard-web/src/App.test.tsx`

- [ ] **Step 1: Write the failing home-page expectation**

```tsx
it('renders curated knowledge sections on the dashboard', async () => {
  renderWithRouter('/')
  expect(await screen.findByText(/main docs/i)).toBeInTheDocument()
  expect(screen.getByText(/personal context/i)).toBeInTheDocument()
  expect(screen.getByText(/recent workspace/i)).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the route smoke tests**

Run: `npm run test -- App.test.tsx`

Expected: FAIL because the dashboard page does not yet render the new knowledge sections.

- [ ] **Step 3: Fetch the knowledge snapshot alongside the existing dashboard data**

```ts
refreshAll: async () => {
  set({ isLoading: true, error: null })
  try {
    await Promise.all([
      get().refreshSnapshot(),
      get().refreshOperations(),
      get().refreshLogs(),
      get().refreshPanels(),
      get().refreshKnowledgeSnapshot(),
    ])
  } finally {
    set({ isLoading: false })
  }
}
```

- [ ] **Step 4: Render the compact curated sections on `DashboardPage`**

```tsx
<SectionFrame eyebrow="Knowledge" title="Main Docs" subtitle="Core public documents always within reach.">
  <KnowledgeList items={knowledgeSnapshot?.mainDocs ?? []} onSelect={(item) => void selectKnowledgeItem(item.id)} />
</SectionFrame>
```

```tsx
<SectionFrame eyebrow="Personal" title="Personal Context" subtitle="Key local memory files surfaced read-only.">
  <KnowledgeList items={knowledgeSnapshot?.personalContext ?? []} onSelect={(item) => void selectKnowledgeItem(item.id)} />
</SectionFrame>
```

- [ ] **Step 5: Run the frontend smoke tests again**

Run: `npm run test -- App.test.tsx`

Expected: PASS for the new home-section expectation.

- [ ] **Step 6: Commit the dashboard integration**

```bash
git add dashboard-web/src/pages/DashboardPage.tsx dashboard-web/src/store/useOpsStore.ts dashboard-web/src/App.test.tsx
git commit -m "feat: surface curated knowledge on dashboard"
```

## Task 7: Run full validation and document any degraded-mode assumptions

**Files:**
- Modify: `tests/test_web_api.py` if validation reveals gaps
- Modify: `dashboard-web/src/*` only if validation reveals gaps

- [ ] **Step 1: Run backend quality checks**

Run: `pytest`

Expected: PASS for the full Python test suite.

- [ ] **Step 2: Run static analysis for Python**

Run: `ruff check . && mypy vitadex`

Expected: PASS with no new lint or typing regressions.

- [ ] **Step 3: Run frontend checks**

Run: `npm run lint && npm run check && npm run build`

Expected: PASS for lint, type-check, and production build.

- [ ] **Step 4: Fix only validation failures that are caused by the knowledge hub changes**

```python
# Example fix pattern for Python:
def _preview_text(value: str, *, limit: int = 280) -> str:
    return " ".join(value.split())[:limit]
```

```tsx
// Example fix pattern for React:
const emptyLabel = scope === 'personal' ? 'No personal files available.' : 'No documents available.'
```

- [ ] **Step 5: Re-run the failing command until the suite is green**

Run: rerun only the command that failed in steps 1 to 3.

Expected: PASS.

- [ ] **Step 6: Commit the validated final slice**

```bash
git add vitadex/web/knowledge.py vitadex/web/app.py tests/test_web_api.py dashboard-web/src/types.ts dashboard-web/src/store/useOpsStore.ts dashboard-web/src/components/ScopeBadge.tsx dashboard-web/src/components/KnowledgeCard.tsx dashboard-web/src/components/KnowledgeDetail.tsx dashboard-web/src/components/KnowledgeList.tsx dashboard-web/src/pages/KnowledgePage.tsx dashboard-web/src/components/AppShell.tsx dashboard-web/src/pages/DashboardPage.tsx dashboard-web/src/App.tsx dashboard-web/src/App.test.tsx
git commit -m "feat: add unified dashboard knowledge hub"
```

## Self-Review Notes

- Spec coverage: backend indexing, path safety, degraded mode, new route, home integration, and validation all map to explicit tasks.
- Placeholder scan: no `TODO`, `TBD`, or implicit “write tests later” steps remain.
- Type consistency: the plan uses `KnowledgeItem`, `KnowledgeSnapshot`, `KnowledgeDetail`, `knowledgeSnapshot`, `knowledgeItems`, and `selectedKnowledgeItem` consistently across backend and frontend tasks.
