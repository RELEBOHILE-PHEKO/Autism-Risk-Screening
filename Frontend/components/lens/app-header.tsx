import { Eye } from 'lucide-react'
import { StripeBar } from './stripe-bar'

export function AppHeader() {
  return (
    <header className="relative">
      <div className="mx-auto flex max-w-6xl items-center gap-4 px-5 py-6 sm:px-8">
        <div className="glow-gold flex size-11 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-lg">
          <Eye className="size-5" aria-hidden="true" />
        </div>
        <div className="flex flex-col">
          <span className="font-serif text-xl font-semibold tracking-tight text-foreground">
            Lesedi Lens
          </span>
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">
            Early childhood screening · Lesotho
          </span>
        </div>

        {/* HUD status readout */}
        <div className="glass ml-auto hidden items-center gap-3 rounded-lg px-3 py-2 sm:flex">
          <span className="hud-dot" aria-hidden="true" />
          <div className="flex flex-col">
            <span className="hud-label">system · online</span>
            <span className="font-mono text-[11px] font-medium text-foreground/80">
              Q-CHAT-10 · v2.1
            </span>
          </div>
        </div>
      </div>
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <StripeBar />
      </div>
    </header>
  )
}
