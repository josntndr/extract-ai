import { useState } from 'react'
import { Link } from 'react-router-dom'
import { AxiosError } from 'axios'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Input, Label } from '@/components/ui/Input'
import { useLogin } from '@/hooks/useAuth'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const login = useLogin()

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    login.mutate({ email, password })
  }

  // The API returns 401 both for a wrong password and for an email that has no
  // account (it doesn't reveal which, by design). So the 401 message nudges
  // new users to sign up, with a register link rendered inline below.
  const isInvalidLogin =
    login.error instanceof AxiosError && login.error.response?.status === 401
  const errorMessage =
    login.error instanceof AxiosError && !isInvalidLogin
      ? 'Something went wrong. Please try again.'
      : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
    >
      <p className="eyebrow">Sign in</p>
      <h2 className="mt-2 font-display text-2xl font-medium text-ink">
        Welcome back
      </h2>
      <p className="mt-1 text-sm text-ink-soft">
        Sign in to your workspace to continue.
      </p>

      <form onSubmit={onSubmit} className="mt-7 space-y-4">
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
          />
        </div>
        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Your password"
          />
        </div>
        {isInvalidLogin && (
          <p className="border-l-2 border-err bg-err-soft px-3 py-2 text-sm text-err">
            We couldn&apos;t sign you in. Double-check your email and password —
            or if you don&apos;t have an account yet,{' '}
            <Link
              to="/register"
              className="font-medium underline underline-offset-2"
            >
              create one here
            </Link>
            .
          </p>
        )}
        {errorMessage && (
          <p className="border-l-2 border-err bg-err-soft px-3 py-2 text-sm text-err">
            {errorMessage}
          </p>
        )}
        <Button type="submit" className="w-full" loading={login.isPending}>
          Sign in
        </Button>
      </form>

      <p className="mt-6 text-sm text-ink-soft">
        No account yet?{' '}
        <Link
          to="/register"
          className="font-medium text-accent underline-offset-4 hover:underline"
        >
          Create one
        </Link>
      </p>
    </motion.div>
  )
}
