import {
  ROADMAP_CHALLENGE,
  ROADMAP_METRICS,
  ROADMAP_SOLUTION,
} from '@/lib/lens-data'
import { cn } from '@/lib/utils'
import { ArrowRight, TriangleAlert, Sparkles } from 'lucide-react'
import { GlassCard } from './glass-card'

type Step = { stat: string; title: string; body: string }

function Track({
  eyebrow,
  steps,
  tone,
}: {
  eyebrow: string
  steps: readonly Step[]
  tone: 'challenge' | 'solution'
}) {
  const isSolution = tone === 'solution'
  const accent = isSolution ? 'var(--risk-low)' : 'var(--clay)'
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <span
          className="flex size-6 items-center justify-center rounded-md"
          style={{ background: `color-mix(in srgb, ${accent} 18%, transparent)` }}
        >
          {isSolution ? (
            <Sparkles className="size-3.5" style={{ color: accent }} aria-hidden="true" />
          ) : (
            <TriangleAlert className="size-3.5" style={{ color: accent }} aria-hidden="true" />
          )}
        </span>
        <span className="hud-label" style={{ color: accent }}>
          {eyebrow}
        </span>
      </div>

      {/* Vertical connected timeline */}
      <ol className="relative flex flex-col gap-3">
        <span
          className="absolute bottom-3 left-[15px] top-3 w-px"
          style={{ background: `color-mix(in srgb, ${accent} 35%, transparent)` }}
          aria-hidden="true"
        />
        {steps.map((s, i) => (
          <li key={s.title} className="relative">
            <GlassCard className="p-4 pl-12">
              {/* Node */}
              <span
                className="absolute left-[7px] top-4 flex size-4 items-center justify-center rounded-full"
                style={{
                  background: accent,
                  boxShadow: `0 0 12px -2px color-mix(in srgb, ${accent} 80%, transparent)`,
                }}
                aria-hidden="true"
              >
                <span className="font-mono text-[8px] font-bold text-background">{i + 1}</span>
              </span>
              <div className="flex items-baseline gap-2">
                <span
                  className="font-serif text-lg font-semibold leading-none"
                  style={{ color: accent }}
                >
                  {s.stat}
                </span>
                <h4 className="text-sm font-semibold text-foreground text-balance">{s.title}</h4>
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground text-pretty">
                {s.body}
              </p>
            </GlassCard>
          </li>
        ))}
      </ol>
    </div>
  )
}

export function Roadmap() {
  return (
    <GlassCard strong className="hud-frame overflow-hidden p-6">
      <div className="flex flex-col gap-1">
        <span className="hud-label">research roadmap</span>
        <h2 className="font-serif text-2xl font-semibold text-balance">
          Transforming autism screening in Lesotho
        </h2>
        <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground text-pretty">
          How a machine-learning approach turns a high-burden challenge into a calibrated,
          capacity-aware screening tool.
        </p>
      </div>

      {/* Blanket stripe divider */}
      <div className="blanket-stripes my-6 h-1.5 w-full rounded-full opacity-80" aria-hidden="true" />

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[1fr_auto_1fr]">
        <Track eyebrow="The challenge in Lesotho" steps={ROADMAP_CHALLENGE} tone="challenge" />

        {/* Center transition arrow */}
        <div className="flex items-center justify-center lg:h-full lg:flex-col">
          <span className="glow-gold flex size-11 items-center justify-center rounded-full bg-primary text-primary-foreground">
            <ArrowRight className="size-5 lg:rotate-0" aria-hidden="true" />
          </span>
        </div>

        <Track eyebrow="The machine-learning solution" steps={ROADMAP_SOLUTION} tone="solution" />
      </div>

      {/* Metric comparison */}
      <div className="mt-6 rounded-xl border border-border/60 bg-foreground/[0.03] p-4">
        <div className="mb-3 grid grid-cols-[1.4fr_1fr_1fr] items-center gap-2">
          <span className="hud-label">metric comparison</span>
          <span className="text-center text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
            Standard Q-CHAT-10
          </span>
          <span className="text-center text-[11px] font-semibold uppercase tracking-wide text-primary">
            Proposed ML model
          </span>
        </div>
        <div className="flex flex-col divide-y divide-border/50">
          {ROADMAP_METRICS.map((m) => (
            <div
              key={m.label}
              className="grid grid-cols-[1.4fr_1fr_1fr] items-center gap-2 py-2.5"
            >
              <span className="text-sm font-medium text-foreground">{m.label}</span>
              <span className="text-center text-sm text-muted-foreground">{m.standard}</span>
              <span
                className={cn(
                  'mx-auto w-fit rounded-full px-2.5 py-0.5 text-center text-sm font-semibold',
                  m.proposedGood
                    ? 'bg-[color-mix(in_srgb,var(--risk-low)_18%,transparent)] text-[var(--risk-low)]'
                    : 'text-muted-foreground',
                )}
              >
                {m.proposed}
              </span>
            </div>
          ))}
        </div>
      </div>
    </GlassCard>
  )
}
