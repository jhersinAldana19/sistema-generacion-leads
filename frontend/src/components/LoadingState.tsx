import { Loader2 } from 'lucide-react'

export function LoadingState({ label = 'Cargando…' }: { label?: string }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-2 text-sm text-gray-500 dark:text-dark-text-muted">
      <Loader2 className="size-5 animate-spin" />
      <span>{label}</span>
    </div>
  )
}
