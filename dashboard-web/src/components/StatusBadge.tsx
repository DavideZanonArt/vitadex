import { cn } from '@/lib/utils'

type StatusBadgeProps = {
  label: string
  tone?: 'neutral' | 'success' | 'warning' | 'critical'
}

export function StatusBadge({ label, tone = 'neutral' }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex rounded-full border px-2.5 py-1 text-[11px] uppercase tracking-[0.18em]',
        tone === 'neutral' && 'border-black/10 bg-black/[0.03] text-black/60',
        tone === 'success' && 'border-emerald-900/10 bg-emerald-900/[0.06] text-emerald-950/70',
        tone === 'warning' && 'border-amber-900/10 bg-amber-900/[0.07] text-amber-950/70',
        tone === 'critical' && 'border-rose-900/10 bg-rose-900/[0.06] text-rose-950/70',
      )}
    >
      {label}
    </span>
  )
}
