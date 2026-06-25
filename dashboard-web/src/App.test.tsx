import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App, { AppRoutes } from '@/App'
import { AppShell } from '@/components/AppShell'

const mockedStore = {
  connection: 'connected' as const,
  snapshot: {
    generatedAt: '2026-06-21T10:00:00+00:00',
    summary: {
      activeTasks: 3,
      pendingApprovals: 2,
      dueFollowups: 1,
      decisionRequests: 1,
      recentEvents: 4,
      panels: 2,
      logs: 5,
    },
    priorities: [],
    timeline: [],
    health: {
      mode: 'read_only' as const,
      realtime: 'connected' as const,
      source: 'local_sqlite' as const,
      workspaceRoot: '/tmp/vitadex-state/workspace',
    },
  },
  knowledgeSnapshot: {
    mainDocs: [
      {
        id: 'doc-1',
        title: 'Architecture',
        scope: 'public' as const,
        source: 'docs' as const,
        kind: 'markdown' as const,
        path: 'docs/architecture.md',
        updatedAt: '2026-06-21T10:00:00+00:00',
        tags: ['public', 'docs'],
        preview: 'System map.',
      },
    ],
    personalContext: [
      {
        id: 'memory-1',
        title: 'Main Memory',
        scope: 'personal' as const,
        source: 'memory' as const,
        kind: 'note' as const,
        path: 'MAINMEMORY.md',
        updatedAt: '2026-06-21T09:00:00+00:00',
        tags: ['personal', 'memory'],
        preview: 'Important personal context.',
      },
    ],
    recentWorkspaceFiles: [
      {
        id: 'workspace-1',
        title: 'Today',
        scope: 'personal' as const,
        source: 'workspace' as const,
        kind: 'note' as const,
        path: 'notes/today.md',
        updatedAt: '2026-06-21T08:00:00+00:00',
        tags: ['personal', 'workspace'],
        preview: 'Focus list.',
      },
    ],
    health: {
      publicAvailable: true,
      personalAvailable: true,
      counts: {
        public: 1,
        personal: 2,
        memory: 1,
        workspace: 1,
        total: 3,
      },
    },
  },
  knowledgeItems: [],
  operations: [],
  selectedEntity: null,
  selectedKnowledgeItem: null,
  filters: { kind: 'all' as const, status: '', search: '' },
  knowledgeFilters: { scope: 'all' as const, source: 'all' as const, search: '' },
  setFilters: vi.fn(),
  setKnowledgeFilters: vi.fn(),
  setConnection: vi.fn(),
  refreshSnapshot: vi.fn(),
  refreshOperations: vi.fn(),
  refreshKnowledgeSnapshot: vi.fn(),
  refreshKnowledgeItems: vi.fn(),
  refreshAll: vi.fn(),
  selectEntity: vi.fn(),
  selectKnowledgeItem: vi.fn(),
}

vi.mock('@/store/useOpsStore', () => ({
  useOpsStore: (selector: (state: Record<string, unknown>) => unknown) =>
    selector(mockedStore),
}))

vi.mock('@/hooks/useRealtime', () => ({
  useRealtime: vi.fn(),
}))

afterEach(() => {
  cleanup()
})

describe('App routes', () => {
  it.each([
    ['/', 'Everything that matters, without the noise.'],
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

  it('shows Knowledge in the app navigation', () => {
    render(<App />)

    expect(screen.getByRole('link', { name: /knowledge/i })).toBeInTheDocument()
  })

  it('renders the knowledge route', () => {
    render(
      <MemoryRouter initialEntries={['/knowledge']}>
        <AppShell connection="connected">
          <AppRoutes />
        </AppShell>
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: /knowledge hub/i })).toBeInTheDocument()
  })

  it('renders curated knowledge sections on the dashboard', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppShell connection="connected">
          <AppRoutes />
        </AppShell>
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: /main docs/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /personal context/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /recent workspace/i })).toBeInTheDocument()
  })

  it('shows a resilient realtime status when local data exists without a dashboard snapshot timestamp', () => {
    render(
      <MemoryRouter>
        <AppShell connection="connecting" hasLocalData>
          <div>content</div>
        </AppShell>
      </MemoryRouter>,
    )

    expect(screen.getByText('Local data available')).toBeInTheDocument()
    expect(screen.getByText('Using the latest local data while realtime connects.')).toBeInTheDocument()
    expect(screen.queryByText('Waiting for the first snapshot')).not.toBeInTheDocument()
  })

  it('shows reconnecting status without hiding the latest snapshot when realtime degrades', () => {
    render(
      <MemoryRouter>
        <AppShell connection="degraded" generatedAt="2026-06-21T10:00:00+00:00" hasLocalData>
          <div>content</div>
        </AppShell>
      </MemoryRouter>,
    )

    expect(screen.getByText('Realtime reconnecting')).toBeInTheDocument()
    expect(screen.getByText(/Latest snapshot/)).toBeInTheDocument()
  })

  it('shows a generic workspace label instead of the absolute local path on the dashboard hero', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppShell connection="connected" generatedAt="2026-06-21T10:00:00+00:00" hasLocalData>
          <AppRoutes />
        </AppShell>
      </MemoryRouter>,
    )

    expect(screen.getByText('Workspace locale connesso')).toBeInTheDocument()
    expect(screen.queryByText('/tmp/vitadex-state/workspace')).not.toBeInTheDocument()
  })
})
