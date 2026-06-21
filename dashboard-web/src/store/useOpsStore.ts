import { create } from 'zustand'

import type {
  DashboardSnapshot,
  EntityDetail,
  EntityKind,
  KnowledgeContent,
  KnowledgeScope,
  KnowledgeSnapshot,
  KnowledgeSource,
  PaginatedItems,
  UnifiedItem,
} from '@/types'
import { fetchJson } from '@/utils/api'

type Filters = {
  kind: 'all' | EntityKind
  status: string
  search: string
}

type KnowledgeFilters = {
  scope: 'all' | KnowledgeScope
  source: 'all' | KnowledgeSource
  search: string
}

type OpsState = {
  snapshot: DashboardSnapshot | null
  knowledgeSnapshot: KnowledgeSnapshot | null
  operations: UnifiedItem[]
  selectedEntity: EntityDetail | null
  knowledgeItems: KnowledgeSnapshot['mainDocs']
  selectedKnowledgeItem: KnowledgeContent | null
  filters: Filters
  knowledgeFilters: KnowledgeFilters
  isLoading: boolean
  error: string | null
  connection: 'connecting' | 'connected' | 'degraded'
  setFilters: (filters: Partial<Filters>) => void
  setKnowledgeFilters: (filters: Partial<KnowledgeFilters>) => void
  setConnection: (status: OpsState['connection']) => void
  refreshSnapshot: () => Promise<void>
  refreshKnowledgeSnapshot: () => Promise<void>
  refreshOperations: () => Promise<void>
  refreshKnowledgeItems: () => Promise<void>
  refreshAll: () => Promise<void>
  selectEntity: (kind: EntityKind, entityId: string) => Promise<void>
  selectKnowledgeItem: (itemId: string) => Promise<void>
}

const defaultFilters: Filters = {
  kind: 'all',
  status: '',
  search: '',
}

const defaultKnowledgeFilters: KnowledgeFilters = {
  scope: 'all',
  source: 'all',
  search: '',
}

export const useOpsStore = create<OpsState>((set, get) => ({
  snapshot: null,
  knowledgeSnapshot: null,
  operations: [],
  selectedEntity: null,
  knowledgeItems: [],
  selectedKnowledgeItem: null,
  filters: defaultFilters,
  knowledgeFilters: defaultKnowledgeFilters,
  isLoading: false,
  error: null,
  connection: 'connecting',
  setFilters: (filters) => set((state) => ({ filters: { ...state.filters, ...filters } })),
  setKnowledgeFilters: (filters) =>
    set((state) => ({ knowledgeFilters: { ...state.knowledgeFilters, ...filters } })),
  setConnection: (connection) => set({ connection }),
  refreshSnapshot: async () => {
    const snapshot = await fetchJson<DashboardSnapshot>('/api/dashboard/snapshot')
    set({ snapshot, error: null })
  },
  refreshKnowledgeSnapshot: async () => {
    const knowledgeSnapshot = await fetchJson<KnowledgeSnapshot>('/api/knowledge/snapshot')
    set({ knowledgeSnapshot, error: null })
  },
  refreshOperations: async () => {
    const { filters } = get()
    const params = new URLSearchParams()
    if (filters.kind !== 'all') {
      params.set('kind', filters.kind)
    }
    if (filters.status) {
      params.set('status', filters.status)
    }
    if (filters.search) {
      params.set('search', filters.search)
    }
    const response = await fetchJson<PaginatedItems>(`/api/operations?${params.toString()}`)
    set({ operations: response.items, error: null })
  },
  refreshKnowledgeItems: async () => {
    const { knowledgeFilters } = get()
    const params = new URLSearchParams()
    if (knowledgeFilters.scope !== 'all') {
      params.set('scope', knowledgeFilters.scope)
    }
    if (knowledgeFilters.source !== 'all') {
      params.set('source', knowledgeFilters.source)
    }
    if (knowledgeFilters.search) {
      params.set('search', knowledgeFilters.search)
    }
    const query = params.toString()
    const response = await fetchJson<{
      items: KnowledgeSnapshot['mainDocs']
      count: number
    }>(query ? `/api/knowledge/items?${query}` : '/api/knowledge/items')
    set({ knowledgeItems: response.items, error: null })
  },
  refreshAll: async () => {
    set({ isLoading: true, error: null })
    try {
      await Promise.all([get().refreshSnapshot(), get().refreshOperations(), get().refreshKnowledgeSnapshot()])
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' })
    } finally {
      set({ isLoading: false })
    }
  },
  selectEntity: async (kind, entityId) => {
    try {
      const selectedEntity = await fetchJson<EntityDetail>(`/api/entities/${kind}/${entityId}`)
      set({ selectedEntity, error: null })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Entity detail error' })
    }
  },
  selectKnowledgeItem: async (itemId) => {
    try {
      const selectedKnowledgeItem = await fetchJson<KnowledgeContent>(
        `/api/knowledge/content?item_id=${encodeURIComponent(itemId)}`,
      )
      set({ selectedKnowledgeItem, error: null })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Knowledge detail error' })
    }
  },
}))
