import { GlassCard } from './glass-card'

type StatCardProps = {
  label: string
  value: string
  hint: string
}

export function StatCard({ label, value, hint }: StatCardProps) {
  return (
    <GlassCard interactive className="p-5">
      <div className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </div>
      <div className="mt-2 font-serif text-3xl font-semibold text-foreground">
        {value}
      </div>
      <div className="mt-1 text-sm text-muted-foreground text-pretty">{hint}</div>
    </GlassCard>
  )
}
