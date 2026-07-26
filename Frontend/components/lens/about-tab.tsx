import React from 'react'
import {
  AlertTriangle,
  Database,
  FileText,
  ListChecks,
  ScanLine,
  Stethoscope,
  Users,
} from 'lucide-react'
import { GlassCard } from './glass-card'

const STEPS = [
  {
    icon: ListChecks,
    title: 'Answer 10 questions',
    body: 'A caregiver responds to short behavioural questions about everyday moments — pointing, eye contact, pretend play.',
  },
  {
    icon: ScanLine,
    title: 'Model reads the pattern',
    body: 'A trained model weighs the answers together with age and context, rather than a simple point tally.',
  },
  {
    icon: FileText,
    title: 'Calibrated result',
    body: 'The output is converted into an honest, plain-language likelihood with a clear referral threshold.',
  },
  {
    icon: Stethoscope,
    title: 'Discuss with a clinician',
    body: 'The summary is designed to hand to a clinic nurse or doctor to guide the next conversation.',
  },
]

const SOURCES = [
  {
    icon: Database,
    title: 'Q-CHAT-10 response bank',
    body: '1,601 de-identified caregiver questionnaires spanning 18–36 months, used for training and validation.',
  },
  {
    icon: Users,
    title: 'Subgroup calibration set',
    body: 'A held-out sample balanced across age windows and sex to check fairness before deployment.',
  },
]

export function AboutTab() {
  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-5">
        <h2 className="font-serif text-2xl font-semibold text-balance">How it works</h2>
        <ol className="relative flex flex-col gap-4 border-l border-border/70 pl-6">
          {STEPS.map((step, i) => (
            <li key={step.title} className="relative">
              <span className="glow-gold absolute -left-[35px] flex size-6 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                {i + 1}
              </span>
              <GlassCard interactive className="flex items-start gap-4 p-5">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-teal/15 text-teal">
                  <step.icon className="size-5" aria-hidden="true" />
                </div>
                <div>
                  <h3 className="font-serif text-lg font-semibold">{step.title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground text-pretty">
                    {step.body}
                  </p>
                </div>
              </GlassCard>
            </li>
          ))}
        </ol>
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="font-serif text-2xl font-semibold text-balance">Data sources</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {SOURCES.map((s) => (
            <GlassCard key={s.title} className="flex items-start gap-4 p-5">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-clay/20 text-clay">
                <s.icon className="size-5" aria-hidden="true" />
              </div>
              <div>
                <h3 className="font-serif text-lg font-semibold">{s.title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-muted-foreground text-pretty">
                  {s.body}
                </p>
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <GlassCard className="border-l-4 border-l-clay p-5">
          <div className="flex items-center gap-2 text-clay">
            <AlertTriangle className="size-5" aria-hidden="true" />
            <h3 className="font-serif text-lg font-semibold">Not a diagnosis</h3>
          </div>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground text-pretty">
            Lesedi Lens flags children who may benefit from a closer look. It cannot confirm
            or rule out any condition — only a qualified clinician can do that.
          </p>
        </GlassCard>
        <GlassCard className="border-l-4 border-l-primary p-5">
          <div className="flex items-center gap-2 text-primary">
            <AlertTriangle className="size-5" aria-hidden="true" />
            <h3 className="font-serif text-lg font-semibold">Know the limits</h3>
          </div>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground text-pretty">
            The tool was calibrated for ages 18–36 months on a Lesotho-representative sample.
            Results outside this range, or for very different populations, should be treated
            with caution.
          </p>
        </GlassCard>
      </section>
    </div>
  )
}
