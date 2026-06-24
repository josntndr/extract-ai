import type { DocumentStatus } from '@/types'
import { cn, humanize } from '@/lib/utils'

const MAP: Record<DocumentStatus, { dot: string; text: string; pulse?: boolean }> = {
  uploaded: { dot: 'bg-ink-faint', text: 'text-ink-soft' },
  processing: { dot: 'bg-wait', text: 'text-wait', pulse: true },
  completed: { dot: 'bg-ok', text: 'text-ok' },
  failed: { dot: 'bg-err', text: 'text-err' },
}

export function StatusBadge({ status }: { status: DocumentStatus }) {
  const config = MAP[status] ?? MAP.uploaded
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-eyebrow',
        config.text,
      )}
    >
      <span className="relative flex h-2 w-2">
        {config.pulse && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-wait opacity-60" />
        )}
        <span className={cn('relative inline-flex h-2 w-2 rounded-full', config.dot)} />
      </span>
      {humanize(status)}
    </span>
  )
}
