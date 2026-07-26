'use client'

import { useState } from 'react'
import { BarChart3, ClipboardCheck, Info, Scale, ScrollText } from 'lucide-react'
import { AppHeader } from '@/components/lens/app-header'
import { SceneBackground } from '@/components/lens/scene-background'
import { OverviewTab } from '@/components/lens/overview-tab'
import { ScreeningTab } from '@/components/lens/screening-tab'
import { AboutTab } from '@/components/lens/about-tab'
import { FairnessTab } from '@/components/lens/fairness-tab'
import { PrivacyTab } from '@/components/lens/privacy-tab'
import { cn } from '@/lib/utils'

const TABS = [
  { id: 'overview', label: 'Overview', icon: BarChart3, hint: 'Model at a glance' },
  { id: 'screening', label: 'Screening', icon: ClipboardCheck, hint: 'Q-CHAT-10 checklist' },
  { id: 'about', label: 'About', icon: Info, hint: 'How it works' },
  { id: 'fairness', label: 'Fairness', icon: Scale, hint: 'Subgroup equity' },
  { id: 'privacy', label: 'Privacy', icon: ScrollText, hint: 'Terms & data use' },
] as const

type TabId = (typeof TABS)[number]['id']

export default function Page() {
  const [tab, setTab] = useState<TabId>('overview')

  return (
    <>
      <SceneBackground />

      <main className="relative z-10 min-h-screen pb-20">
        <AppHeader />

        <div className="mx-auto flex max-w-6xl flex-col gap-6 px-5 sm:px-8 lg:flex-row lg:gap-8">
          {/* Vertical side rail */}
          <nav
            className="hud-frame glass sticky top-3 z-20 flex shrink-0 gap-1.5 overflow-x-auto rounded-2xl p-2 lg:top-6 lg:mt-2 lg:h-fit lg:w-64 lg:flex-col lg:overflow-visible lg:p-3"
            role="tablist"
            aria-label="Sections"
          >
            {/* HUD rail header */}
            <div className="hidden items-center justify-between px-2 pb-2 lg:flex">
              <span className="hud-label">nav · modules</span>
              <span className="font-mono text-[10px] text-muted-foreground/70">
                {String(TABS.findIndex((t) => t.id === tab) + 1).padStart(2, '0')}/
                {String(TABS.length).padStart(2, '0')}
              </span>
            </div>

            {TABS.map((t, i) => {
              const active = tab === t.id
              return (
                <button
                  key={t.id}
                  type="button"
                  role="tab"
                  aria-selected={active}
                  onClick={() => setTab(t.id)}
                  className={cn(
                    'group relative flex items-center gap-3 rounded-xl px-3 py-3 text-left transition-all duration-200',
                    'flex-1 justify-center lg:flex-none lg:justify-start',
                    active
                      ? 'bg-primary text-primary-foreground shadow-[0_10px_28px_-10px_var(--gold)]'
                      : 'text-muted-foreground hover:bg-foreground/5 hover:text-foreground',
                  )}
                >
                  {/* Active edge marker */}
                  <span
                    className={cn(
                      'absolute left-0 top-1/2 hidden h-6 w-[3px] -translate-y-1/2 rounded-full bg-primary-foreground transition-opacity lg:block',
                      active ? 'opacity-90' : 'opacity-0',
                    )}
                    aria-hidden="true"
                  />
                  <span
                    className={cn(
                      'flex size-8 shrink-0 items-center justify-center rounded-lg transition-colors',
                      active
                        ? 'bg-primary-foreground/15'
                        : 'bg-foreground/5 group-hover:bg-foreground/10',
                    )}
                  >
                    <t.icon className="size-4" aria-hidden="true" />
                  </span>
                  <span className="hidden flex-1 flex-col leading-tight lg:flex">
                    <span className="text-sm font-semibold">{t.label}</span>
                    <span
                      className={cn(
                        'text-[11px] font-medium',
                        active ? 'text-primary-foreground/70' : 'text-muted-foreground/70',
                      )}
                    >
                      {t.hint}
                    </span>
                  </span>
                  {/* Mono module index */}
                  <span
                    className={cn(
                      'hidden font-mono text-[10px] tabular-nums lg:block',
                      active ? 'text-primary-foreground/60' : 'text-muted-foreground/50',
                    )}
                    aria-hidden="true"
                  >
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <span className="text-sm font-semibold sm:hidden lg:hidden">{t.label}</span>
                </button>
              )
            })}

            {/* HUD rail footer */}
            <div className="mt-1 hidden items-center gap-2 px-2 pt-2 lg:flex">
              <span className="hud-dot" aria-hidden="true" />
              <span className="hud-label">calibrated · ready</span>
            </div>
          </nav>

          {/* Panels */}
          <div className="min-w-0 flex-1" role="tabpanel">
            {tab === 'overview' && <OverviewTab onStart={() => setTab('screening')} />}
            {tab === 'screening' && <ScreeningTab />}
            {tab === 'about' && <AboutTab />}
            {tab === 'fairness' && <FairnessTab />}
            {tab === 'privacy' && <PrivacyTab />}
          </div>
        </div>
      </main>
    </>
  )
}
