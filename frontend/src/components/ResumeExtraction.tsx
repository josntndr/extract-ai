import { Badge } from '@/components/ui/Badge'
import type { Extraction, ResumeData } from '@/types'
import { humanize } from '@/lib/utils'

function isResumeData(data: unknown): data is ResumeData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'skills' in data &&
    'experience' in data
  )
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

function yearRange(start: unknown, end: unknown): string | null {
  const s = start ?? ''
  const e = end ?? ''
  if (!s && !e) return null
  return `${s || '?'} – ${e || 'Present'}`
}

export function ResumeExtraction({ extraction }: { extraction: Extraction }) {
  const { data, missing_fields } = extraction

  if (!isResumeData(data)) {
    return (
      <div className="space-y-4">
        <MissingFields fields={missing_fields} />
        <pre className="scrollbar-thin overflow-x-auto rounded border border-line bg-paper p-4 font-mono text-[12.5px] leading-relaxed text-ink">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Identity */}
      <div>
        {data.name && (
          <h2 className="font-display text-2xl font-medium text-ink">{data.name}</h2>
        )}
        <dl className="mt-3 divide-y divide-line border-y border-line">
          <FieldRow label="Email" value={data.email} />
          <FieldRow label="Phone" value={data.phone} />
          <FieldRow label="Location" value={data.location} />
        </dl>
      </div>

      {data.summary && (
        <section>
          <SectionTitle>Summary</SectionTitle>
          <p className="text-sm leading-relaxed text-ink-soft">{data.summary}</p>
        </section>
      )}

      {data.skills?.length > 0 && (
        <section>
          <SectionTitle>Skills</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {data.skills.map((skill, i) => (
              <Badge key={`${skill}-${i}`} variant="tag">
                {skill}
              </Badge>
            ))}
          </div>
        </section>
      )}

      {data.experience?.length > 0 && (
        <section>
          <SectionTitle>Experience</SectionTitle>
          <ul className="space-y-3">
            {data.experience.map((exp, i) => (
              <li
                key={i}
                className="border-l-2 border-accent/40 pl-4"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-1">
                  <p className="font-medium text-ink">
                    {exp.title || 'Role'}
                    {exp.company && (
                      <span className="font-normal text-ink-soft"> · {exp.company}</span>
                    )}
                  </p>
                  {yearRange(exp.start_date, exp.end_date) && (
                    <span className="font-mono text-[11px] text-ink-faint">
                      {yearRange(exp.start_date, exp.end_date)}
                    </span>
                  )}
                </div>
                {exp.summary && (
                  <p className="mt-1 text-sm leading-relaxed text-ink-soft">
                    {exp.summary}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {data.education?.length > 0 && (
        <section>
          <SectionTitle>Education</SectionTitle>
          <ul className="space-y-3">
            {data.education.map((edu, i) => (
              <li key={i} className="flex flex-wrap items-baseline justify-between gap-1">
                <div>
                  <p className="font-medium text-ink">
                    {edu.institution || 'Institution'}
                  </p>
                  <p className="text-sm text-ink-soft">
                    {[edu.degree, edu.field_of_study].filter(Boolean).join(', ')}
                  </p>
                </div>
                {yearRange(edu.start_year, edu.end_year) && (
                  <span className="font-mono text-[11px] text-ink-faint">
                    {yearRange(edu.start_year, edu.end_year)}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      <MissingFields fields={missing_fields} />
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
