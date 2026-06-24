import { Navigate, Outlet } from 'react-router-dom'
import { useIsAuthenticated } from '@/hooks/useAuth'
import { BrandMark } from '@/components/Wordmark'

export function AuthLayout() {
  const isAuthed = useIsAuthenticated()
  if (isAuthed) return <Navigate to="/" replace />

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[1.1fr_1fr]">
      {/* Left: editorial brand panel (hidden on small screens) */}
      <aside className="relative hidden flex-col justify-between bg-ink p-12 text-paper-card lg:flex">
        <div className="flex items-center gap-2">
          <BrandMark className="[&_.stroke-ink]:stroke-paper-card" />
          <span className="font-display text-xl font-medium">
            Extract<span className="text-accent">.</span>
          </span>
        </div>

        <div className="max-w-md">
          <p className="eyebrow text-accent">Document intelligence</p>
          <h1 className="mt-4 font-display text-4xl font-medium leading-[1.1]">
            Turn invoices, contracts and resumes into structured data.
          </h1>
          <p className="mt-5 text-[15px] leading-relaxed text-paper-card/70">
            Upload a file. We read it — native PDF text or OCR — and extract
            clean, validated fields you can review, query and export.
          </p>
        </div>

        <dl className="grid grid-cols-3 gap-6 border-t border-paper-card/15 pt-6 font-mono text-paper-card/70">
          {[
            ['OCR', 'EasyOCR · Tesseract'],
            ['Extract', 'GPT-4o structured'],
            ['Store', 'PostgreSQL'],
          ].map(([k, v]) => (
            <div key={k}>
              <dt className="text-[10.5px] uppercase tracking-eyebrow text-accent">{k}</dt>
              <dd className="mt-1 text-[12px] leading-snug">{v}</dd>
            </div>
          ))}
        </dl>
      </aside>

      {/* Right: form */}
      <main className="flex min-h-screen items-center justify-center bg-canvas px-4 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2 lg:hidden">
            <BrandMark />
            <span className="font-display text-xl font-medium text-ink">
              Extract<span className="text-accent">.</span>
            </span>
          </div>
          <Outlet />
        </div>
      </main>
    </div>
  )
}
