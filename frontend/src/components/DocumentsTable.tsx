import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowUpRight } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { StatusBadge } from '@/components/StatusBadge'
import type { DocumentResponse } from '@/types'
import { formatDate, humanize } from '@/lib/utils'

interface Props {
  documents: DocumentResponse[]
  isLoading?: boolean
}

export function DocumentsTable({ documents, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="divide-y divide-line">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 px-5 py-4">
            <div className="h-4 w-44 animate-pulse rounded-sm bg-paper-sunk" />
            <div className="ml-auto h-4 w-20 animate-pulse rounded-sm bg-paper-sunk" />
          </div>
        ))}
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-1 px-6 py-20 text-center">
        <p className="font-display text-base text-ink">No documents yet</p>
        <p className="max-w-xs text-sm text-ink-soft">
          Upload a file above and its extracted data will be listed here.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-line">
            <th className="px-5 py-2.5 eyebrow font-normal">Document</th>
            <th className="px-5 py-2.5 eyebrow font-normal">Type</th>
            <th className="px-5 py-2.5 eyebrow font-normal">Status</th>
            <th className="hidden px-5 py-2.5 eyebrow font-normal md:table-cell">
              Uploaded
            </th>
            <th className="px-5 py-2.5" />
          </tr>
        </thead>
        <tbody>
          {documents.map((doc, i) => (
            <motion.tr
              key={doc.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2, delay: Math.min(i * 0.025, 0.25) }}
              className="group border-b border-line/70 last:border-0 hover:bg-paper-sunk/60"
            >
              <td className="px-5 py-3.5">
                <Link
                  to={`/documents/${doc.id}`}
                  className="block max-w-[20rem] truncate font-medium text-ink decoration-accent/40 underline-offset-4 hover:underline"
                >
                  {doc.filename}
                </Link>
              </td>
              <td className="px-5 py-3.5">
                <Badge variant="tag">{humanize(doc.doc_type)}</Badge>
              </td>
              <td className="px-5 py-3.5">
                <StatusBadge status={doc.status} />
              </td>
              <td className="hidden px-5 py-3.5 font-mono text-[12.5px] tnum text-ink-soft md:table-cell">
                {formatDate(doc.created_at)}
              </td>
              <td className="px-5 py-3.5 text-right">
                <Link
                  to={`/documents/${doc.id}`}
                  className="inline-flex items-center text-ink-faint transition-colors group-hover:text-accent"
                  aria-label={`Open ${doc.filename}`}
                >
                  <ArrowUpRight className="h-4 w-4" />
                </Link>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
