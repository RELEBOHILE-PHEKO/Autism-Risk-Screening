// Talks to the FastAPI backend (main.py) that replicates the notebook's
// exact deploy_* ensemble pipeline. Set NEXT_PUBLIC_API_URL in .env.local.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export type PredictResponse = {
  risk_score: number // Saerens-corrected probability, calibrated to ~1% prevalence
  at_risk: boolean
  threshold: number
  disclaimer: string
}

export async function predictRisk(answers: number[]): Promise<PredictResponse> {
  const res = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
  })
  if (!res.ok) {
    throw new Error(`Prediction request failed (${res.status})`)
  }
  return res.json()
}

/**
 * The gauge/bandForScore in lib/lens-data.ts assumes a flat 0-100 scale with
 * band edges at 33 (low/mid) and 66 (mid/high). The real model's probability
 * is tiny after Saerens prior correction (deployment prevalence ~1%), so a
 * raw prob*100 would sit near 0 regardless of actual risk.
 *
 * This rescales relative to the model's own decision threshold, matching the
 * Streamlit app's _risk_tier logic exactly:
 *   prob < threshold        -> score in [0, 33)   ("low")
 *   threshold <= prob < 3x  -> score in [33, 66)  ("mid")
 *   prob >= 3x threshold    -> score in [66, 100]  ("high")
 */
export function scoreForProb(prob: number, threshold: number): number {
  if (threshold <= 0) return Math.min(prob * 100, 100)
  const ratio = prob / threshold
  if (ratio <= 1) return ratio * 33
  if (ratio <= 3) return 33 + ((ratio - 1) / 2) * 33
  return Math.min(66 + ((ratio - 3) / 2) * 34, 100)
}
