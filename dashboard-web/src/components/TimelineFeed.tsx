import { Clock3 } from 'lucide-react'

import { StatusBadge } from '@/components/StatusBadge'
import type { TimelineEvent } from '@/types'

type TimelineFeedProps = {
  items: TimelineEvent[]
}

function toneFromSeverity(severity: TimelineEvent['severity']) {
  if (severity === 'critical') {
    return 'critical' as const
  }
  if (severity === 'warning') {
    return 'warning' as const
  }
  return 'neutral' as const
}

export function TimelineFeed({ items }: TimelineFeedProps) {
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <article key={item.id} className="rounded-[24px] border border-black/8 bg-[var(--paper-strong)] px-4 py-4">
          <div className="flex items-center gap-3 text-[11px] uppercase tracking-[0.18em] text-black/35">
            <Clock3 className="h-3.5 w-3.5" />
            <span>{new Date(item.at).toLocaleString('it-IT')}</span>
          </div>
          <p className="mt-3 text-sm leading-6 text-black/75">{item.label}</p>
          <div className="mt-3 flex items-center gap-2">
            <StatusBadge label={item.kind} tone="neutral" />
            <StatusBadge label={item.severity} tone={toneFromSeverity(item.severity)} />
          </div>
        </article>
      ))}
    </div>
  )
}
