'use client'

import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { GlassCard } from './glass-card'

export type ContextState = {
  ageMonths: number
  sex: 'girl' | 'boy'
  prematurity: boolean
  familyHistory: boolean
}

type ContextSidebarProps = {
  value: ContextState
  onChange: (next: ContextState) => void
}

export function ContextSidebar({ value, onChange }: ContextSidebarProps) {
  return (
    <GlassCard strong className="flex flex-col gap-6 p-6">
      <div>
        <h2 className="font-serif text-lg font-semibold">About the child</h2>
        <p className="mt-1 text-xs text-muted-foreground text-pretty">
          Context helps a clinician read the result. It does not change your answers.
        </p>
      </div>

      {/* Age slider */}
      <div className="flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <label htmlFor="age" className="text-sm font-medium text-foreground">
            Age
          </label>
          <span className="font-serif text-lg font-semibold text-primary">
            {value.ageMonths} mo
          </span>
        </div>
        <input
          id="age"
          type="range"
          min={18}
          max={36}
          step={1}
          value={value.ageMonths}
          onChange={(e) => onChange({ ...value, ageMonths: Number(e.target.value) })}
          className="lens-range"
          style={{
            background: `linear-gradient(to right, var(--gold) 0%, var(--gold) ${
              ((value.ageMonths - 18) / 18) * 100
            }%, color-mix(in srgb, #eaf3f5 16%, transparent) ${
              ((value.ageMonths - 18) / 18) * 100
            }%, color-mix(in srgb, #eaf3f5 16%, transparent) 100%)`,
          }}
        />
        <div className="flex justify-between text-[11px] font-medium text-muted-foreground">
          <span>18 mo</span>
          <span>36 mo</span>
        </div>
      </div>

      {/* Sex toggle */}
      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium text-foreground">Sex</span>
        <div className="grid grid-cols-2 gap-1 rounded-xl border border-border bg-background/30 p-1">
          {(['girl', 'boy'] as const).map((s) => (
            <button
              key={s}
              type="button"
              aria-pressed={value.sex === s}
              onClick={() => onChange({ ...value, sex: s })}
              className={cn(
                'rounded-lg py-2 text-sm font-semibold capitalize transition-all duration-200',
                value.sex === s
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Checkboxes */}
      <div className="flex flex-col gap-3">
        <GlassCheckbox
          label="Born more than 3 weeks early"
          checked={value.prematurity}
          onChange={(c) => onChange({ ...value, prematurity: c })}
        />
        <GlassCheckbox
          label="Family history of developmental concerns"
          checked={value.familyHistory}
          onChange={(c) => onChange({ ...value, familyHistory: c })}
        />
      </div>

      <style>{`
        .lens-range {
          -webkit-appearance: none;
          appearance: none;
          width: 100%;
          height: 8px;
          border-radius: 999px;
          outline: none;
          cursor: pointer;
        }
        .lens-range::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 22px;
          height: 22px;
          border-radius: 999px;
          background: #fff;
          border: 3px solid var(--gold);
          box-shadow: 0 0 14px -2px var(--gold), 0 3px 8px rgba(0, 0, 0, 0.4);
          cursor: pointer;
        }
        .lens-range::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 999px;
          background: #fff;
          border: 3px solid var(--gold);
          box-shadow: 0 0 14px -2px var(--gold);
          cursor: pointer;
        }
      `}</style>
    </GlassCard>
  )
}

function GlassCheckbox({
  label,
  checked,
  onChange,
}: {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="flex items-center gap-3 rounded-xl border border-border bg-background/20 p-3 text-left transition-colors hover:bg-foreground/5"
    >
      <span
        className={cn(
          'flex size-5 shrink-0 items-center justify-center rounded-md border transition-all duration-200',
          checked
            ? 'border-primary bg-primary text-primary-foreground'
            : 'border-border bg-transparent',
        )}
      >
        {checked && <Check className="size-3.5" aria-hidden="true" />}
      </span>
      <span className="text-sm font-medium text-foreground text-pretty">{label}</span>
    </button>
  )
}
