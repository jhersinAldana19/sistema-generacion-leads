import { useState, type KeyboardEvent } from 'react'
import { Check, Pencil, Trash2, X } from 'lucide-react'

import { cn } from '@/lib/utils'
import type { Conversation } from '@/types/api'

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onRename,
  onDelete,
}: {
  conversations: Conversation[]
  activeId: number | null
  onSelect: (id: number) => void
  onRename: (id: number, title: string) => void
  onDelete: (id: number) => void
}) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [draftTitle, setDraftTitle] = useState('')

  if (conversations.length === 0) {
    return <p className="px-2 text-xs text-white/40">Sin conversaciones todavía.</p>
  }

  const startEditing = (conversation: Conversation) => {
    setEditingId(conversation.id)
    setDraftTitle(conversation.title)
  }

  const commitEdit = () => {
    if (editingId !== null) {
      const trimmed = draftTitle.trim()
      if (trimmed) onRename(editingId, trimmed)
    }
    setEditingId(null)
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') commitEdit()
    if (event.key === 'Escape') setEditingId(null)
  }

  return (
    <ul className="space-y-0.5">
      {conversations.map((conversation) => {
        const isEditing = editingId === conversation.id
        return (
          <li key={conversation.id} className="group relative">
            {isEditing ? (
              <div className="flex items-center gap-1 rounded-md bg-white/10 px-2 py-1">
                <input
                  autoFocus
                  value={draftTitle}
                  onChange={(event) => setDraftTitle(event.target.value)}
                  onKeyDown={handleKeyDown}
                  onBlur={commitEdit}
                  className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none"
                />
                <button onMouseDown={(e) => e.preventDefault()} onClick={commitEdit} className="text-white/50 hover:text-status-confirmed">
                  <Check className="size-3.5" />
                </button>
                <button
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => setEditingId(null)}
                  className="text-white/50 hover:text-status-discarded"
                >
                  <X className="size-3.5" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => onSelect(conversation.id)}
                className={cn(
                  'flex w-full items-center rounded-md px-2 py-1.5 text-left text-sm text-white/70 hover:bg-white/10',
                  activeId === conversation.id && 'bg-white/10 font-medium text-white',
                )}
              >
                <span className="min-w-0 flex-1 truncate pr-1">{conversation.title}</span>
                <span className="ml-auto hidden shrink-0 items-center gap-1 group-hover:flex">
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={(event) => {
                      event.stopPropagation()
                      startEditing(conversation)
                    }}
                    className="rounded p-1 text-white/50 hover:bg-white/20 hover:text-white"
                  >
                    <Pencil className="size-3.5" />
                  </span>
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={(event) => {
                      event.stopPropagation()
                      if (confirm(`¿Eliminar "${conversation.title}"?`)) onDelete(conversation.id)
                    }}
                    className="rounded p-1 text-white/50 hover:bg-red-500/20 hover:text-red-300"
                  >
                    <Trash2 className="size-3.5" />
                  </span>
                </span>
              </button>
            )}
          </li>
        )
      })}
    </ul>
  )
}
