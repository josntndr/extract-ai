import { Link, Navigate, Outlet, useLocation } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import {
  useCurrentUser,
  useIsAuthenticated,
  useLogout,
} from '@/hooks/useAuth'
import { cn } from '@/lib/utils'
import { Wordmark } from '@/components/Wordmark'

const NAV = [{ to: '/', label: 'Documents' }]

export function ProtectedLayout() {
  const isAuthed = useIsAuthenticated()
  const location = useLocation()
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  if (!isAuthed) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  const initials = (user?.full_name || user?.email || '?')
    .trim()
    .slice(0, 1)
    .toUpperCase()

  return (
    <div className="flex min-h-screen">
      {/* Sidebar (desktop) */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-line bg-paper-card px-3 py-5 md:flex">
        <div className="px-2">
          <Wordmark />
        </div>

        <nav className="mt-8 flex-1">
          <p className="px-2 pb-2 eyebrow">Workspace</p>
          {NAV.map((item) => {
            const active = location.pathname === item.to
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  'relative flex items-center rounded px-3 py-2 text-sm font-medium transition-colors',
                  active
                    ? 'bg-paper-sunk text-ink'
                    : 'text-ink-soft hover:bg-paper-sunk/60 hover:text-ink',
                )}
              >
                {active && (
                  <span className="absolute left-0 top-1/2 h-4 w-[3px] -translate-y-1/2 rounded-full bg-accent" />
                )}
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="border-t border-line pt-4">
          {user && (
            <div className="mb-3 flex items-center gap-2.5 px-2">
              <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-ink font-mono text-xs text-paper-card">
                {initials}
              </span>
              <div className="min-w-0">
                <p className="truncate text-[13px] font-medium text-ink">
                  {user.full_name || user.email}
                </p>
                <p className="truncate font-mono text-[11px] text-ink-faint">
                  {user.email}
                </p>
              </div>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            loading={logout.isPending}
            onClick={() => logout.mutate()}
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col bg-canvas">
        {/* Topbar (mobile) */}
        <header className="flex items-center justify-between border-b border-line bg-paper-card px-4 py-3 md:hidden">
          <Wordmark />
          <Button
            variant="ghost"
            size="icon"
            loading={logout.isPending}
            onClick={() => logout.mutate()}
            aria-label="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-8 lg:px-10">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
