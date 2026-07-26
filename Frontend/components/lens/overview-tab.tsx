import { STATS } from '@/lib/lens-data'
import { AccuracyChart } from './accuracy-chart'
import { ComparisonTable } from './comparison-table'
import { FeatureGrid } from './feature-grid'
import { GlassCard } from './glass-card'
import { Roadmap } from './roadmap'
import { StatCard } from './stat-card'

export function OverviewTab({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-5">
        <span className="w-fit rounded-full border border-primary/40 bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-primary">
          Q-CHAT-10 · ages 18–36 months
        </span>
        <h1 className="max-w-3xl font-serif text-4xl font-semibold leading-tight text-balance sm:text-5xl">
          A clearer lens on your child&apos;s early development.
        </h1>
        <p className="max-w-2xl text-base leading-relaxed text-muted-foreground text-pretty">
          Lesedi Lens turns a short ten-question behavioural checklist into a calm,
          practical result that families and health workers can talk through together.
        </p>
        <div>
          <button
            type="button"
            onClick={onStart}
            className="glow-gold inline-flex items-center rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-all duration-200 hover:brightness-110 active:translate-y-px"
          >
            Start the screening
          </button>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {STATS.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </section>

      <section>
        <Roadmap />
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="font-serif text-2xl font-semibold text-balance">
          Why this is built differently
        </h2>
        <FeatureGrid />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <GlassCard className="p-6">
          <h2 className="font-serif text-xl font-semibold">Screening accuracy (AUROC)</h2>
          <p className="mt-1 text-sm text-muted-foreground text-pretty">
            Higher is better. These figures compare the tool against common paper-based
            screeners on the same held-out sample.
          </p>
          <div className="mt-4">
            <AccuracyChart />
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <h2 className="font-serif text-xl font-semibold">Feature comparison</h2>
          <p className="mt-1 text-sm text-muted-foreground text-pretty">
            This shows what Lesedi Lens adds on top of the underlying questionnaire.
          </p>
          <div className="mt-4">
            <ComparisonTable />
          </div>
        </GlassCard>
      </section>
    </div>
  )
}
