import { cn } from '@/lib/utils'

function initialsFromName(name: string): string {
  const parts = name.trim().split(/\s+/)
  const initials = parts.slice(0, 2).map((part) => part[0]?.toUpperCase() ?? '')
  return initials.join('')
}

export function Avatar({ name, className }: { name: string; className?: string }) {
  return (
    <div
      className={cn(
        'flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand text-xs font-semibold text-white',
        className,
      )}
    >
      {initialsFromName(name)}
    </div>
  )
}
