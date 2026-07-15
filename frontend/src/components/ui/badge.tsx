import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', {
  variants: {
    variant: {
      neutral: 'bg-gray-100 text-gray-700 dark:bg-white/10 dark:text-dark-text',
      confirmed: 'bg-green-100 text-status-confirmed dark:bg-status-confirmed/20 dark:text-green-300',
      review: 'bg-orange-100 text-status-review dark:bg-status-review/20 dark:text-orange-300',
      discarded: 'bg-red-100 text-status-discarded dark:bg-status-discarded/20 dark:text-red-300',
      candidate: 'bg-slate-100 text-status-candidate dark:bg-white/10 dark:text-dark-text-muted',
      probable: 'bg-blue-100 text-status-probable dark:bg-status-probable/20 dark:text-blue-300',
      outdated: 'bg-yellow-100 text-status-outdated dark:bg-status-outdated/20 dark:text-yellow-300',
    },
  },
  defaultVariants: {
    variant: 'neutral',
  },
})

export interface BadgeProps extends React.ComponentProps<'span'>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant, className }))} {...props} />
}
