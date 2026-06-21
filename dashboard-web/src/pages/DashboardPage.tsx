import { useEffect } from 'react'

import { EntityDetail } from '@/components/EntityDetail'
import { KnowledgeDetail } from '@/components/KnowledgeDetail'
import { KnowledgeList } from '@/components/KnowledgeList'
import { MetricCard } from '@/components/MetricCard'
import { SectionFrame } from '@/components/SectionFrame'
import { TimelineFeed } from '@/components/TimelineFeed'
import { UnifiedList } from '@/components/UnifiedList'
import { useRealtime } from '@/hooks/useRealtime'
import { useOpsStore } from '@/store/useOpsStore'

export default function DashboardPage() {
  const snapshot = useOpsStore((state) => state.snapshot)
  const knowledgeSnapshot = useOpsStore((state) => state.knowledgeSnapshot)
  const selectedEntity = useOpsStore((state) => state.selectedEntity)
  const selectedKnowledgeItem = useOpsStore((state) => state.selectedKnowledgeItem)
  const refreshAll = useOpsStore((state) => state.refreshAll)
  const selectEntity = useOpsStore((state) => state.selectEntity)
  const selectKnowledgeItem = useOpsStore((state) => state.selectKnowledgeItem)

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
            <h2 className="font-serif text-4xl text-black/85">Everything that matters, without the noise.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-black/48">
              A continuous read of tasks, approvals, follow-ups, logs, and system-generated panels, updated locally in real time.
            </p>
          </div>
          <p className="max-w-xs text-sm leading-6 text-black/45">{snapshot?.health.workspaceRoot ?? 'Waiting for the local workspace'}</p>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Active tasks" value={summary?.activeTasks ?? 0} note="Immediate operational focus." />
        <MetricCard label="Pending approvals" value={summary?.pendingApprovals ?? 0} note="Items waiting for a yes or no." />
        <MetricCard label="Follow-ups" value={summary?.dueFollowups ?? 0} note="Deadlines that should not drift away." />
        <MetricCard label="Decisions" value={summary?.decisionRequests ?? 0} note="Open tasks that still need completion." />
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
        <SectionFrame
          eyebrow="Priority"
          title="Hot flow"
          subtitle="The most relevant entities right now, ordered by latest update."
        >
          <UnifiedList
            items={snapshot?.priorities ?? []}
            selectedId={selectedEntity?.id}
            emptyLabel="No priorities available."
            onSelect={(item) => void selectEntity(item.kind, item.id)}
          />
        </SectionFrame>

        <SectionFrame
          eyebrow="Realtime"
          title="Event timeline"
          subtitle="Audited events inserted into the stream in reverse chronological order."
        >
          <TimelineFeed items={snapshot?.timeline ?? []} />
        </SectionFrame>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <SectionFrame
          eyebrow="Knowledge"
          title="Main Docs"
          subtitle="Core public documents always within reach."
        >
          <KnowledgeList
            items={knowledgeSnapshot?.mainDocs ?? []}
            selectedId={selectedKnowledgeItem?.id}
            emptyLabel="No public docs available."
            onSelect={(item) => void selectKnowledgeItem(item.id)}
          />
        </SectionFrame>

        <SectionFrame
          eyebrow="Personal"
          title="Personal Context"
          subtitle="High-signal memory files surfaced read-only."
        >
          <KnowledgeList
            items={knowledgeSnapshot?.personalContext ?? []}
            selectedId={selectedKnowledgeItem?.id}
            emptyLabel="No personal context available."
            onSelect={(item) => void selectKnowledgeItem(item.id)}
          />
        </SectionFrame>

        <SectionFrame
          eyebrow="Workspace"
          title="Recent Workspace"
          subtitle="Latest local notes and outputs from approved folders."
        >
          <KnowledgeList
            items={knowledgeSnapshot?.recentWorkspaceFiles ?? []}
            selectedId={selectedKnowledgeItem?.id}
            emptyLabel="No recent workspace files available."
            onSelect={(item) => void selectKnowledgeItem(item.id)}
          />
        </SectionFrame>
      </div>

      <KnowledgeDetail item={selectedKnowledgeItem} />
      <EntityDetail entity={selectedEntity} />
    </div>
  )
}
