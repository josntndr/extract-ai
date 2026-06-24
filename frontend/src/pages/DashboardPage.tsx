import { PageTransition } from '@/components/PageTransition'
import { UploadCard } from '@/components/UploadCard'
import { DocumentsTable } from '@/components/DocumentsTable'
import { useDocuments } from '@/hooks/useDocuments'

export function DashboardPage() {
  const { data, isLoading, isError } = useDocuments({ limit: 100, offset: 0 })

  const items = data?.items ?? []
  const completed = items.filter((d) => d.status === 'completed').length
  const active = items.filter(
    (d) => d.status === 'processing' || d.status === 'uploaded',
  ).length

  const stats = [
    ['Documents', data?.total ?? 0],
    ['Completed', completed],
    ['In progress', active],
  ] as const

  return (
    <PageTransition>
      {/* Page header */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="eyebrow">Workspace</p>
          <h1 className="mt-1.5 font-display text-3xl font-medium tracking-tight text-ink">
            Documents
          </h1>
        </div>
        <dl className="flex items-stretch divide-x divide-line rounded-md border border-line bg-paper-card">
          {stats.map(([label, value]) => (
            <div key={label} className="px-5 py-2.5 text-center">
              <dd className="font-mono text-xl font-medium tnum text-ink">{value}</dd>
              <dt className="eyebrow mt-0.5">{label}</dt>
            </div>
          ))}
        </dl>
      </header>

      <div className="mt-8 grid items-start gap-8 lg:grid-cols-[minmax(0,1fr)_22rem]">
        {/* Documents list */}
        <section className="order-2 rounded-md border border-line bg-paper-card lg:order-1">
          <div className="flex items-center justify-between border-b border-line px-5 py-3">
            <h2 className="font-display text-base font-medium text-ink">
              Recent documents
            </h2>
          </div>
          {isError ? (
            <div className="px-5 py-16 text-center text-sm text-err">
              Failed to load documents. Please refresh and try again.
            </div>
          ) : (
            <DocumentsTable documents={items} isLoading={isLoading} />
          )}
        </section>

        {/* Upload (sticky aside on desktop) */}
        <aside className="order-1 lg:order-2 lg:sticky lg:top-8">
          <UploadCard />
        </aside>
      </div>
    </PageTransition>
  )
}
