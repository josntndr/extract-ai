import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'

/**
 * Brand mark: a document glyph with three "field" rules, the middle one in the
 * clay accent — a nod to fields being lifted out of a page. Hand-drawn in SVG
 * so it reads as a designed mark rather than a stock icon.
 */
export function BrandMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 28 28"
      className={cn('h-7 w-7', className)}
      fill="none"
      aria-hidden="true"
    >
      <rect
        x="5.5"
        y="2.5"
        width="17"
        height="23"
        rx="2"
        className="stroke-ink"
        strokeWidth="1.6"
      />
      <line x1="9.5" y1="9" x2="18.5" y2="9" className="stroke-ink" strokeWidth="1.6" strokeLinecap="round" />
      <line x1="9.5" y1="14" x2="18.5" y2="14" className="stroke-accent" strokeWidth="1.6" strokeLinecap="round" />
      <line x1="9.5" y1="19" x2="15" y2="19" className="stroke-ink" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <Link to="/" className={cn('inline-flex items-center gap-2', className)}>
      <BrandMark />
      <span className="font-display text-[19px] font-medium tracking-tight text-ink">
        Extract<span className="text-accent">.</span>
      </span>
    </Link>
  )
}
