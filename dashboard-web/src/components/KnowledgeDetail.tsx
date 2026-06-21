import { BookOpenText, ScrollText } from 'lucide-react'

import { ScopeBadge } from '@/components/ScopeBadge'
import { SectionFrame } from '@/components/SectionFrame'
import type { KnowledgeContent } from '@/types'

type KnowledgeDetailProps = {
  item: KnowledgeContent | null
}

export function KnowledgeDetail({ item }: KnowledgeDetailProps) {
  if (!item) {
    return (
      <SectionFrame
        eyebrow="Knowledge Detail"
        title="No document selected"
        subtitle="Pick a document to inspect source, path, and preview content."
      >
        <div className="rounded-[24px] border border-dashed border-black/10 bg-black/[0.02] p-8 text-sm text-black/45">
          The knowledge hub stays read-only and only exposes approved content previews.
        </div>
      </SectionFrame>
    )
  }

  return (
    <SectionFrame eyebrow="Knowledge Detail" title={item.title} subtitle="Read-only preview from the approved knowledge sources.">
      <div className="flex flex-wrap items-center gap-2">
        <ScopeBadge scope={item.scope} source={item.source} />
        <span className="rounded-full bg-black/[0.04] px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-black/42">
          {item.kind}
        </span>
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-[24px] border border-black/8 bg-[var(--paper-strong)] p-5">
          <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.2em] text-black/35">
            <BookOpenText className="h-3.5 w-3.5" />
            <span>Metadata</span>
          </div>
          <dl className="mt-4 space-y-3 text-sm text-black/60">
            <div>
              <dt className="text-[11px] uppercase tracking-[0.2em] text-black/35">Path</dt>
              <dd className="mt-1 break-all">{item.path}</dd>
            </div>
            <div>
              <dt className="text-[11px] uppercase tracking-[0.2em] text-black/35">Updated</dt>
              <dd className="mt-1">{new Date(item.updatedAt).toLocaleString('en-US')}</dd>
            </div>
          </dl>
        </div>
        <div className="rounded-[24px] border border-black/8 bg-[var(--paper-strong)] p-5">
          <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.2em] text-black/35">
            <BookOpenText className="h-3.5 w-3.5" />
            <span>Tags</span>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {item.tags.map((tag) => (
              <span key={tag} className="rounded-full bg-black/[0.04] px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-black/42">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div className="mt-5 rounded-[24px] border border-black/8 bg-black/[0.02] p-5">
        <div className="mb-4 flex items-center gap-2 text-[11px] uppercase tracking-[0.2em] text-black/35">
          <ScrollText className="h-3.5 w-3.5" />
          <span>Preview Content</span>
        </div>
        <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-6 text-black/70">{item.content}</pre>
      </div>
    </SectionFrame>
  )
}
