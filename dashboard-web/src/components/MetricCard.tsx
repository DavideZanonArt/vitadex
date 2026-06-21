type MetricCardProps = {
  label: string
  value: number
  note: string
}

export function MetricCard({ label, value, note }: MetricCardProps) {
  return (
    <article className="rounded-[28px] border border-black/8 bg-white/90 p-5 shadow-[0_20px_60px_rgba(29,29,28,0.06)]">
      <p className="text-[11px] uppercase tracking-[0.24em] text-black/40">{label}</p>
      <div className="mt-4 flex items-end justify-between gap-4">
        <strong className="font-serif text-4xl font-semibold text-black/85">{value}</strong>
        <span className="max-w-[9rem] text-right text-xs leading-5 text-black/45">{note}</span>
      </div>
    </article>
  )
}
