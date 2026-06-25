# Vertical Dashboard IA + Tasks Kanban Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the dashboard into more useful vertical pages and ship a dedicated `Tasks` page with a kanban workflow built on top of the existing local operations data.

**Architecture:** Keep the current FastAPI and Zustand data flow intact, but stop treating `Operations` as the primary working surface. Add a dedicated task slice in the frontend store, derive kanban columns from task statuses in a small utility module, and expose the new structure through the main app navigation: `Home`, `Tasks`, `Knowledge`, and `All items`. Leave `Approvals`, `Follow-ups`, and `Logs` for later plans so this slice stays front-end only and shippable in one pass.

**Tech Stack:** React, TypeScript, Zustand, React Router, Vitest, Testing Library, Tailwind CSS

---

## File Map

- Modify: `dashboard-web/src/App.tsx`
- Modify: `dashboard-web/src/App.test.tsx`
- Modify: `dashboard-web/src/components/AppShell.tsx`
- Modify: `dashboard-web/src/store/useOpsStore.ts`
- Create: `dashboard-web/src/lib/task-board.ts`
- Create: `dashboard-web/src/lib/task-board.test.ts`
- Create: `dashboard-web/src/components/TaskFilters.tsx`
- Create: `dashboard-web/src/components/TaskColumn.tsx`
- Create: `dashboard-web/src/components/TaskBoard.tsx`
- Create: `dashboard-web/src/pages/TasksPage.tsx`
- Modify: `dashboard-web/src/pages/DashboardPage.tsx`
- Modify: `dashboard-web/src/pages/OperationsPage.tsx`

## Scope Notes

- This plan intentionally does **not** split `Approvals`, `Follow-ups`, or `Logs` into their own routes yet.
- `Tasks` becomes the first true vertical work surface.
- `Operations` remains available as a fallback audit page, renamed in navigation and copy to `All items`.

## Task 1: Lock the new information architecture in tests and routes

**Files:**
- Modify: `dashboard-web/src/App.tsx`
- Modify: `dashboard-web/src/App.test.tsx`
- Modify: `dashboard-web/src/components/AppShell.tsx`
- Test: `dashboard-web/src/App.test.tsx`

- [ ] **Step 1: Write the failing route and navigation tests**

```tsx
it.each([
  ['/', 'Everything that matters, without the noise.'],
  ['/tasks', 'Task board'],
  ['/operations', 'Unified list'],
])('renders %s without crashing', (path, heading) => {
  render(
    <MemoryRouter initialEntries={[path]}>
      <AppShell connection="connected">
        <AppRoutes />
      </AppShell>
    </MemoryRouter>,
  )

  expect(screen.getByText(heading)).toBeInTheDocument()
})

it('shows the new vertical navigation labels', () => {
  render(<App />)

  expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /tasks/i })).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /knowledge/i })).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /all items/i })).toBeInTheDocument()
  expect(screen.queryByRole('link', { name: /dashboard/i })).not.toBeInTheDocument()
})
```

- [ ] **Step 2: Run the route test to verify it fails**

Run: `npx vitest run src/App.test.tsx --reporter=verbose`

Expected: FAIL because `/tasks` is not defined and the sidebar still renders `Dashboard` and `Operations`.

- [ ] **Step 3: Implement the minimal route and navigation changes**

```tsx
// src/App.tsx
import TasksPage from '@/pages/TasksPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/tasks" element={<TasksPage />} />
      <Route path="/knowledge" element={<KnowledgePage />} />
      <Route path="/operations" element={<OperationsPage />} />
    </Routes>
  )
}
```

```tsx
// src/components/AppShell.tsx
const links = [
  { to: '/', label: 'Home', icon: Activity, end: true },
  { to: '/tasks', label: 'Tasks', icon: KanbanSquare },
  { to: '/knowledge', label: 'Knowledge', icon: BookOpenText },
  { to: '/operations', label: 'All items', icon: PanelLeftOpen },
]
```

- [ ] **Step 4: Run the route test to verify it passes**

Run: `npx vitest run src/App.test.tsx --reporter=verbose`

Expected: PASS with the new `/tasks` route and navigation labels visible.

