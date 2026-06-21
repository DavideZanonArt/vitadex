import { cn } from '@/lib/utils'
import type { KnowledgeScope, KnowledgeSource } from '@/types'

type ScopeBadgeProps = {
  scope: KnowledgeScope
  source?: KnowledgeSource
}

export function ScopeBadge({ scope, source }: ScopeBadgeProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span
        className={cn(
          'rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.18em]',
          scope === 'public' ? 'bg-sky-100 text-sky-900' : 'bg-amber-100 text-amber-900',
        )}
      >
        {scope}
      </span>
      {source ? (
        <span className="rounded-full bg-black/[0.04] px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-black/42">
          {source}
        </span>
      ) : null}
    </div>
  )
}
