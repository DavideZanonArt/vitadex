import { ArrowUpRight } from 'lucide-react'

import { ScopeBadge } from '@/components/ScopeBadge'
import { cn, compactPath, compactText } from '@/lib/utils'
import type { KnowledgeItem } from '@/types'

type KnowledgeCardProps = {
  item: KnowledgeItem
  isSelected?: boolean
  onSelect: (item: KnowledgeItem) => void
}

export function KnowledgeCard({ item, isSelected = false, onSelect }: KnowledgeCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(item)}
      className={cn(
        'w-full rounded-[24px] border px-4 py-4 text-left transition',
        isSelected ? 'border-black/15 bg-black/[0.04]' : 'border-black/8 bg-[var(--paper-strong)] hover:border-black/15 hover:bg-white',
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <ScopeBadge scope={item.scope} source={item.source} />
            <span className="text-[11px] uppercase tracking-[0.2em] text-black/35">{item.kind}</span>
          </div>
          <div>
            <h3 className="text-sm font-medium text-black/78">{item.title}</h3>
            <p className="mt-1 text-xs uppercase tracking-[0.14em] text-black/35">{compactPath(item.path)}</p>
          </div>
        </div>
        <ArrowUpRight className="mt-1 h-4 w-4 text-black/25" />
      </div>
      <p className="mt-3 line-clamp-3 text-sm leading-6 text-black/48">{compactText(item.preview, 170)}</p>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {item.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="rounded-full bg-black/[0.04] px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-black/42">
              {tag}
            </span>
          ))}
        </div>
        <span className="text-xs text-black/45">{new Date(item.updatedAt).toLocaleString('en-US')}</span>
      </div>
    </button>
  )
}