- [ ] **Step 5: Commit**

```bash
git add dashboard-web/src/App.tsx dashboard-web/src/App.test.tsx dashboard-web/src/components/AppShell.tsx
git commit -m "feat: add vertical dashboard navigation"
```

## Task 2: Add a dedicated task board model and tests

**Files:**
- Create: `dashboard-web/src/lib/task-board.ts`
- Create: `dashboard-web/src/lib/task-board.test.ts`
- Modify: `dashboard-web/src/store/useOpsStore.ts`
- Test: `dashboard-web/src/lib/task-board.test.ts`

- [ ] **Step 1: Write the failing tests for status-to-column mapping and filtering**

```ts
import { describe, expect, it } from 'vitest'

import { buildTaskColumns, normalizeTaskStatus } from '@/lib/task-board'
import type { UnifiedItem } from '@/types'

const tasks: UnifiedItem[] = [
  { id: 't-1', kind: 'task', title: 'Inbox item', status: 'pending', updatedAt: '2026-06-21T10:00:00+00:00', tags: ['ops'], preview: 'triage me' },
  { id: 't-2', kind: 'task', title: 'Active item', status: 'active', updatedAt: '2026-06-21T10:00:00+00:00', tags: ['ops'], preview: 'do now' },
  { id: 't-3', kind: 'task', title: 'Blocked item', status: 'blocked', updatedAt: '2026-06-21T10:00:00+00:00', tags: ['ops'], preview: 'waiting dependency' },
]

describe('task board helpers', () => {
  it('normalizes backend statuses into kanban columns', () => {
    expect(normalizeTaskStatus('pending')).toBe('inbox')
    expect(normalizeTaskStatus('active')).toBe('active')
    expect(normalizeTaskStatus('waiting')).toBe('waiting')
    expect(normalizeTaskStatus('blocked')).toBe('blocked')
    expect(normalizeTaskStatus('done')).toBe('done')
  })

  it('builds ordered task columns from raw task items', () => {
    const columns = buildTaskColumns(tasks)

    expect(columns.map((column) => column.id)).toEqual(['inbox', 'active', 'waiting', 'blocked', 'done'])
    expect(columns.find((column) => column.id === 'inbox')?.items).toHaveLength(1)
    expect(columns.find((column) => column.id === 'blocked')?.items[0].title).toBe('Blocked item')
  })
})
```

- [ ] **Step 2: Run the helper test to verify it fails**

Run: `npx vitest run src/lib/task-board.test.ts --reporter=verbose`

Expected: FAIL because `task-board.ts` does not exist yet.

- [ ] **Step 3: Implement the minimal helper module and store task slice**

```ts
// src/lib/task-board.ts
import type { UnifiedItem } from '@/types'

export type TaskColumnId = 'inbox' | 'active' | 'waiting' | 'blocked' | 'done'

export function normalizeTaskStatus(status: string): TaskColumnId {
  if (status === 'active') return 'active'
  if (status === 'waiting') return 'waiting'
  if (status === 'blocked') return 'blocked'
  if (status === 'done') return 'done'
  return 'inbox'
}

export function buildTaskColumns(items: UnifiedItem[]) {
  const orderedIds: TaskColumnId[] = ['inbox', 'active', 'waiting', 'blocked', 'done']
  return orderedIds.map((id) => ({
    id,
    label: id[0].toUpperCase() + id.slice(1),
    items: items.filter((item) => normalizeTaskStatus(item.status) === id),
  }))
}
```

```ts
// src/store/useOpsStore.ts
type TaskFilters = {
  status: 'all' | 'inbox' | 'active' | 'waiting' | 'blocked' | 'done'
  search: string
}

type OpsState = {
  tasks: UnifiedItem[]
  taskFilters: TaskFilters
  setTaskFilters: (filters: Partial<TaskFilters>) => void
  refreshTasks: () => Promise<void>
}
```

```ts
// src/store/useOpsStore.ts
const defaultTaskFilters: TaskFilters = {
  status: 'all',
  search: '',
}

refreshTasks: async () => {
  const { taskFilters } = get()
  const params = new URLSearchParams({ kind: 'task' })
  if (taskFilters.search) params.set('search', taskFilters.search)
  const response = await fetchJson<PaginatedItems>(`/api/operations?${params.toString()}`)
  set({ tasks: response.items, error: null })
},
```

