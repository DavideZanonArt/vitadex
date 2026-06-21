import { create } from 'zustand'

import type { DashboardSnapshot, EntityDetail, EntityKind, PaginatedItems, UnifiedItem } from '@/types'
import { fetchJson } from '@/utils/api'

type Filters = {
  kind: 'all' | EntityKind
  status: string
  search: string
}

type OpsState = {
  snapshot: DashboardSnapshot | null
  operations: UnifiedItem[]
  logs: UnifiedItem[]
  panels: UnifiedItem[]
  selectedEntity: EntityDetail | null
  filters: Filters
  isLoading: boolean
  error: string | null
  connection: 'connecting' | 'connected' | 'degraded'
  setFilters: (filters: Partial<Filters>) => void
  setConnection: (status: OpsState['connection']) => void
  refreshSnapshot: () => Promise<void>
  refreshOperations: () => Promise<void>
  refreshLogs: () => Promise<void>
  refreshPanels: () => Promise<void>
  refreshAll: () => Promise<void>
  selectEntity: (kind: EntityKind, entityId: string) => Promise<void>
}

const defaultFilters: Filters = {
  kind: 'all',
  status: '',
  search: '',
}

export const useOpsStore = create<OpsState>((set, get) => ({
  snapshot: null,
  operations: [],
  logs: [],
  panels: [],
  selectedEntity: null,
  filters: defaultFilters,
  isLoading: false,
  error: null,
  connection: 'connecting',
  setFilters: (filters) => set((state) => ({ filters: { ...state.filters, ...filters } })),
  setConnection: (connection) => set({ connection }),
  refreshSnapshot: async () => {
    const snapshot = await fetchJson<DashboardSnapshot>('/api/dashboard/snapshot')
    set({ snapshot, error: null })
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
    const response = await fetchJson<PaginatedItems>(`/api/operazioni?${params.toString()}`)
    set({ operations: response.items, error: null })
  },
  refreshLogs: async () => {
    const response = await fetchJson<PaginatedItems>('/api/archivio/logs')
    set({ logs: response.items, error: null })
  },
  refreshPanels: async () => {
    const response = await fetchJson<PaginatedItems>('/api/panels')
    set({ panels: response.items, error: null })
  },
  refreshAll: async () => {
    set({ isLoading: true, error: null })
    try {
      await Promise.all([
        get().refreshSnapshot(),
        get().refreshOperations(),
        get().refreshLogs(),
        get().refreshPanels(),
      ])
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Errore sconosciuto' })
    } finally {
      set({ isLoading: false })
    }
  },
  selectEntity: async (kind, entityId) => {
    try {
      const selectedEntity = await fetchJson<EntityDetail>(`/api/entita/${kind}/${entityId}`)
      set({ selectedEntity, error: null })
    } catch (error) {
        set({ error: error instanceof Error ? error.message : "Errore dettaglio entita'" })
      }
    },
}))
