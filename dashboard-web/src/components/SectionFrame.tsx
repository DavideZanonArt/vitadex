import type { ReactNode } from 'react'

type SectionFrameProps = {
  eyebrow: string
  title: string
  subtitle?: string
  children: ReactNode
}

export function SectionFrame({ eyebrow, title, subtitle, children }: SectionFrameProps) {
  return (
    <section className="rounded-[32px] border border-black/8 bg-white/88 p-6 shadow-[0_22px_70px_rgba(17,17,17,0.06)]">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3 border-b border-black/6 pb-4">
        <div>
          <p className="text-[11px] uppercase tracking-[0.24em] text-black/35">{eyebrow}</p>
          <h2 className="mt-2 font-serif text-2xl text-black/85">{title}</h2>
        </div>
        {subtitle ? <p className="max-w-md text-sm leading-6 text-black/45">{subtitle}</p> : null}
      </div>
      {children}
    </section>
  )
}