- [ ] **Step 4: Run the helper test to verify it passes**

Run: `npx vitest run src/lib/task-board.test.ts --reporter=verbose`

Expected: PASS with deterministic column ordering.

- [ ] **Step 5: Commit**

```bash
git add dashboard-web/src/lib/task-board.ts dashboard-web/src/lib/task-board.test.ts dashboard-web/src/store/useOpsStore.ts
git commit -m "feat: add task board state model"
```

## Task 3: Build the Tasks kanban page with focused filters and detail panel

**Files:**
- Create: `dashboard-web/src/components/TaskFilters.tsx`
- Create: `dashboard-web/src/components/TaskColumn.tsx`
- Create: `dashboard-web/src/components/TaskBoard.tsx`
- Create: `dashboard-web/src/pages/TasksPage.tsx`
- Modify: `dashboard-web/src/App.test.tsx`
- Test: `dashboard-web/src/App.test.tsx`

- [ ] **Step 1: Write the failing UI test for the kanban work surface**

```tsx
it('renders the tasks route as a kanban work surface', () => {
  mockedStore.tasks = [
    { id: 'task-1', kind: 'task', title: 'Inbox task', status: 'pending', updatedAt: '2026-06-21T10:00:00+00:00', tags: ['ops'], preview: 'triage me' },
    { id: 'task-2', kind: 'task', title: 'Blocked task', status: 'blocked', updatedAt: '2026-06-21T10:00:00+00:00', tags: ['ops'], preview: 'waiting reply' },
  ]

  render(
    <MemoryRouter initialEntries={['/tasks']}>
      <AppShell connection="connected">
        <AppRoutes />
      </AppShell>
    </MemoryRouter>,
  )

  expect(screen.getByRole('heading', { name: /task board/i })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: /inbox/i })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: /blocked/i })).toBeInTheDocument()
  expect(screen.getByText('Inbox task')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the UI test to verify it fails**

Run: `npx vitest run src/App.test.tsx --reporter=verbose`

Expected: FAIL because `TasksPage` and kanban components do not exist yet.

- [ ] **Step 3: Implement the minimal kanban components and page**

```tsx
// src/components/TaskColumn.tsx
import { UnifiedList } from '@/components/UnifiedList'
import type { UnifiedItem } from '@/types'

type TaskColumnProps = {
  title: string
  items: UnifiedItem[]
  selectedId?: string
  onSelect: (item: UnifiedItem) => void
}

export function TaskColumn({ title, items, selectedId, onSelect }: TaskColumnProps) {
  return (
    <section className="min-w-[280px] rounded-[28px] border border-black/8 bg-white/88 p-4">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-serif text-xl text-black/82">{title}</h2>
        <span className="text-xs text-black/45">{items.length}</span>
      </div>
      <UnifiedList items={items} selectedId={selectedId} emptyLabel={`No tasks in ${title}.`} onSelect={onSelect} />
    </section>
  )
}
```

```tsx
// src/pages/TasksPage.tsx
import { useEffect, useMemo } from 'react'

import { EntityDetail } from '@/components/EntityDetail'
import { SectionFrame } from '@/components/SectionFrame'
import { TaskBoard } from '@/components/TaskBoard'
import { TaskFilters } from '@/components/TaskFilters'
import { buildTaskColumns } from '@/lib/task-board'
import { useOpsStore } from '@/store/useOpsStore'

