import { ScrollText } from 'lucide-react'

import { SectionFrame } from '@/components/SectionFrame'
import { StatusBadge } from '@/components/StatusBadge'
import { extractScalarEntries } from '@/lib/utils'
import type { EntityDetail as EntityDetailType } from '@/types'

type EntityDetailProps = {
  entity: EntityDetailType | null
}

export function EntityDetail({ entity }: EntityDetailProps) {
  if (!entity) {
    return (
      <SectionFrame
        eyebrow="Detail"
        title="No entity selected"
        subtitle="Select an item from the list to open context, payload, and relationships."
      >
        <div className="rounded-[24px] border border-dashed border-black/10 bg-black/[0.02] p-8 text-sm text-black/45">
          The dashboard remains read-only: only the context of the selected item appears here.
        </div>
      </SectionFrame>
    )
  }

  const scalarEntries = extractScalarEntries(entity.data)

  return (
    <SectionFrame eyebrow="Detail" title={entity.title} subtitle="Full read-only context, ready for audit and review.">
      <div className="flex flex-wrap gap-2">
        <StatusBadge label={entity.kind} />
        <StatusBadge label={entity.status.split('_').join(' ')} />
        {entity.relatedTaskId ? <StatusBadge label={`task ${entity.relatedTaskId}`} /> : null}
      </div>
      {entity.rendered ? (
        <div className="mt-5 rounded-[24px] border border-black/8 bg-[var(--paper-strong)] p-5">
          <div className="mb-4 flex items-center gap-2 text-[11px] uppercase tracking-[0.2em] text-black/35">
            <ScrollText className="h-3.5 w-3.5" />
            <span>Render Markdown</span>
          </div>
          <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-6 text-black/70">{entity.rendered}</pre>
        </div>
      ) : null}
      {scalarEntries.length ? (
        <div className="mt-5 rounded-[24px] border border-black/8 bg-[var(--paper-strong)] p-5">
          <p className="text-[11px] uppercase tracking-[0.22em] text-black/35">Key fields</p>
          <dl className="mt-4 grid gap-3 sm:grid-cols-2">
            {scalarEntries.map(([key, value]) => (
              <div key={key} className="rounded-[18px] border border-black/6 bg-white/80 px-4 py-3">
                <dt className="text-[11px] uppercase tracking-[0.18em] text-black/35">{key}</dt>
                <dd className="mt-2 text-sm text-black/72">{String(value)}</dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}
      <details className="mt-5 rounded-[24px] border border-black/8 bg-black/[0.02] p-5">
        <summary className="cursor-pointer list-none text-[11px] uppercase tracking-[0.22em] text-black/35">Raw payload</summary>
        <pre className="mt-3 overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-6 text-black/70">
          {JSON.stringify(entity.data, null, 2)}
        </pre>
      </details>
    </SectionFrame>
  )
}
