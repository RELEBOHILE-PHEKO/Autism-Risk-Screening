import { cn } from '@/lib/utils'
import type { ComponentPropsWithoutRef } from 'react'

type GlassCardProps = ComponentPropsWithoutRef<'div'> & {
  strong?: boolean
  interactive?: boolean
}

export function GlassCard({
  className,
  strong,
  interactive,
  children,
  ...props
}: GlassCardProps) {
  return (
    <div
      className={cn(
        strong ? 'glass-strong' : 'glass',
        'rounded-2xl',
        interactive &&
          'transition-all duration-300 will-change-transform hover:-translate-y-1 hover:shadow-[0_28px_70px_-28px_rgba(0,0,0,0.75)]',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}
