import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AlertTriangle, ArrowLeft, ChevronDown, Loader2, RefreshCw } from 'lucide-react'
import { PageTransition } from '@/components/PageTransition'
import { ResumeExtraction } from '@/components/ResumeExtraction'
import { InvoiceExtraction } from '@/components/InvoiceExtraction'
import { StatusBadge } from '@/components/StatusBadge'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { useDocument, useReprocessDocument } from '@/hooks/useDocuments'
import { cn, formatBytes, formatConfidence, formatDate, humanize } from '@/lib/utils'

function MetaRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-2.5">
      <dt className="eyebrow">{label}</dt>
      <dd className="text-right font-mono text-[12.5px] tnum text-ink">{value}</dd>
    </div>
  )
}

export function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: doc, isLoading, isError } = useDocument(id)
  const reprocess = useReprocessDocument()
  const [showRaw, setShowRaw] = useState(false)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24 text-ink-faint">
        <Loader2 className="h-5 w-5 animate-spin" />
      </div>
    )
  }

  if (isError || !doc) {
    return (
      <div className="py-24 text-center">
        <p className="text-sm text-err">Could not load this document.</p>
        <Link
          to="/"
          className="mt-4 inline-block text-sm font-medium text-accent hover:underline"
        >
          Back to documents
        </Link>
      </div>
    )
  }

  const isPending = doc.status === 'uploaded' || doc.status === 'processing'

  return (
    <PageTransition>
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-[13px] font-medium text-ink-soft hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" />
        Documents
      </Link>

      {/* Header */}
      <header className="mt-4 flex flex-wrap items-start justify-between gap-4 border-b border-line pb-5">
        <div className="min-w-0">
          <div className="mb-2 flex items-center gap-2.5">
            <StatusBadge status={doc.status} />
            <Badge variant="tag">{humanize(doc.doc_type)}</Badge>
          </div>
          <h1 className="break-all font-display text-2xl font-medium leading-tight text-ink">
            {doc.filename}
          </h1>
          <p className="mt-1 font-mono text-[12px] text-ink-faint">
            {formatDate(doc.created_at)}
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => id && reprocess.mutate(id)}
          loading={reprocess.isPending}
          disabled={isPending}
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Reprocess
        </Button>
      </header>

      {/* Failed banner */}
      {doc.status === 'failed' && (
        <div className="mt-6 flex items-start gap-3 rounded-md border border-err-line bg-err-soft p-4">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-err" />
          <div>
            <p className="text-sm font-medium text-err">Processing failed</p>
            <p className="mt-0.5 text-sm text-err/80">
              {doc.error_message || 'An unknown error occurred.'}
            </p>
          </div>
        </div>
      )}

      <div className="mt-6 grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        {/* Extracted data (primary) */}
        <section className="order-2 space-y-6 lg:order-1">
          {isPending && (
            <div className="flex items-center gap-2.5 rounded-md border border-line bg-paper-card px-5 py-4 text-sm text-ink-soft">
              <Loader2 className="h-4 w-4 animate-spin text-accent" />
              Processing this document — the page updates automatically when ready.
            </div>
          )}

          {doc.extraction && (
            <div className="rounded-md border border-line bg-paper-card">
              <div className="flex items-center justify-between border-b border-line px-5 py-3">
                <h2 className="font-display text-base font-medium text-ink">
                  Extracted fields
                </h2>
                <div className="flex items-center gap-2">
                  <Badge variant="tag">{doc.extraction.model}</Badge>
                  {doc.extraction.confidence != null && (
                    <Badge variant="neutral">
                      {formatConfidence(doc.extraction.confidence)} filled
                    </Badge>
                  )}
                </div>
              </div>
              <div className="p-5">
                {doc.doc_type === 'invoice' ? (
                  <InvoiceExtraction extraction={doc.extraction} />
                ) : (
                  <ResumeExtraction extraction={doc.extraction} />
                )}
              </div>
            </div>
          )}

          {/* Raw text (collapsible) */}
          {doc.extracted_text && (
            <div className="rounded-md border border-line bg-paper-card">
              <button
                type="button"
                onClick={() => setShowRaw((v) => !v)}
                className="flex w-full items-center justify-between px-5 py-3 text-left"
              >
                <h2 className="font-display text-base font-medium text-ink">
                  Source text
                </h2>
                <ChevronDown
                  className={cn(
                    'h-4 w-4 text-ink-faint transition-transform',
                    showRaw && 'rotate-180',
                  )}
                />
              </button>
              {showRaw && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="overflow-hidden border-t border-line"
                >
                  <pre className="scrollbar-thin max-h-96 overflow-auto whitespace-pre-wrap p-5 font-mono text-[12.5px] leading-relaxed text-ink-soft">
                    {doc.extracted_text}
                  </pre>
                </motion.div>
              )}
            </div>
          )}
        </section>

        {/* Metadata (aside) */}
        <aside className="order-1 lg:order-2 lg:sticky lg:top-8">
          <div className="rounded-md border border-line bg-paper-card px-5 py-1">
            <p className="border-b border-line py-3 eyebrow">Pipeline</p>
            <dl className="divide-y divide-line">
              <MetaRow label="Source" value={humanize(doc.source)} />
              <MetaRow label="Pages" value={doc.page_count ?? '—'} />
              <MetaRow label="OCR conf." value={formatConfidence(doc.ocr_confidence)} />
              <MetaRow
                label="Time"
                value={doc.processing_ms != null ? `${doc.processing_ms} ms` : '—'}
              />
              <MetaRow label="Size" value={formatBytes(doc.size_bytes)} />
              <MetaRow label="MIME" value={doc.content_type} />
            </dl>
          </div>
        </aside>
      </div>
    </PageTransition>
  )
}
