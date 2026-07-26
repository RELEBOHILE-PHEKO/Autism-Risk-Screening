import { Check, Minus } from 'lucide-react'
import { COMPARISON_FEATURES } from '@/lib/lens-data'

function Mark({ on }: { on: boolean }) {
  return on ? (
    <span className="inline-flex size-6 items-center justify-center rounded-full bg-risk-low/20 text-risk-low">
      <Check className="size-4" aria-label="Yes" />
    </span>
  ) : (
    <span className="inline-flex size-6 items-center justify-center rounded-full bg-muted text-muted-foreground">
      <Minus className="size-4" aria-label="No" />
    </span>
  )
}

export function ComparisonTable() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] border-collapse text-left">
        <thead>
          <tr className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
            <th className="px-3 py-3 font-semibold">Capability</th>
            <th className="px-3 py-3 text-center font-semibold text-primary">Lesedi Lens</th>
            <th className="px-3 py-3 text-center font-semibold">Q-CHAT-10</th>
            <th className="px-3 py-3 text-center font-semibold">M-CHAT-R/F</th>
          </tr>
        </thead>
        <tbody>
          {COMPARISON_FEATURES.map((row) => (
            <tr key={row.feature} className="border-t border-border/70">
              <td className="px-3 py-3 text-sm text-foreground">{row.feature}</td>
              <td className="px-3 py-3 text-center">
                <div className="flex justify-center">
                  <Mark on={row.lesedi} />
                </div>
              </td>
              <td className="px-3 py-3 text-center">
                <div className="flex justify-center">
                  <Mark on={row.qchat} />
                </div>
              </td>
              <td className="px-3 py-3 text-center">
                <div className="flex justify-center">
                  <Mark on={row.mchat} />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
