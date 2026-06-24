import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Plus, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Label, Select } from '@/components/ui/Input'
import { useUploadDocument } from '@/hooks/useDocuments'
import { cn, formatBytes } from '@/lib/utils'

const ACCEPT = '.pdf,.png,.jpg,.jpeg'
// Values must match the backend DocumentType enum. Only "resume" has a
// fully-typed extraction schema today; the others process text + render raw.
const DOC_TYPES = [
  { value: 'resume', label: 'Resume' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'contract', label: 'Contract' },
  { value: 'medical_form', label: 'Medical Form' },
  { value: 'business_report', label: 'Business Report' },
]

export function UploadCard() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [docType, setDocType] = useState('resume')
  const [dragging, setDragging] = useState(false)
  const upload = useUploadDocument()

  function pickFile(f: File | null | undefined) {
    if (f) setFile(f)
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragging(false)
    pickFile(e.dataTransfer.files?.[0])
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return
    upload.mutate(
      { file, doc_type: docType, process_now: true },
      {
        onSuccess: () => {
          setFile(null)
          if (inputRef.current) inputRef.current.value = ''
        },
      },
    )
  }

  return (
    <div className="rounded-md border border-line bg-paper-card">
      <div className="border-b border-line px-5 py-3">
        <h2 className="font-display text-base font-medium text-ink">New upload</h2>
        <p className="mt-0.5 text-[13px] text-ink-soft">
          PDF, PNG or JPG — up to 50&nbsp;MB.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4 p-5">
        <div
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
          }}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={cn(
            'flex cursor-pointer flex-col items-center justify-center gap-2.5 rounded border border-dashed px-6 py-9 text-center transition-colors',
            dragging
              ? 'border-accent bg-accent-soft/60'
              : 'border-line-strong bg-paper hover:border-accent/60 hover:bg-paper-sunk/50',
          )}
        >
          <span className="grid h-9 w-9 place-items-center rounded-full border border-line bg-paper-card text-ink-soft">
            <Plus className="h-4 w-4" />
          </span>
          <p className="text-sm font-medium text-ink">
            Drop a file here, or click to browse
          </p>
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT}
            className="hidden"
            onChange={(e) => pickFile(e.target.files?.[0])}
          />
        </div>

        {file && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between gap-2 rounded border border-line bg-paper px-3 py-2"
          >
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-ink">{file.name}</p>
              <p className="font-mono text-[11px] tnum text-ink-faint">
                {formatBytes(file.size)}
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                setFile(null)
                if (inputRef.current) inputRef.current.value = ''
              }}
              className="rounded p-1 text-ink-faint hover:bg-paper-sunk hover:text-ink"
              aria-label="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
          </motion.div>
        )}

        <div>
          <Label htmlFor="doc_type">Document type</Label>
          <Select
            id="doc_type"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
          >
            {DOC_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </Select>
        </div>

        <Button
          type="submit"
          variant="accent"
          disabled={!file}
          loading={upload.isPending}
          className="w-full"
        >
          {upload.isPending ? 'Uploading' : 'Upload & process'}
        </Button>

        {upload.isError && (
          <p className="border-l-2 border-err bg-err-soft px-3 py-2 text-sm text-err">
            Upload failed. Please check the file and try again.
          </p>
        )}
      </form>
    </div>
  )
}
