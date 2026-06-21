import { useEffect } from 'react'

import { EntityDetail } from '@/components/EntityDetail'
import { MetricCard } from '@/components/MetricCard'
import { SectionFrame } from '@/components/SectionFrame'
import { TimelineFeed } from '@/components/TimelineFeed'
import { UnifiedList } from '@/components/UnifiedList'
import { useRealtime } from '@/hooks/useRealtime'
import { useOpsStore } from '@/store/useOpsStore'

export default function DashboardPage() {
  const snapshot = useOpsStore((state) => state.snapshot)
  const selectedEntity = useOpsStore((state) => state.selectedEntity)
  const refreshAll = useOpsStore((state) => state.refreshAll)
  const selectEntity = useOpsStore((state) => state.selectEntity)

  useRealtime()

  useEffect(() => {
    void refreshAll()
  }, [refreshAll])

  const summary = snapshot?.summary

  return (
    <div className="space-y-6">
      <section className="rounded-[36px] border border-black/8 bg-[linear-gradient(135deg,rgba(255,251,245,0.95),rgba(246,241,234,0.92))] px-6 py-7 shadow-[0_35px_90px_rgba(30,29,27,0.08)]">
        <p className="text-[11px] uppercase tracking-[0.26em] text-black/35">Dashboard</p>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="font-serif text-4xl text-black/85">Tutto cio' che accade, senza rumore.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-black/48">
              Una lettura continua di task, approval, follow-up, log e pannelli generati dal sistema, con aggiornamento locale in tempo reale.
            </p>
          </div>
          <p className="max-w-xs text-sm leading-6 text-black/45">{snapshot?.health.workspaceRoot ?? 'In attesa del workspace locale'}</p>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Task attive" value={summary?.activeTasks ?? 0} note="Focus operativo immediato." />
        <MetricCard label="Approval pendenti" value={summary?.pendingApprovals ?? 0} note="Nodi che aspettano un si o un no." />
        <MetricCard label="Follow-up" value={summary?.dueFollowups ?? 0} note="Scadenze da non lasciare evaporare." />
        <MetricCard label="Decisioni" value={summary?.decisionRequests ?? 0} note="Task aperte ma incomplete." />
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
        <SectionFrame
          eyebrow="Priorita'"
          title="Flusso caldo"
          subtitle="Le entita' piu' rilevanti del momento, ordinate per ultimo aggiornamento."
        >
          <UnifiedList
            items={snapshot?.priorities ?? []}
            selectedId={selectedEntity?.id}
            emptyLabel="Nessuna priorita' disponibile."
            onSelect={(item) => void selectEntity(item.kind, item.id)}
          />
        </SectionFrame>

        <SectionFrame
          eyebrow="Realtime"
          title="Timeline eventi"
          subtitle="Eventi auditati, inseriti nel flusso in ordine cronologico inverso."
        >
          <TimelineFeed items={snapshot?.timeline ?? []} />
        </SectionFrame>
      </div>

      <EntityDetail entity={selectedEntity} />
    </div>
  )
}
