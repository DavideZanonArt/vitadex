import { useEffect } from 'react'

import { KnowledgeDetail } from '@/components/KnowledgeDetail'
import { KnowledgeList } from '@/components/KnowledgeList'
import { MetricCard } from '@/components/MetricCard'
import { SectionFrame } from '@/components/SectionFrame'
import { useOpsStore } from '@/store/useOpsStore'

const scopes = ['all', 'public', 'personal'] as const
const sources = ['all', 'docs', 'memory', 'workspace'] as const

export default function KnowledgePage() {
  const knowledgeSnapshot = useOpsStore((state) => state.knowledgeSnapshot)
  const knowledgeItems = useOpsStore((state) => state.knowledgeItems)
  const selectedKnowledgeItem = useOpsStore((state) => state.selectedKnowledgeItem)
  const knowledgeFilters = useOpsStore((state) => state.knowledgeFilters)
  const setKnowledgeFilters = useOpsStore((state) => state.setKnowledgeFilters)
  const refreshKnowledgeSnapshot = useOpsStore((state) => state.refreshKnowledgeSnapshot)
  const refreshKnowledgeItems = useOpsStore((state) => state.refreshKnowledgeItems)
  const selectKnowledgeItem = useOpsStore((state) => state.selectKnowledgeItem)

  useEffect(() => {
    void refreshKnowledgeSnapshot()
  }, [refreshKnowledgeSnapshot])

  useEffect(() => {
    void refreshKnowledgeItems()
  }, [knowledgeFilters.scope, knowledgeFilters.search, knowledgeFilters.source, refreshKnowledgeItems])

  const visibleSelectedKnowledgeItem =
    selectedKnowledgeItem && knowledgeItems.some((item) => item.id === selectedKnowledgeItem.id) ? selectedKnowledgeItem : null

  useEffect(() => {
    if (!visibleSelectedKnowledgeItem && knowledgeItems.length > 0) {
      void selectKnowledgeItem(knowledgeItems[0].id)
    }
  }, [knowledgeItems, selectKnowledgeItem, visibleSelectedKnowledgeItem])

  const counts = knowledgeSnapshot?.health.counts

  return (
    <div className="space-y-6">
      <section className="rounded-[36px] border border-black/8 bg-[linear-gradient(135deg,rgba(255,251,245,0.95),rgba(246,241,234,0.92))] px-6 py-7 shadow-[0_35px_90px_rgba(30,29,27,0.08)]">
        <p className="text-[11px] uppercase tracking-[0.26em] text-black/35">Knowledge</p>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="font-serif text-4xl text-black/85">Knowledge Hub</h2>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-black/48">
              Curated public docs, personal memory, and recent workspace files in one read-only surface.
            </p>
          </div>
          <p className="max-w-xs text-sm leading-6 text-black/45">
            {knowledgeSnapshot?.health.personalAvailable
              ? 'Public and personal roots are available.'
              : 'Personal roots are unavailable, showing the public slice only.'}
          </p>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Indexed items" value={counts?.total ?? 0} note="Files currently exposed through approved roots." />
        <MetricCard label="Public docs" value={counts?.public ?? 0} note="Repository docs and workflows ready to inspect." />
        <MetricCard label="Memory files" value={counts?.memory ?? 0} note="Personal context available in degraded-safe mode." />
        <MetricCard label="Workspace files" value={counts?.workspace ?? 0} note="Recent local notes, outputs, and panels." />
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
        <SectionFrame
          eyebrow="Knowledge Browser"
          title="Browse approved sources"
          subtitle="Filter by scope, source, or text to move from curated context to the broader knowledge list."
        >
          <div className="mb-5 grid gap-3 md:grid-cols-[1.1fr_0.45fr_0.45fr]">
            <input
              value={knowledgeFilters.search}
              onChange={(event) => setKnowledgeFilters({ search: event.target.value })}
              placeholder="Search title, preview, path, or tag"
              className="rounded-2xl border border-black/10 bg-[var(--paper-strong)] px-4 py-3 text-sm outline-none transition focus:border-black/20"
            />
            <select
              value={knowledgeFilters.scope}
              onChange={(event) => setKnowledgeFilters({ scope: event.target.value as typeof knowledgeFilters.scope })}
              className="rounded-2xl border border-black/10 bg-[var(--paper-strong)] px-4 py-3 text-sm outline-none"
            >
              {scopes.map((scope) => (
                <option key={scope} value={scope}>
                  {scope === 'all' ? 'All scopes' : scope}
                </option>
              ))}
            </select>
            <select
              value={knowledgeFilters.source}
              onChange={(event) => setKnowledgeFilters({ source: event.target.value as typeof knowledgeFilters.source })}
              className="rounded-2xl border border-black/10 bg-[var(--paper-strong)] px-4 py-3 text-sm outline-none"
            >
              {sources.map((source) => (
                <option key={source} value={source}>
                  {source === 'all' ? 'All sources' : source}
                </option>
              ))}
            </select>
          </div>

          <KnowledgeList
            items={knowledgeItems}
            selectedId={visibleSelectedKnowledgeItem?.id}
            emptyLabel="No knowledge item matches the current filters."
            onSelect={(item) => void selectKnowledgeItem(item.id)}
          />
        </SectionFrame>

        <KnowledgeDetail item={visibleSelectedKnowledgeItem} />
      </div>
    </div>
  )
}
