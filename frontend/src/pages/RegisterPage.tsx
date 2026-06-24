import { useState } from 'react'
import { Link } from 'react-router-dom'
import { AxiosError } from 'axios'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Input, Label } from '@/components/ui/Input'
import { useRegister } from '@/hooks/useAuth'

export function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const register = useRegister()

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    register.mutate({
      email,
      password,
      full_name: fullName.trim() || undefined,
    })
  }

  const errorMessage =
    register.error instanceof AxiosError
      ? register.error.response?.status === 409 ||
        register.error.response?.status === 400
        ? 'An account with that email may already exist.'
        : 'Something went wrong. Please try again.'
      : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
    >
      <p className="eyebrow">Get started</p>
      <h2 className="mt-2 font-display text-2xl font-medium text-ink">
        Create your account
      </h2>
      <p className="mt-1 text-sm text-ink-soft">
        Start extracting structured data from your documents.
      </p>

      <form onSubmit={onSubmit} className="mt-7 space-y-4">
        <div>
          <Label htmlFor="full_name">Full name</Label>
          <Input
            id="full_name"
            autoComplete="name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Ada Lovelace"
          />
        </div>
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
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
          />
        </div>
        {errorMessage && (
          <p className="border-l-2 border-err bg-err-soft px-3 py-2 text-sm text-err">
            {errorMessage}
          </p>
        )}
        <Button type="submit" className="w-full" loading={register.isPending}>
          Create account
        </Button>
      </form>

      <p className="mt-6 text-sm text-ink-soft">
        Already have an account?{' '}
        <Link
          to="/login"
          className="font-medium text-accent underline-offset-4 hover:underline"
        >
          Sign in
        </Link>
      </p>
    </motion.div>
  )
}