export default function TasksPage() {
  const tasks = useOpsStore((state) => state.tasks)
  const taskFilters = useOpsStore((state) => state.taskFilters)
  const selectedEntity = useOpsStore((state) => state.selectedEntity)
  const refreshTasks = useOpsStore((state) => state.refreshTasks)
  const selectEntity = useOpsStore((state) => state.selectEntity)
  const setTaskFilters = useOpsStore((state) => state.setTaskFilters)

  useEffect(() => {
    void refreshTasks()
  }, [refreshTasks, taskFilters.search])

  const columns = useMemo(() => buildTaskColumns(tasks), [tasks])

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(360px,0.7fr)]">
      <SectionFrame eyebrow="Tasks" title="Task board" subtitle="Kanban view for the work that actually needs motion.">
        <TaskFilters filters={taskFilters} onChange={setTaskFilters} />
        <TaskBoard columns={columns} selectedId={selectedEntity?.id} onSelect={(item) => void selectEntity(item.kind, item.id)} />
      </SectionFrame>
      <EntityDetail entity={selectedEntity} />
    </div>
  )
}
```

- [ ] **Step 4: Run the UI test to verify it passes**

Run: `npx vitest run src/App.test.tsx --reporter=verbose`

Expected: PASS with `Task board`, kanban columns, and task cards visible on `/tasks`.

- [ ] **Step 5: Commit**

```bash
git add dashboard-web/src/components/TaskFilters.tsx dashboard-web/src/components/TaskColumn.tsx dashboard-web/src/components/TaskBoard.tsx dashboard-web/src/pages/TasksPage.tsx dashboard-web/src/App.test.tsx
git commit -m "feat: add tasks kanban page"
```

## Task 4: Reframe the remaining pages around the new navigation model

**Files:**
- Modify: `dashboard-web/src/pages/DashboardPage.tsx`
- Modify: `dashboard-web/src/pages/OperationsPage.tsx`
- Modify: `dashboard-web/src/App.test.tsx`
- Test: `dashboard-web/src/App.test.tsx`

- [ ] **Step 1: Write the failing copy tests for `Home` and `All items`**

```tsx
it('keeps the home page focused on overview instead of being the primary work surface', () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <AppShell connection="connected">
        <AppRoutes />
      </AppShell>
    </MemoryRouter>,
  )

  expect(screen.getByText(/overview of priorities, decisions, context, and health/i)).toBeInTheDocument()
})

it('relabels operations as all items for audit workflows', () => {
  render(
    <MemoryRouter initialEntries={['/operations']}>
      <AppShell connection="connected">
        <AppRoutes />
      </AppShell>
    </MemoryRouter>,
  )

  expect(screen.getByRole('heading', { name: /all items/i })).toBeInTheDocument()
  expect(screen.getByText(/cross-entity audit surface/i)).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the copy test to verify it fails**

Run: `npx vitest run src/App.test.tsx --reporter=verbose`

Expected: FAIL because the existing pages still speak as `Dashboard` and `Unified list`.

- [ ] **Step 3: Implement the minimal copy and layout reframing**

```tsx
// src/pages/DashboardPage.tsx
<p className="text-[11px] uppercase tracking-[0.26em] text-black/35">Home</p>
<p className="mt-3 max-w-2xl text-sm leading-7 text-black/48">
  Overview of priorities, decisions, context, and health across the local system.
</p>
```

```tsx
// src/pages/OperationsPage.tsx
<SectionFrame
  eyebrow="All items"
  title="All items"
  subtitle="Cross-entity audit surface for tasks, approvals, follow-ups, panels, and logs."
>
```

- [ ] **Step 4: Run the copy test to verify it passes**

Run: `npx vitest run src/App.test.tsx --reporter=verbose`

Expected: PASS with the new framing text visible on both routes.

- [ ] **Step 5: Commit**

```bash
git add dashboard-web/src/pages/DashboardPage.tsx dashboard-web/src/pages/OperationsPage.tsx dashboard-web/src/App.test.tsx
git commit -m "feat: reframe home and audit pages"
```

## Final Verification

- [ ] Run: `npx vitest run --reporter=dot`
- [ ] Run: `npm run build`
- [ ] Open the app locally and verify:
  - `Home` stays overview-only
  - `Tasks` shows kanban columns in the order `Inbox`, `Active`, `Waiting`, `Blocked`, `Done`
  - selecting a card opens the right detail panel
  - `Knowledge` remains unchanged
  - `All items` still supports cross-entity audit filters

## Follow-Up Plans

- Separate plan for `Approvals` page with queue UX
- Separate plan for `Follow-ups` page with timeline/calendar view
- Separate plan for `Logs` page with high-density trail and source filters
