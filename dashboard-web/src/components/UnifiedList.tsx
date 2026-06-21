import { ArrowUpRight } from 'lucide-react'

import { StatusBadge } from '@/components/StatusBadge'
import { cn } from '@/lib/utils'
import type { UnifiedItem } from '@/types'

type UnifiedListProps = {
  items: UnifiedItem[]
  selectedId?: string
  emptyLabel: string
  onSelect: (item: UnifiedItem) => void
}

function toneFromStatus(status: string) {
  if (status.includes('critical') || status.includes('urgent') || status.includes('rejected')) {
    return 'critical' as const
  }
  if (status.includes('pending') || status.includes('waiting') || status.includes('blocked') || status.includes('high')) {
    return 'warning' as const
  }
  if (status.includes('done') || status.includes('approved') || status.includes('active')) {
    return 'success' as const
  }
  return 'neutral' as const
}

export function UnifiedList({ items, selectedId, emptyLabel, onSelect }: UnifiedListProps) {
  if (!items.length) {
    return <div className="rounded-[24px] border border-dashed border-black/10 bg-black/[0.02] p-6 text-sm text-black/45">{emptyLabel}</div>
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          onClick={() => onSelect(item)}
          className={cn(
            'w-full rounded-[24px] border px-4 py-4 text-left transition',
            selectedId === item.id ? 'border-black/15 bg-black/[0.04]' : 'border-black/8 bg-[var(--paper-strong)] hover:border-black/15 hover:bg-white',
          )}
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[11px] uppercase tracking-[0.22em] text-black/35">{item.kind}</p>
              <h3 className="mt-2 text-sm font-medium text-black/78">{item.title}</h3>
            </div>
            <ArrowUpRight className="mt-1 h-4 w-4 text-black/25" />
          </div>
          <p className="mt-3 line-clamp-2 text-sm leading-6 text-black/48">{item.preview}</p>
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <StatusBadge label={item.status.split('_').join(' ')} tone={toneFromStatus(item.status)} />
            {item.tags.slice(0, 2).map((tag) => (
              <span key={tag} className="rounded-full bg-black/[0.04] px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-black/42">
                {tag}
              </span>
            ))}
          </div>
        </button>
      ))}
    </div>
  )
}
