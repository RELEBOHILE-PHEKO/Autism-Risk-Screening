export type ScaleOption = {
  label: string
  value: number // 0 = typical, 1 = flag-contributing
}

// 5-option segmented scale shared across questions.
// Standard Q-CHAT-10 keying: for items 1–9, only "Always"/"Usually" count as
// typical (0); "Sometimes" and rarer answers contribute a flag (1).
// Item 10 is reverse-keyed and handled separately in the screening logic.
export const SCALE: ScaleOption[] = [
  { label: 'Always', value: 0 },
  { label: 'Usually', value: 0 },
  { label: 'Sometimes', value: 1 },
  { label: 'Rarely', value: 1 },
  { label: 'Never', value: 1 },
]

export type Question = {
  id: number
  text: string
  /** When true, the "more often" answers contribute to the flag tally instead. */
  reverse?: boolean
}

// Q-CHAT-10 style behavioural items (18–36 months).
export const QUESTIONS: Question[] = [
  { id: 1, text: 'Does your child look at you when you call their name?' },
  { id: 2, text: 'How easy is it for you to get eye contact with your child?' },
  {
    id: 3,
    text: 'Does your child point to indicate that they want something (e.g. a toy out of reach)?',
  },
  {
    id: 4,
    text: 'Does your child point to share interest with you (e.g. pointing at a passing animal)?',
  },
  {
    id: 5,
    text: 'Does your child pretend during play (e.g. caring for dolls, talking on a toy phone)?',
  },
  { id: 6, text: 'Does your child follow where you are looking?' },
  {
    id: 7,
    text: 'If a family member is visibly upset, does your child try to comfort them?',
  },
  {
    id: 8,
    text: 'Would you describe your child\u2019s first words as clear and typical for their age?',
  },
  { id: 9, text: 'Does your child use simple gestures, such as waving goodbye?' },
  {
    id: 10,
    text: 'Does your child stare at nothing with no apparent purpose for long stretches?',
    reverse: true,
  },
]

export const FLAG_THRESHOLD = 3 // items flagged at or above this trigger a referral suggestion

// Cultural-alignment notes for communication/speech items. During development
// these items were flagged as not transferring cleanly to Sesotho-speaking
// contexts, so the tool surfaces context rather than treating them at face value.
export const CULTURAL_NOTES: Record<number, string> = {
  1: 'Response to name can be shaped by language and everyday communication patterns in Sesotho-speaking homes — interpret with local context.',
  8: 'Early speech develops differently across languages. This item may not transfer directly to Sesotho linguistic norms.',
  9: 'Gestures such as waving vary across cultural settings; the cultural-alignment analysis flagged this item for careful reading.',
}

// ---- Overview stats ----
export const STATS = [
  { label: 'Training records', value: '1,601', hint: 'Caregiver-reported profiles' },
  { label: 'AUROC', value: '0.892', hint: 'Discrimination on held-out data' },
  { label: 'Flag threshold', value: '1%', hint: 'Calibrated referral rate' },
  { label: 'Mode', value: 'Deploy', hint: 'Field-ready configuration' },
]

// ---- Roadmap: challenge -> solution (from research infographic) ----
export const ROADMAP_CHALLENGE = [
  {
    stat: '1 in 100',
    title: 'Children affected',
    body: 'Early identification is critical for outcomes, yet screening remains inaccessible across much of the region.',
  },
  {
    stat: 'Sesotho',
    title: 'Cultural & linguistic gaps',
    body: 'Standard tools lean on communication questions that do not align with local linguistic norms.',
  },
  {
    stat: '84.9%',
    title: 'The "referral burden" problem',
    body: 'Traditional methods flag a very high share of children for assessment — far beyond specialist capacity.',
  },
] as const

export const ROADMAP_SOLUTION = [
  {
    stat: '0.892',
    title: 'AUROC accuracy',
    body: 'A cross-validated logistic regression, selected over XGBoost through CV blend weighting, outperformed standard benchmarks for screening precision.',
  },
  {
    stat: '54.4%',
    title: '30% reduction in referrals',
    body: 'The model cut the referral rate toward specialist capacity while maintaining high screening sensitivity.',
  },
  {
    stat: 'Calibrated',
    title: 'Prior probability correction',
    body: 'Predictions were adjusted to reflect real-world autism prevalence rather than artificial dataset ratios.',
  },
] as const

export const ROADMAP_METRICS = [
  { label: 'Referral burden', standard: '84.9%', proposed: '54.4%', proposedGood: true },
  { label: 'Sensitivity', standard: 'High', proposed: 'Maintained', proposedGood: true },
  { label: 'Specificity', standard: 'Low', proposed: 'Improved', proposedGood: true },
] as const

// ---- Accuracy comparison (mock) ----
export const ACCURACY_COMPARISON = [
  { tool: 'Lesedi Lens', auroc: 0.892, self: true },
  { tool: 'Q-CHAT-10 (raw)', auroc: 0.83, self: false },
  { tool: 'M-CHAT-R/F', auroc: 0.79, self: false },
  { tool: 'CSBS Checklist', auroc: 0.74, self: false },
]

// ---- Feature comparison table (mock) ----
export const COMPARISON_FEATURES = [
  { feature: 'Calibrated probabilities', lesedi: true, qchat: false, mchat: false },
  { feature: 'Local subgroup fairness audit', lesedi: true, qchat: false, mchat: false },
  { feature: 'Offline / low-bandwidth ready', lesedi: true, qchat: true, mchat: false },
  { feature: 'Caregiver-friendly result', lesedi: true, qchat: false, mchat: true },
  { feature: 'Clinician hand-off summary', lesedi: true, qchat: false, mchat: false },
]

// ---- Subgroup fairness: F1 by demographic group (from evaluation run) ----
export const FAIRNESS_OVERALL = 0.765 // overall F1
export type FairnessGroup = {
  group: string
  f1: number
  kind: 'sex' | 'age'
}
export const FAIRNESS_SUBGROUPS: FairnessGroup[] = [
  { group: 'Female', f1: 0.735, kind: 'sex' },
  { group: 'Male', f1: 0.775, kind: 'sex' },
  { group: '18–24m', f1: 0.76, kind: 'age' },
]

export type RiskBand = 'low' | 'mid' | 'high'

export function bandForScore(score: number): RiskBand {
  if (score < 33) return 'low'
  if (score < 66) return 'mid'
  return 'high'
}

export const RISK_COPY: Record<
  RiskBand,
  { title: string; body: string; token: string }
> = {
  low: {
    title: 'Lower likelihood of developmental concern',
    body: 'Responses fall within the typical range for this age. Keep tracking milestones and share this result at your next routine check-up.',
    token: 'var(--risk-low)',
  },
  mid: {
    title: 'Some signals worth watching',
    body: 'A few responses sit outside the typical range. This is not a diagnosis — it is a good reason to talk with a clinic nurse or doctor within the next few weeks.',
    token: 'var(--risk-mid)',
  },
  high: {
    title: 'Referral for further assessment suggested',
    body: 'Several responses suggest a developmental review would help. Please bring this summary to a clinician so they can arrange a full assessment.',
    token: 'var(--risk-high)',
  },
}
