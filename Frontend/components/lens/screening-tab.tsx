'use client'

import { useMemo, useRef, useState } from 'react'
import { AlertTriangle, RotateCcw, Sparkles } from 'lucide-react'
import { CULTURAL_NOTES, QUESTIONS, SCALE } from '@/lib/lens-data'
import { predictRisk, scoreForProb } from '@/lib/api'
import { ContextSidebar, type ContextState } from './context-sidebar'
import { QuestionCard } from './question-card'
import { ResultCard } from './result-card'

const TOTAL_QUESTIONS = QUESTIONS.length

function flagFor(questionIndex: number, answerIndex: number) {
  const question = QUESTIONS[questionIndex]

  if (question.reverse) {
    return answerIndex <= 2 ? 1 : 0
  }

  return SCALE[answerIndex].value
}

type ResultState = {
  score: number
  atRisk: boolean
}

function createEmptyAnswers() {
  return Array.from({ length: TOTAL_QUESTIONS }, () => null as number | null)
}

export function ScreeningTab() {
  const [context, setContext] = useState<ContextState>({
    ageMonths: 24,
    sex: 'girl',
    prematurity: false,
    familyHistory: false,
  })
  const [answers, setAnswers] = useState<(number | null)[]>(createEmptyAnswers())
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ResultState | null>(null)
  const resultRef = useRef<HTMLDivElement>(null)

  const answeredCount = answers.filter((answer) => answer !== null).length
  const progress = Math.round((answeredCount / TOTAL_QUESTIONS) * 100)
  const isComplete = answeredCount === TOTAL_QUESTIONS

  const flaggedCount = useMemo(() => {
    return answers.reduce<number>((total, answer, index) => {
      if (answer === null) {
        return total
      }

      return total + flagFor(index, answer)
    }, 0)
  }, [answers])

  const culturalNotes = useMemo(() => {
    return QUESTIONS.flatMap((question, index) => {
      const note = CULTURAL_NOTES[question.id]
      if (!note) {
        return []
      }

      const answerIndex = answers[index]
      return [
        {
          id: question.id,
          answer: answerIndex !== null ? SCALE[answerIndex].label : '—',
          note,
        },
      ]
    })
  }, [answers])

  const handleAnswer = (index: number, value: number) => {
    setAnswers((previous) => {
      const next = [...previous]
      next[index] = value
      return next
    })
  }

  const handleSubmit = async () => {
    setError(null)
    setLoading(true)

    try {
      const encoded = answers.map((answer, index) =>
        answer === null ? 0 : flagFor(index, answer),
      )

      const response = await predictRisk(encoded)

      setResult({
        score: scoreForProb(response.risk_score, response.threshold),
        atRisk: response.at_risk,
      })
      setSubmitted(true)

      requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      })
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not reach the scoring service. Check that the API is running.',
      )
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setAnswers(createEmptyAnswers())
    setSubmitted(false)
    setResult(null)
    setError(null)
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
      <aside className="lg:sticky lg:top-6 lg:self-start">
        <ContextSidebar value={context} onChange={setContext} />
      </aside>

      <div className="flex flex-col gap-6">
        <div className="glass sticky top-4 z-10 flex items-center gap-4 rounded-2xl p-4">
          <div className="flex-1">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-medium text-foreground">Your answers</span>
              <span className="font-semibold text-primary">
                {answeredCount}/{TOTAL_QUESTIONS}
              </span>
            </div>
            <div
              className="h-2.5 w-full overflow-hidden rounded-full bg-background/40"
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <div
                className="h-full rounded-full bg-primary transition-all duration-500"
                style={{
                  width: `${progress}%`,
                  boxShadow: '0 0 12px -1px var(--gold)',
                }}
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {QUESTIONS.map((question, index) => (
            <QuestionCard
              key={question.id}
              question={question}
              index={index}
              value={answers[index]}
              onChange={(value) => handleAnswer(index, value)}
            />
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!isComplete || loading}
            className="glow-gold inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-all duration-200 hover:brightness-110 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
          >
            <Sparkles className="size-4" aria-hidden="true" />
            {loading ? 'Scoring…' : 'Get my result'}
          </button>

          {submitted && (
            <button
              type="button"
              onClick={handleReset}
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-background/30 px-5 py-3 text-sm font-semibold text-foreground transition-colors hover:bg-foreground/5"
            >
              <RotateCcw className="size-4" aria-hidden="true" />
              Start over
            </button>
          )}

          {!isComplete && (
            <span className="text-sm text-muted-foreground">
              Answer all {TOTAL_QUESTIONS} questions to continue.
            </span>
          )}
        </div>

        {error && (
          <div className="flex items-start gap-2 rounded-xl border border-risk-high/30 bg-risk-high/5 p-3">
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-risk-high" aria-hidden="true" />
            <p className="text-sm text-foreground">{error}</p>
          </div>
        )}

        {submitted && result && (
          <div ref={resultRef} className="scroll-mt-6">
            <ResultCard
              score={result.score}
              flaggedCount={flaggedCount}
              culturalNotes={culturalNotes}
            />
          </div>
        )}
      </div>
    </div>
  )
}

