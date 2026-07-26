import { cn } from '@/lib/utils'

export function StripeBar({ className }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        'blanket-stripes h-1.5 w-full rounded-full opacity-90',
        className,
      )}
    />
  )
}
