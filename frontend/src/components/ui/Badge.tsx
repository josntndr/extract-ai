import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-sm px-2 py-0.5 text-[11px] font-medium ring-1 ring-inset',
  {
    variants: {
      variant: {
        neutral: 'bg-paper-sunk text-ink-soft ring-line',
        accent: 'bg-accent-soft text-accent ring-accent-line',
        success: 'bg-ok-soft text-ok ring-ok-line',
        warning: 'bg-wait-soft text-wait ring-wait-line',
        danger: 'bg-err-soft text-err ring-err-line',
        muted: 'bg-transparent text-ink-faint ring-line',
        // Mono "tag" style for document types / codes.
        tag: 'bg-paper-card font-mono uppercase tracking-wide text-ink-soft ring-line',
      },
    },
    defaultVariants: {
      variant: 'neutral',
    },
  },
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { badgeVariants }
