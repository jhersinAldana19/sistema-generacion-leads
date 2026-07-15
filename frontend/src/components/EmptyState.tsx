import type { ReactNode } from 'react'

export function EmptyState({ title, description }: { title: string; description?: ReactNode }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-gray-200 px-6 py-8 text-center dark:border-dark-border">
      <p className="text-sm font-medium text-gray-700 dark:text-dark-text">{title}</p>
      {description && <p className="text-xs text-gray-500 dark:text-dark-text-muted">{description}</p>}
    </div>
  )
}
