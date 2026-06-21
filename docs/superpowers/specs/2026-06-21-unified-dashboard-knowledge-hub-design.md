# Unified Dashboard Knowledge Hub Design

## Goal

Expand the existing read-only dashboard into a unified knowledge hub that surfaces:

- operational entities already available in the product
- primary open-source documentation from the public repository
- primary personal context from the local state overlay
- recent local workspace files

The first milestone stays strictly read-only and must preserve the separation between public code and personal local data.

## Scope

In scope:

- add read-only backend endpoints for knowledge snapshot, list, and content preview
- index a curated set of public markdown files from the repository
- index a curated set of personal markdown files from the local state overlay
- index recent files from the local workspace overlay
- add a new `Knowledge` page in the dashboard web app
- enrich the home dashboard with high-value knowledge sections
- add clear `public` and `personal` provenance labels in the UI
- add backend tests for indexing, path safety, degraded mode, and preview behavior

Out of scope:

- editing or writing files from the dashboard
- full filesystem browsing outside approved directories
- external actions through Gmail, Telegram, browser, or other tools
- database schema changes
- semantic search, embeddings, or vector indexing
- broad redesign of the operations and archive pages

## Recommended Approach

Use a dedicated read-only knowledge index layered beside the existing operations read model.

Why:

- it fits the current FastAPI plus read-model architecture
- it avoids coupling document indexing to the operational entity model
- it keeps filesystem access narrow, testable, and explicitly permissioned
- it delivers immediate value without expanding the product into a write-capable file manager

## Product Shape

### Information Architecture

The dashboard exposes four top-level surfaces:

- `Dashboard`: summary view with operational metrics and curated knowledge blocks
- `Knowledge`: searchable list of public docs, personal context, and workspace files
- `Operations`: existing operational entity list and filters
- `Archive`: existing logs and generated panels history

### Home Experience

The home page keeps the current hero, metrics, priorities, timeline, and entity detail areas, then adds three curated sections:

- `Main Docs`: high-signal public repository markdown files
- `Personal Context`: high-signal local memory files
- `Recent Workspace`: recently updated local workspace files

Each section shows a small number of items with:

- title
- provenance badge
- source badge
- last update
- short preview

### Knowledge Experience

The `Knowledge` page becomes the broader browsing surface. It includes:

- quick filters for `all`, `public`, `personal`, and source groups
- simple text search across title, tags, path, and preview
- a list of knowledge items
- a detail panel for the selected item

The detail panel shows:

- file title
- provenance and source metadata
- relative path
- updated time
- preview content

## Data Model

Add a dedicated `knowledge item` response shape for the web layer.

Fields:

- `id`: stable identifier derived from scope and relative path
- `title`: human-readable file title
- `scope`: `public` or `personal`
- `source`: `docs`, `memory`, or `workspace`
- `kind`: `markdown`, `note`, or `panel`
- `path`: relative path within the approved root
- `updatedAt`: ISO timestamp from file metadata
- `tags`: lightweight descriptors derived from source and filename
- `preview`: short text excerpt for list rendering

Add a `knowledge snapshot` shape for the home page with:

- `mainDocs`
- `personalContext`
- `recentWorkspaceFiles`
- `health`

The `health` block reports whether the expected public and personal roots are available plus indexing counts.

## Backend Design

### New Read-Only Module

Add a dedicated web-facing knowledge index module that:

- knows the approved roots
- discovers files from a small curated set first
- adds recent workspace files from approved directories
- reads text content safely
- returns degraded but valid responses when personal directories do not exist

This module should not depend on SQLite because its source of truth is the filesystem, not the operational database.

### Approved Paths

Public repository files:

- `README.md`
- `ROADMAP.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `docs/*.md`
- `workflows/*.md`

Personal memory files:

- `memory/MAINMEMORY.md`
- `memory/PRIVATE_PROFILE.md`
- `memory/preferences.md`
- `memory/constraints.md`
- `memory/decisions.md`
- `memory/finance.md`
- `memory/health.md`
- `memory/travel.md`
- additional `memory/*.md` files only when still inside the approved memory directory

Workspace files:

- `workspace/notes/*`
- `workspace/lists/*`
- `workspace/outputs/*`
- `workspace/panels/*`

The implementation must resolve paths and reject anything outside these approved roots.

### API Endpoints

Add:

- `GET /api/knowledge/snapshot`
- `GET /api/knowledge/items`
- `GET /api/knowledge/content`

Behavior:

- `snapshot` returns curated home sections and health data
- `items` returns a filtered list by `scope`, `source`, `search`, and `limit`
- `content` returns one approved file preview selected by stable item identifier, not by arbitrary raw path

All endpoints reuse the existing web access token guard and remain read-only.

### Error Handling

If personal directories are missing:

- return empty personal sections
- keep public docs available
- expose degraded health details instead of raising server errors

If a file disappears between index and preview:

- return `404`

If a caller asks for an item outside the approved set:

- return `404` or `400` depending on whether the identifier is malformed or simply absent from the index

## Frontend Design

### Routing

Add a new route:

- `/knowledge`

Update the app shell navigation to include `Knowledge`.

### Store

Extend the existing Zustand store with:

- `knowledgeSnapshot`
- `knowledgeItems`
- `selectedKnowledgeItem`
- `knowledgeFilters`
- `refreshKnowledgeSnapshot()`
- `refreshKnowledgeItems()`
- `selectKnowledgeItem()`

This keeps knowledge state aligned with the existing fetch and selection pattern already used for operations.

### Components

Add focused components rather than overloading the operational entity components:

- `KnowledgeList`
- `KnowledgeCard`
- `KnowledgeDetail`
- `ScopeBadge`

Reuse existing layout primitives such as `SectionFrame` where possible.

### Home Integration

Update the current home page to render:

- `Main Docs`
- `Personal Context`
- `Recent Workspace`

The sections should stay curated and compact so the dashboard remains a decision surface rather than a file browser.

## Testing Plan

Backend tests should cover:

- indexing public docs
- indexing personal files when present
- degraded snapshot when personal roots are missing
- workspace recent file ordering
- path traversal resistance and root enforcement
- content preview for an allowed file
- not-found behavior for missing or invalid item identifiers

Frontend changes should be validated at minimum through:

- type-check
- lint
- build

Add frontend tests only if the existing dashboard test setup already supports low-cost coverage for the new route and rendering. Do not introduce broad UI test scaffolding as part of this milestone.

## Validation Plan

Run:

- `pytest`
- `ruff check .`
- `mypy private_os`
- `npm run lint`
- `npm run check`
- `npm run build`

## Risks And Mitigations

- Personal data could accidentally bleed into the public repo.
  - Mitigation: read only from local overlay roots, never copy files into versioned directories, and keep tests based on temporary local fixtures.
- Filesystem access could become too broad.
  - Mitigation: use curated roots and stable item identifiers instead of raw path access.
- The home page could become visually overloaded.
  - Mitigation: keep knowledge blocks curated and defer full exploration to the dedicated `Knowledge` page.
- Personal directories may not exist on every machine.
  - Mitigation: support degraded mode and empty states as first-class behavior.

## Success Criteria

- the dashboard exposes a dedicated `Knowledge` page
- the home page surfaces main public docs, personal context, and recent workspace files
- public and personal items are clearly labeled in the UI
- personal directories can be missing without breaking the dashboard
- no write actions or unsafe filesystem access are introduced
- backend and existing quality checks remain green
