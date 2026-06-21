import { KnowledgeCard } from '@/components/KnowledgeCard'
import type { KnowledgeItem } from '@/types'

type KnowledgeListProps = {
  items: KnowledgeItem[]
  selectedId?: string
  emptyLabel: string
  onSelect: (item: KnowledgeItem) => void
}

export function KnowledgeList({ items, selectedId, emptyLabel, onSelect }: KnowledgeListProps) {
  if (!items.length) {
    return <div className="rounded-[24px] border border-dashed border-black/10 bg-black/[0.02] p-6 text-sm text-black/45">{emptyLabel}</div>
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <KnowledgeCard key={item.id} item={item} isSelected={selectedId === item.id} onSelect={onSelect} />
      ))}
    </div>
  )
}
