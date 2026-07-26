'use client'

import { cn } from '@/lib/utils'

type SegmentedControlProps = {
  options: { label: string }[]
  value: number | null
  onChange: (index: number) => void
  name: string
  ariaLabel: string
}

export function SegmentedControl({
  options,
  value,
  onChange,
  name,
  ariaLabel,
}: SegmentedControlProps) {
  return (
    <div
      role="radiogroup"
      aria-label={ariaLabel}
      className="grid grid-cols-5 gap-1 rounded-xl border border-border bg-background/30 p-1"
    >
      {options.map((opt, i) => {
        const selected = value === i
        return (
          <button
            key={opt.label}
            type="button"
            role="radio"
            aria-checked={selected}
            name={name}
            onClick={() => onChange(i)}
            className={cn(
              'rounded-lg px-1 py-2 text-center text-xs font-semibold transition-all duration-200',
              selected
                ? 'bg-primary text-primary-foreground shadow-[0_6px_16px_-6px_var(--gold)]'
                : 'text-muted-foreground hover:bg-foreground/5 hover:text-foreground',
            )}
          >
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}
