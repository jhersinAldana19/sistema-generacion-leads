import { cn } from '@/lib/utils'

export function ChatMessage({ role, content }: { role: 'user' | 'assistant'; content: string }) {
  const isUser = role === 'user'
  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-xl rounded-lg px-3 py-2 text-sm',
          isUser
            ? 'bg-brand text-white dark:bg-dark-surface-hover'
            : 'bg-gray-100 text-gray-800 dark:bg-white/5 dark:text-dark-text',
        )}
      >
        {content}
      </div>
    </div>
  )
}
