import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

const fieldBase =
  'flex h-10 w-full rounded border border-line bg-paper-card px-3 py-2 text-sm text-ink transition-colors ' +
  'placeholder:text-ink-faint ' +
  'focus-visible:outline-none focus-visible:border-accent focus-visible:ring-2 focus-visible:ring-accent/20 ' +
  'disabled:cursor-not-allowed disabled:opacity-50'

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = 'text', ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(fieldBase, className)}
        {...props}
      />
    )
  },
)
Input.displayName = 'Input'

export interface LabelProps
  extends React.LabelHTMLAttributes<HTMLLabelElement> {}

export function Label({ className, ...props }: LabelProps) {
  return (
    <label
      className={cn('mb-1.5 block eyebrow text-ink-soft', className)}
      {...props}
    />
  )
}

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={cn(fieldBase, 'cursor-pointer appearance-none pr-8', className)}
        {...props}
      >
        {children}
      </select>
    )
  },
)
Select.displayName = 'Select'
