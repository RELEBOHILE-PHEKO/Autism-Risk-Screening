import {
  BadgeCheck,
  Ban,
  Database,
  FileText,
  Lock,
  ScrollText,
  ShieldAlert,
  UserX,
} from 'lucide-react'
import { GlassCard } from './glass-card'

const DATA_CLAUSES = [
  {
    icon: Database,
    title: 'What data this screening uses',
    body: 'The model was trained and validated on de-identified, secondary Q-CHAT-10 datasets from New Zealand, Saudi Arabia, and Poland, plus Lesotho DHS 2023–24 microdata used only for threshold calibration. No directly identifiable participant information is contained in these sources.',
  },
  {
    icon: UserX,
    title: 'What happens to your answers',
    body: 'Your checklist answers are sent to the scoring API to generate a result and are not stored, logged, or linked to you or your child afterward. Nothing you enter is used to retrain the model.',
  },
  {
    icon: ShieldAlert,
    title: 'This is a screening aid, not a diagnosis',
    body: 'A risk score from Lesedi Lens is an indication for further assessment, never a medical diagnosis. Only a qualified clinician can confirm or rule out a developmental condition.',
  },
  {
    icon: Lock,
    title: 'Ethical approval & oversight',
    body: 'This project operates under ALU Senate Research Ethics Committee approval (Code M26-BSE-026, issued 18 June 2026). Any material change to how this tool interacts with participants is reported to the REC within 48 hours.',
  },
  {
    icon: Ban,
    title: 'Licensing & permitted use',
    body: 'Lesotho DHS data carries restrictions on downstream commercial use. In line with that, this tool is made available for research, clinical-support, and non-commercial use only, unless separate permission is obtained.',
  },
  {
    icon: BadgeCheck,
    title: 'Fairness commitment',
    body: 'Model performance is audited across age and sex subgroups (see the Fairness tab) before anything ships toward clinical use, so no single group bears a disproportionate error rate.',
  },
]

export function PrivacyTab() {
  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-3">
        <div className="flex items-center gap-2 text-primary">
          <ScrollText className="size-5" aria-hidden="true" />
          <span className="hud-label">privacy &amp; terms</span>
        </div>
        <h2 className="font-serif text-2xl font-semibold text-balance">
          Privacy Policy &amp; Terms of Use
        </h2>
        <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground text-pretty">
          This page explains, in plain language, what happens to the information you enter,
          what this tool can and cannot be used for, and the ethical oversight behind it.
          Read this before using the Screening tab.
        </p>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {DATA_CLAUSES.map((clause) => (
          <GlassCard key={clause.title} className="flex items-start gap-4 p-5">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-teal/15 text-teal">
              <clause.icon className="size-5" aria-hidden="true" />
            </div>
            <div>
              <h3 className="font-serif text-lg font-semibold">{clause.title}</h3>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground text-pretty">
                {clause.body}
              </p>
            </div>
          </GlassCard>
        ))}
      </section>

      <GlassCard className="border-l-4 border-l-clay p-5">
        <div className="flex items-center gap-2 text-clay">
          <FileText className="size-5" aria-hidden="true" />
          <h3 className="font-serif text-lg font-semibold">Consent to proceed</h3>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground text-pretty">
          By continuing to the Screening tab, you confirm you understand this tool provides a
          calibrated risk indication only, that your answers are not stored beyond generating
          that result, and that any next step should be discussed with a qualified health
          worker.
        </p>
      </GlassCard>
    </div>
  )
}
