import { cn } from '@/lib/utils'

function initialsFromName(name: string): string {
  const parts = name.trim().split(/\s+/)
  const initials = parts.slice(0, 2).map((part) => part[0]?.toUpperCase() ?? '')
  return initials.join('')
}

const AUTO_PALETTE = [
  'bg-blue-500',
  'bg-emerald-500',
  'bg-amber-500',
  'bg-rose-500',
  'bg-violet-500',
  'bg-cyan-600',
  'bg-orange-500',
  'bg-teal-500',
]

function colorFromName(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) | 0
  }
  return AUTO_PALETTE[Math.abs(hash) % AUTO_PALETTE.length]
}

export function Avatar({
  name,
  className,
  variant = 'brand',
}: {
  name: string
  className?: string
  variant?: 'brand' | 'auto'
}) {
  return (
    <div
      className={cn(
        'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white',
        variant === 'brand' ? 'bg-brand' : colorFromName(name),
        className,
      )}
    >
      {initialsFromName(name)}
    </div>
  )
}
