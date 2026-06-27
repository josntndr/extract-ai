import { Badge } from '@/components/ui/Badge'
import type { Extraction, InvoiceData } from '@/types'
import { humanize } from '@/lib/utils'

function isInvoiceData(data: unknown): data is InvoiceData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'invoice_number' in data &&
    'line_items' in data
  )
}

function money(value: number | null | undefined, currency?: string | null): string | null {
  if (value === null || value === undefined) return null
  const amount = value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return currency ? `${currency} ${amount}` : amount
}

function FieldRow({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="grid grid-cols-[7rem_1fr] items-baseline gap-3 py-2">
      <dt className="eyebrow pt-0.5">{label}</dt>
      <dd className="text-sm text-ink">
        {value ? value : <span className="text-ink-faint">Not found</span>}
      </dd>
    </div>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="mb-3 flex items-center gap-3 eyebrow text-ink-soft">
      {children}
      <span className="h-px flex-1 bg-line" />
    </h3>
  )
}

export function InvoiceExtraction({ extraction }: { extraction: Extraction }) {
  const { data, missing_fields } = extraction

  if (!isInvoiceData(data)) {
    return (
      <div className="space-y-4">
        <MissingFields fields={missing_fields} />
        <pre className="scrollbar-thin overflow-x-auto rounded border border-line bg-paper p-4 font-mono text-[12.5px] leading-relaxed text-ink">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    )
  }

  const currency = data.currency
  const lineItems = data.line_items ?? []

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          {data.vendor_name && (
            <h2 className="font-display text-2xl font-medium text-ink">
              {data.vendor_name}
            </h2>
          )}
          {data.invoice_number && (
            <span className="font-mono text-[12.5px] text-ink-soft">
              #{data.invoice_number}
            </span>
          )}
        </div>
        <dl className="mt-3 divide-y divide-line border-y border-line">
          <FieldRow label="Bill to" value={data.bill_to} />
          <FieldRow label="Issued" value={data.issue_date} />
          <FieldRow label="Due" value={data.due_date} />
          <FieldRow label="Vendor addr." value={data.vendor_address} />
        </dl>
      </div>

      {/* Line items */}
      {lineItems.length > 0 && (
        <section>
          <SectionTitle>Line items</SectionTitle>
          <div className="overflow-x-auto rounded border border-line">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left eyebrow text-ink-soft">
                  <th className="px-3 py-2 font-normal">Description</th>
                  <th className="px-3 py-2 text-right font-normal">Qty</th>
                  <th className="px-3 py-2 text-right font-normal">Unit</th>
                  <th className="px-3 py-2 text-right font-normal">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {lineItems.map((li, i) => (
                  <tr key={i}>
                    <td className="px-3 py-2 text-ink">{li.description ?? '—'}</td>
                    <td className="px-3 py-2 text-right font-mono tnum text-ink-soft">
                      {li.quantity ?? '—'}
                    </td>
                    <td className="px-3 py-2 text-right font-mono tnum text-ink-soft">
                      {money(li.unit_price, currency) ?? '—'}
                    </td>
                    <td className="px-3 py-2 text-right font-mono tnum text-ink">
                      {money(li.amount, currency) ?? '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Totals */}
      <section>
        <SectionTitle>Totals</SectionTitle>
        <dl className="ml-auto max-w-xs space-y-1">
          <TotalRow label="Subtotal" value={money(data.subtotal, currency)} />
          <TotalRow label="Tax" value={money(data.tax, currency)} />
          <TotalRow label="Total" value={money(data.total, currency)} emphasis />
        </dl>
      </section>

      <MissingFields fields={missing_fields} />
    </div>
  )
}

function TotalRow({
  label,
  value,
  emphasis = false,
}: {
  label: string
  value: string | null
  emphasis?: boolean
}) {
  return (
    <div
      className={
        emphasis
          ? 'flex items-baseline justify-between border-t border-line pt-2 font-medium text-ink'
          : 'flex items-baseline justify-between text-ink-soft'
      }
    >
      <dt className="text-sm">{label}</dt>
      <dd className="font-mono tnum text-sm">
        {value ?? <span className="text-ink-faint">—</span>}
      </dd>
    </div>
  )
}

function MissingFields({ fields }: { fields: string[] }) {
  if (!fields || fields.length === 0) return null
  return (
    <div className="border-t border-line pt-4">
      <p className="mb-2 eyebrow">Not detected</p>
      <div className="flex flex-wrap gap-1.5">
        {fields.map((f) => (
          <Badge key={f} variant="muted">
            {humanize(f)}
          </Badge>
        ))}
      </div>
    </div>
  )
}
