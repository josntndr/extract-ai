import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-canvas px-4 text-center">
      <p className="font-mono text-sm uppercase tracking-eyebrow text-accent">
        Error 404
      </p>
      <h1 className="font-display text-3xl font-medium text-ink">
        Page not found
      </h1>
      <p className="max-w-sm text-sm text-ink-soft">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link to="/" className="mt-2">
        <Button variant="secondary">Back to documents</Button>
      </Link>
    </div>
  )
}
