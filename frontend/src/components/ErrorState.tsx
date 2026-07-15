import { AlertTriangle } from 'lucide-react'

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex min-h-32 flex-col items-center justify-center gap-2 rounded-lg border border-red-100 bg-red-50 px-6 py-6 text-center dark:border-status-discarded/30 dark:bg-status-discarded/10">
      <AlertTriangle className="size-5 text-status-discarded" />
      <p className="text-sm text-status-discarded dark:text-red-300">{message}</p>
    </div>
  )
}
