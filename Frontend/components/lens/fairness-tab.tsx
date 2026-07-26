import { FAIRNESS_OVERALL, FAIRNESS_SUBGROUPS } from '@/lib/lens-data'
import { FairnessChart } from './fairness-chart'
import { GlassCard } from './glass-card'

function getDeltaColor(delta: number) {
  return delta < 0 ? 'var(--clay)' : 'var(--risk-low)'
}

export function FairnessTab() {
  return (
    <div className="flex flex-col gap-6">
      <section className="flex flex-col gap-3">
        <h2 className="font-serif text-2xl font-semibold text-balance">
          Fairness across subgroups
        </h2>
        <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground text-pretty">
          A screening tool is only trustworthy if it serves each child fairly. We review
          the F1 score across sex and age groups and compare each result with the overall
          F1 of {FAIRNESS_OVERALL} to spot any group that needs extra attention.
        </p>
      </section>

      <GlassCard className="p-6">
        <h3 className="font-serif text-lg font-semibold">
          Subgroup fairness — F1 by demographic group
        </h3>
        <p className="mt-1 text-sm text-muted-foreground text-pretty">
          The dashed line marks the overall F1 ({FAIRNESS_OVERALL}). The results stay close
          to that line, which is a good sign of balanced performance.
        </p>
        <div className="mt-4">
          <FairnessChart />
        </div>
      </GlassCard>

      <GlassCard className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[420px] border-collapse text-left">
            <thead>
              <tr className="bg-background/30 text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                <th className="px-5 py-3 font-semibold">Subgroup</th>
                <th className="px-5 py-3 font-semibold">Type</th>
                <th className="px-5 py-3 font-semibold">F1 score</th>
                <th className="px-5 py-3 font-semibold">vs. overall</th>
              </tr>
            </thead>
            <tbody>
              {FAIRNESS_SUBGROUPS.map((row) => {
                const delta = row.f1 - FAIRNESS_OVERALL
                const deltaText = `${delta >= 0 ? '+' : ''}${delta.toFixed(3)}`

                return (
                  <tr key={row.group} className="border-t border-border/70">
                    <td className="px-5 py-3 text-sm font-medium text-foreground">
                      {row.group}
                    </td>
                    <td className="px-5 py-3 text-sm capitalize text-muted-foreground">
                      {row.kind}
                    </td>
                    <td className="px-5 py-3 text-sm tabular-nums">
                      <span
                        style={{ color: row.kind === 'age' ? 'var(--gold)' : 'var(--teal)' }}
                      >
                        {row.f1.toFixed(3)}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-sm tabular-nums">
                      <span className="font-semibold" style={{ color: getDeltaColor(delta) }}>
                        {deltaText}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  )
}
