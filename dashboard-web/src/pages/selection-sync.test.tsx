import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import KnowledgePage from '@/pages/KnowledgePage'
import OperationsPage from '@/pages/OperationsPage'
import type { EntityDetail, KnowledgeContent, KnowledgeItem, UnifiedItem } from '@/types'

const { currentState, refreshOperationsMock, refreshKnowledgeSnapshotMock, refreshKnowledgeItemsMock, selectEntityMock, selectKnowledgeItemMock } =
  vi.hoisted(() => ({
    currentState: {} as Record<string, unknown>,
    refreshOperationsMock: vi.fn().mockResolvedValue(undefined),
    refreshKnowledgeSnapshotMock: vi.fn().mockResolvedValue(undefined),
    refreshKnowledgeItemsMock: vi.fn().mockResolvedValue(undefined),
    selectEntityMock: vi.fn().mockResolvedValue(undefined),
    selectKnowledgeItemMock: vi.fn().mockResolvedValue(undefined),
  }))

vi.mock('@/store/useOpsStore', () => ({
  useOpsStore: (selector: (state: Record<string, unknown>) => unknown) => selector(currentState),
}))

function makeOperation(id: string, title: string): UnifiedItem {
  return {
    id,
    kind: 'task',
    title,
    status: 'active',
    updatedAt: '2026-06-21T10:00:00+00:00',
    tags: ['home'],
    preview: `${title} preview`,
  }
}

function makeEntity(id: string, title: string): EntityDetail {
  return {
    id,
    kind: 'task',
    title,
    status: 'active',
    data: { id, title },
    rendered: `# ${title}`,
  }
}

function makeKnowledgeItem(id: string, title: string): KnowledgeItem {
  return {
    id,
    title,
    scope: 'personal',
    source: 'memory',
    kind: 'note',
    path: `${title}.md`,
    updatedAt: '2026-06-21T10:00:00+00:00',
    tags: ['memory'],
    preview: `${title} preview`,
  }
}

function makeKnowledgeContent(id: string, title: string): KnowledgeContent {
  return {
    ...makeKnowledgeItem(id, title),
    content: `${title} content`,
  }
}

function baseState() {
  return {
    snapshot: null,
    knowledgeSnapshot: {
      mainDocs: [],
      personalContext: [],
      recentWorkspaceFiles: [],
      health: {
        publicAvailable: true,
        personalAvailable: true,
        counts: {
          public: 0,
          personal: 0,
          memory: 0,
          workspace: 0,
          total: 0,
        },
      },
    },
    operations: [],
    selectedEntity: null,
    knowledgeItems: [],
    selectedKnowledgeItem: null,
    filters: { kind: 'all', status: '', search: '' },
    knowledgeFilters: { scope: 'all', source: 'all', search: '' },
    setFilters: vi.fn(),
    setKnowledgeFilters: vi.fn(),
    setConnection: vi.fn(),
    refreshSnapshot: vi.fn().mockResolvedValue(undefined),
    refreshOperations: refreshOperationsMock,
    refreshKnowledgeSnapshot: refreshKnowledgeSnapshotMock,
    refreshKnowledgeItems: refreshKnowledgeItemsMock,
    refreshAll: vi.fn().mockResolvedValue(undefined),
    selectEntity: selectEntityMock,
    selectKnowledgeItem: selectKnowledgeItemMock,
  }
}

describe('selection sync', () => {
  afterEach(() => {
    cleanup()
  })

  beforeEach(() => {
    refreshOperationsMock.mockClear()
    refreshKnowledgeSnapshotMock.mockClear()
    refreshKnowledgeItemsMock.mockClear()
    selectEntityMock.mockClear()
    selectKnowledgeItemMock.mockClear()
    Object.assign(currentState, baseState())
  })

  it('reselects the first visible entity when the current operations selection is filtered out', async () => {
    Object.assign(currentState, {
      operations: [makeOperation('task-visible', 'Visible task')],
      selectedEntity: makeEntity('task-stale', 'Stale task'),
    })

    render(<OperationsPage />)

    await waitFor(() => {
      expect(selectEntityMock).toHaveBeenCalledWith('task', 'task-visible')
    })
  })

  it('shows the empty detail state when operations filters return no results', () => {
    Object.assign(currentState, {
      operations: [],
      selectedEntity: makeEntity('task-stale', 'Stale task'),
      filters: { kind: 'task', status: 'active', search: 'no-match' },
    })

    render(<OperationsPage />)

    expect(screen.getByText('No entity matches the current filters.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'No entity selected' })).toBeInTheDocument()
  })

  it('reselects the first visible knowledge item when the current selection is filtered out', async () => {
    Object.assign(currentState, {
      knowledgeItems: [makeKnowledgeItem('item-visible', 'Visible item')],
      selectedKnowledgeItem: makeKnowledgeContent('item-stale', 'Stale item'),
    })

    render(<KnowledgePage />)

    await waitFor(() => {
      expect(selectKnowledgeItemMock).toHaveBeenCalledWith('item-visible')
    })
  })

  it('shows the empty knowledge detail state when filters return no documents', () => {
    Object.assign(currentState, {
      knowledgeItems: [],
      selectedKnowledgeItem: makeKnowledgeContent('item-stale', 'Stale item'),
      knowledgeFilters: { scope: 'all', source: 'all', search: 'no-match' },
    })

    render(<KnowledgePage />)

    expect(screen.getByText('No knowledge item matches the current filters.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'No document selected' })).toBeInTheDocument()
  })
})
