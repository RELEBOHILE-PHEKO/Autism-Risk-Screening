'use client'

import { useEffect, useRef, useState } from 'react'
import { bandForScore, type RiskBand } from '@/lib/lens-data'

const CX = 160
const CY = 168
const R = 124
const STROKE = 26

const BAND_COLOR: Record<RiskBand, string> = {
  low: 'var(--risk-low)',
  mid: 'var(--risk-mid)',
  high: 'var(--risk-high)',
}

function polar(angle: number, r = R) {
  const rad = (angle * Math.PI) / 180
  return { x: CX + r * Math.sin(rad), y: CY - r * Math.cos(rad) }
}

// score 0..100 -> angle -90 (left) .. +90 (right)
function scoreToAngle(score: number) {
  return -90 + (score / 100) * 180
}

function arc(scoreStart: number, scoreEnd: number, r = R) {
  const a0 = scoreToAngle(scoreStart)
  const a1 = scoreToAngle(scoreEnd)
  const start = polar(a0, r)
  const end = polar(a1, r)
  const largeArc = a1 - a0 > 180 ? 1 : 0
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`
}

type RiskGaugeProps = {
  score: number
  thresholdScore?: number
}

export function RiskGauge({ score, thresholdScore = 33 }: RiskGaugeProps) {
  const [animScore, setAnimScore] = useState(0)
  const raf = useRef<number | null>(null)

  useEffect(() => {
    const start = performance.now()
    const from = 0
    const duration = 1100
    const tick = (now: number) => {
      const t = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - t, 3)
      setAnimScore(from + (score - from) * eased)
      if (t < 1) raf.current = requestAnimationFrame(tick)
    }
    raf.current = requestAnimationFrame(tick)
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current)
    }
  }, [score])

  const band = bandForScore(score)
  const color = BAND_COLOR[band]
  const needleAngle = scoreToAngle(animScore)
  const glow = 4 + (animScore / 100) * 16
  const threshTip = polar(scoreToAngle(thresholdScore), R + STROKE / 2 + 6)
  const threshBase = polar(scoreToAngle(thresholdScore), R - STROKE / 2 - 6)

  return (
    <div className="relative flex flex-col items-center">
      <svg
        viewBox="0 0 320 200"
        className="w-full max-w-sm"
        role="img"
        aria-label={`Risk score ${Math.round(score)} out of 100`}
      >
        <defs>
          <linearGradient id="hubGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.9" />
            <stop offset="45%" stopColor="#dfe9ec" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#0f2632" stopOpacity="0.9" />
          </linearGradient>
          <radialGradient id="hubGlow" cx="50%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
            <stop offset="100%" stopColor={color} stopOpacity="0.15" />
          </radialGradient>
          <filter id="trackInner" x="-20%" y="-20%" width="140%" height="140%">
            <feOffset dx="0" dy="3" />
            <feGaussianBlur stdDeviation="3" result="offset-blur" />
            <feComposite operator="out" in="SourceGraphic" in2="offset-blur" result="inverse" />
            <feFlood floodColor="#000000" floodOpacity="0.5" result="color" />
            <feComposite operator="in" in="color" in2="inverse" result="shadow" />
            <feComposite operator="over" in="shadow" in2="SourceGraphic" />
          </filter>
          <filter id="needleGlow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation={glow} result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Dim track with inner shadow */}
        <path
          d={arc(0, 100)}
          fill="none"
          stroke="color-mix(in srgb, #eaf3f5 10%, transparent)"
          strokeWidth={STROKE}
          strokeLinecap="round"
          filter="url(#trackInner)"
        />

        {/* Colored zones */}
        <path d={arc(1, 33)} fill="none" stroke="var(--risk-low)" strokeWidth={STROKE} strokeLinecap="round" opacity={0.85} />
        <path d={arc(34, 66)} fill="none" stroke="var(--risk-mid)" strokeWidth={STROKE} opacity={0.85} />
        <path d={arc(67, 99)} fill="none" stroke="var(--risk-high)" strokeWidth={STROKE} strokeLinecap="round" opacity={0.85} />

        {/* Threshold marker */}
        <line
          x1={threshBase.x}
          y1={threshBase.y}
          x2={threshTip.x}
          y2={threshTip.y}
          stroke="#eaf3f5"
          strokeWidth={2.5}
          strokeDasharray="4 3"
          strokeLinecap="round"
        />

        {/* Needle */}
        <g
          transform={`rotate(${needleAngle} ${CX} ${CY})`}
          filter="url(#needleGlow)"
          style={{ transition: 'none' }}
        >
          <polygon
            points={`${CX - 6},${CY} ${CX + 6},${CY} ${CX + 1.5},${CY - R + 14} ${CX - 1.5},${CY - R + 14}`}
            fill={color}
          />
        </g>

        {/* Glossy hub */}
        <circle cx={CX} cy={CY} r="26" fill="url(#hubGlow)" opacity="0.5" />
        <circle cx={CX} cy={CY} r="18" fill="url(#hubGrad)" stroke={color} strokeWidth="2" />
        <ellipse cx={CX} cy={CY - 6} rx="9" ry="5" fill="#ffffff" opacity="0.5" />
      </svg>

      {/* Readout */}
      <div className="-mt-14 flex flex-col items-center">
        <span
          className="font-serif text-5xl font-semibold tabular-nums"
          style={{ color, textShadow: `0 0 24px color-mix(in srgb, ${color} 60%, transparent)` }}
        >
          {Math.round(animScore)}
          <span className="text-2xl">%</span>
        </span>
        <span className="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
          Estimated likelihood
        </span>
      </div>

      <div className="mt-2 flex w-full max-w-sm justify-between px-6 text-[11px] font-semibold text-muted-foreground">
        <span>Lower</span>
        <span>Refer</span>
      </div>
    </div>
  )
}
