'use client'

import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts'
import { FAIRNESS_OVERALL, FAIRNESS_SUBGROUPS } from '@/lib/lens-data'

export function FairnessChart() {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={FAIRNESS_SUBGROUPS}
          margin={{ top: 24, right: 16, bottom: 4, left: 0 }}
          barCategoryGap="28%"
        >
          <XAxis
            dataKey="group"
            tickLine={false}
            axisLine={{ stroke: 'color-mix(in srgb, var(--teal) 40%, transparent)' }}
            tick={{ fill: '#a7c3cc', fontSize: 12, fontWeight: 600 }}
          />
          <YAxis
            domain={[0, 0.8]}
            ticks={[0, 0.2, 0.4, 0.6, 0.8]}
            tickLine={false}
            axisLine={false}
            width={36}
            tick={{ fill: '#7f9aa3', fontSize: 11 }}
          />
          <ReferenceLine
            y={FAIRNESS_OVERALL}
            stroke="var(--clay)"
            strokeDasharray="6 4"
            strokeWidth={1.5}
            label={{
              value: `Overall F1 = ${FAIRNESS_OVERALL}`,
              position: 'insideTopLeft',
              fill: 'var(--clay)',
              fontSize: 11,
              fontWeight: 700,
            }}
          />
          <Bar dataKey="f1" radius={[6, 6, 0, 0]} isAnimationActive={false}>
            {FAIRNESS_SUBGROUPS.map((entry) => (
              <Cell
                key={entry.group}
                fill={entry.kind === 'age' ? 'var(--gold)' : 'var(--teal)'}
              />
            ))}
            <LabelList
              dataKey="f1"
              position="top"
              formatter={(value) =>
                typeof value === 'number' ? value.toFixed(3) : String(value ?? '')
              }
              fill="#eaf3f5"
              fontSize={12}
              fontWeight={700}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
