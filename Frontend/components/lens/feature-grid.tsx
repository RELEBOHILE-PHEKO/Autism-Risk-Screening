import { Gauge, ShieldCheck, WifiOff, HeartHandshake } from 'lucide-react'
import { GlassCard } from './glass-card'

const FEATURES = [
  {
    icon: Gauge,
    title: 'Calibrated, not just a score',
    body: 'Results are turned into honest probabilities, so a "1 in 5" means roughly what it says.',
  },
  {
    icon: ShieldCheck,
    title: 'Audited for fairness',
    body: 'Performance is checked across age and sex subgroups before anything ships to a clinic.',
  },
  {
    icon: WifiOff,
    title: 'Built for the field',
    body: 'Runs on modest devices and low bandwidth, matching how rural clinics actually work.',
  },
  {
    icon: HeartHandshake,
    title: 'Made for caregivers',
    body: 'Plain-language results a parent can read and carry into a conversation with a nurse.',
  },
]

export function FeatureGrid() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {FEATURES.map((f) => (
        <GlassCard key={f.title} interactive className="p-5">
          <div className="flex size-10 items-center justify-center rounded-xl bg-teal/15 text-teal">
            <f.icon className="size-5" aria-hidden="true" />
          </div>
          <h3 className="mt-4 font-serif text-lg font-semibold text-foreground text-balance">
            {f.title}
          </h3>
          <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground text-pretty">
            {f.body}
          </p>
        </GlassCard>
      ))}
    </div>
  )
}
