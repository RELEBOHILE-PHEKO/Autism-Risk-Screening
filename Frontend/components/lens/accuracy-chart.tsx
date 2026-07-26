'use client'

import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts'
import { ACCURACY_COMPARISON } from '@/lib/lens-data'

export function AccuracyChart() {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={ACCURACY_COMPARISON}
          margin={{ top: 4, right: 44, bottom: 4, left: 8 }}
          barCategoryGap={16}
        >
          <XAxis type="number" domain={[0.6, 1]} hide />
          <YAxis
            type="category"
            dataKey="tool"
            width={124}
            tickLine={false}
            axisLine={false}
            tick={{ fill: '#a7c3cc', fontSize: 12, fontWeight: 600 }}
          />
          <Bar dataKey="auroc" radius={[6, 6, 6, 6]} isAnimationActive={false}>
            {ACCURACY_COMPARISON.map((entry) => (
              <Cell
                key={entry.tool}
                fill={entry.self ? 'var(--gold)' : 'color-mix(in srgb, #a7c3cc 45%, transparent)'}
              />
            ))}
            <LabelList
              dataKey="auroc"
              position="right"
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
