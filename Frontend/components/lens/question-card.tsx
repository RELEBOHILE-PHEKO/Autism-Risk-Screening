'use client'

import { SCALE, type Question } from '@/lib/lens-data'
import { cn } from '@/lib/utils'
import { GlassCard } from './glass-card'
import { SegmentedControl } from './segmented-control'

type QuestionCardProps = {
  question: Question
  index: number
  value: number | null
  onChange: (value: number) => void
}

export function QuestionCard({ question, index, value, onChange }: QuestionCardProps) {
  const answered = value !== null
  return (
    <GlassCard
      className={cn(
        'flex flex-col gap-4 p-4 transition-all duration-300 sm:p-5',
        answered && 'ring-1 ring-primary/30',
      )}
    >
      <div className="flex items-start gap-3">
        <span
          className={cn(
            'mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg text-xs font-bold transition-colors',
            answered
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground',
          )}
        >
          {index + 1}
        </span>
        <p className="text-sm font-medium leading-relaxed text-foreground text-pretty">
          {question.text}
        </p>
      </div>
      <SegmentedControl
        name={`q-${question.id}`}
        ariaLabel={question.text}
        options={SCALE}
        value={value}
        onChange={onChange}
      />
    </GlassCard>
  )
}
