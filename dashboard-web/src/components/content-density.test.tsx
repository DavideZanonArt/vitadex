import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { EntityDetail } from '@/components/EntityDetail'
import { KnowledgeCard } from '@/components/KnowledgeCard'
import { UnifiedList } from '@/components/UnifiedList'
import type { EntityDetail as EntityDetailType, KnowledgeItem, UnifiedItem } from '@/types'

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('content density', () => {
  it('truncates noisy operation previews in the unified list', () => {
    const items: UnifiedItem[] = [
      {
        id: 'task-1',
        kind: 'task',
        title: 'Long operation preview',
        status: 'active',
        updatedAt: '2026-06-21T10:00:00+00:00',
        tags: ['home'],
        preview: `Lead summary ${'x'.repeat(220)} HIDDEN_MARKER`,
      },
    ]

    render(<UnifiedList items={items} emptyLabel="Empty" onSelect={vi.fn()} />)

    expect(screen.getByText(/Lead summary/i)).toBeInTheDocument()
    expect(screen.queryByText(/HIDDEN_MARKER/)).not.toBeInTheDocument()
  })

  it('shows a compact file label instead of the full knowledge path in the card body', () => {
    const item: KnowledgeItem = {
      id: 'doc-1',
      title: 'Knowledge item',
      scope: 'public',
      source: 'docs',
      kind: 'markdown',
      path: 'docs/superpowers/specs/2026-06-21-unified-dashboard-knowledge-hub-design.md',
      updatedAt: '2026-06-21T10:00:00+00:00',
      tags: ['public', 'docs'],
      preview: 'A compact preview.',
    }

    render(<KnowledgeCard item={item} onSelect={vi.fn()} />)

    expect(screen.getByText('2026-06-21-unified-dashboard-knowledge-hub-design.md')).toBeInTheDocument()
    expect(screen.queryByText(item.path)).not.toBeInTheDocument()
  })

  it('surfaces key entity fields before the raw payload dump', () => {
    const entity: EntityDetailType = {
      id: 'task-1',
      kind: 'task',
      title: 'Housing task',
      status: 'active',
      relatedTaskId: 'task-1',
      rendered: '# Housing task',
      data: {
        owner: 'Davide',
        budget: 1400,
        city: 'Munich',
        nested: { pets: 2 },
      },
    }

    render(<EntityDetail entity={entity} />)

    expect(screen.getByText('Key fields')).toBeInTheDocument()
    expect(screen.getByText('owner')).toBeInTheDocument()
    expect(screen.getByText('Davide')).toBeInTheDocument()
    expect(screen.getByText('Raw payload')).toBeInTheDocument()
  })
})
