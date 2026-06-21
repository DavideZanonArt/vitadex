import { useEffect } from 'react'

import { EntityDetail } from '@/components/EntityDetail'
import { SectionFrame } from '@/components/SectionFrame'
import { UnifiedList } from '@/components/UnifiedList'
import { useOpsStore } from '@/store/useOpsStore'

const kinds = ['all', 'task', 'approval', 'followup', 'panel', 'log'] as const
const statuses = ['', 'active', 'pending', 'waiting', 'blocked', 'done', 'approved', 'rejected']

export default function OperationsPage() {
  const operations = useOpsStore((state) => state.operations)
  const filters = useOpsStore((state) => state.filters)
  const selectedEntity = useOpsStore((state) => state.selectedEntity)
  const setFilters = useOpsStore((state) => state.setFilters)
  const refreshOperations = useOpsStore((state) => state.refreshOperations)
  const selectEntity = useOpsStore((state) => state.selectEntity)

  useEffect(() => {
    void refreshOperations()
  }, [filters.kind, filters.search, filters.status, refreshOperations])

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
      <SectionFrame
        eyebrow="Operations"
        title="Unified list"
        subtitle="Filter by type, status, or text to read the system as one coherent flow."
      >
        <div className="mb-5 grid gap-3 md:grid-cols-[1.1fr_0.5fr_0.5fr]">
          <input
            value={filters.search}
            onChange={(event) => setFilters({ search: event.target.value })}
            placeholder="Search title, preview, or tag"
            className="rounded-2xl border border-black/10 bg-[var(--paper-strong)] px-4 py-3 text-sm outline-none transition focus:border-black/20"
          />
          <select
            value={filters.kind}
            onChange={(event) => setFilters({ kind: event.target.value as typeof filters.kind })}
            className="rounded-2xl border border-black/10 bg-[var(--paper-strong)] px-4 py-3 text-sm outline-none"
          >
            {kinds.map((kind) => (
              <option key={kind} value={kind}>
                {kind === 'all' ? 'All types' : kind}
              </option>
            ))}
          </select>
          <select
            value={filters.status}
            onChange={(event) => setFilters({ status: event.target.value })}
            className="rounded-2xl border border-black/10 bg-[var(--paper-strong)] px-4 py-3 text-sm outline-none"
          >
            {statuses.map((status) => (
              <option key={status || 'all-status'} value={status}>
                {status || 'All statuses'}
              </option>
            ))}
          </select>
        </div>

        <UnifiedList
          items={operations}
          selectedId={selectedEntity?.id}
          emptyLabel="No entity matches the current filters."
          onSelect={(item) => void selectEntity(item.kind, item.id)}
        />
      </SectionFrame>

      <EntityDetail entity={selectedEntity} />
    </div>
  )
}
