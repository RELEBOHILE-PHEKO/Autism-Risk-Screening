'use client'

import { AlertTriangle, ClipboardList, Globe, Info } from 'lucide-react'
import { bandForScore, FLAG_THRESHOLD, RISK_COPY } from '@/lib/lens-data'
import { GlassCard } from './glass-card'
import { RiskGauge } from './risk-gauge'

type CulturalNote = { id: number; answer: string; note: string }

type ResultCardProps = {
  score: number
  flaggedCount: number
  culturalNotes?: CulturalNote[]
}

export function ResultCard({ score, flaggedCount, culturalNotes = [] }: ResultCardProps) {
  const band = bandForScore(score)
  const copy = RISK_COPY[band]

  return (
    <div className="flex flex-col gap-4">
    <GlassCard strong className="grid grid-cols-1 gap-6 p-6 lg:grid-cols-[1fr_1.1fr] lg:p-8">
      {/* Gauge */}
      <div className="flex items-center justify-center">
        <RiskGauge score={score} />
      </div>

      {/* Explanation */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <span
            className="inline-block size-2.5 rounded-full"
            style={{ background: copy.token, boxShadow: `0 0 12px ${copy.token}` }}
          />
          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            What this means
          </span>
        </div>
        <h3
          className="font-serif text-2xl font-semibold leading-tight text-balance"
          style={{ color: copy.token }}
        >
          {copy.title}
        </h3>
        <p className="text-sm leading-relaxed text-muted-foreground text-pretty">
          {copy.body}
        </p>

        <div className="flex items-center gap-3 rounded-xl border border-border bg-background/25 p-3">
          <ClipboardList className="size-5 shrink-0 text-primary" aria-hidden="true" />
          <p className="text-sm text-foreground">
            <span className="font-semibold">{flaggedCount}</span> of 10 items fell outside
            the typical range. The referral threshold is{' '}
            <span className="font-semibold">{FLAG_THRESHOLD}</span> or more.
          </p>
        </div>

        <div className="flex items-start gap-2 rounded-xl border border-primary/25 bg-primary/5 p-3">
          {band === 'high' ? (
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-risk-high" aria-hidden="true" />
          ) : (
            <Info className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
          )}
          <p className="text-xs leading-relaxed text-muted-foreground text-pretty">
            Lesedi Lens is a screening aid, not a diagnosis. Only a qualified clinician can
            assess your child. Share this result at your next visit.
          </p>
        </div>
      </div>
    </GlassCard>

      {/* Cultural-alignment notes — distinctive to the Lesotho calibration */}
      {culturalNotes.length > 0 && (
        <GlassCard className="flex flex-col gap-4 p-6">
          <div className="flex items-center gap-2">
            <Globe className="size-4 text-primary" aria-hidden="true" />
            <span className="hud-label">Cultural alignment · Sesotho context</span>
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground text-pretty">
            A few communication items don&apos;t transfer cleanly to Sesotho-speaking homes.
            Read these answers with local context before drawing conclusions.
          </p>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {culturalNotes.map((n) => (
              <div
                key={n.id}
                className="flex flex-col gap-2 rounded-xl border border-border bg-background/25 p-4"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold text-primary">
                    Q{n.id}
                  </span>
                  <span className="rounded-full bg-foreground/5 px-2.5 py-0.5 text-[11px] font-semibold text-foreground">
                    {n.answer}
                  </span>
                </div>
                <p className="text-xs leading-relaxed text-muted-foreground text-pretty">
                  {n.note}
                </p>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  )
}
