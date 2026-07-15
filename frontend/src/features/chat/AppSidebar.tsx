import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'

import logoWhite from '@/assets/branding/logo-tecport-blanco.webp'
import { Avatar } from '@/components/ui/avatar'
import { ThemeToggle } from '@/components/ThemeToggle'
import type { Conversation, User } from '@/types/api'
import { useLogout } from '@/features/auth/useAuth'
import { ConversationList } from '@/features/chat/ConversationList'
import { listsApi } from '@/features/lists/listsApi'

export function AppSidebar({
  user,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onRenameConversation,
  onDeleteConversation,
}: {
  user: User
  conversations: Conversation[]
  activeConversationId: number | null
  onSelectConversation: (id: number) => void
  onNewConversation: () => void
  onRenameConversation: (id: number, title: string) => void
  onDeleteConversation: (id: number) => void
}) {
  const logout = useLogout()
  const [showLists, setShowLists] = useState(false)
  const { data: lists = [] } = useQuery({ queryKey: ['lists'], queryFn: listsApi.list, enabled: showLists })

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col bg-brand-dark">
      <div className="flex items-center justify-between px-3 pb-1 pt-3">
        <img src={logoWhite} alt="Tecport" className="h-6 w-auto" />
        <ThemeToggle />
      </div>

      <div className="p-2">
        <button
          onClick={onNewConversation}
          className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm font-medium text-white/90 hover:bg-white/10"
        >
          <Plus className="size-4" />
          Nueva conversación
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        <p className="px-2 pb-1 pt-2 text-xs font-semibold uppercase tracking-wide text-white/40">Historial</p>
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={onSelectConversation}
          onRename={onRenameConversation}
          onDelete={onDeleteConversation}
        />

        <button
          onClick={() => setShowLists((value) => !value)}
          className="mt-4 w-full px-2 pb-1 pt-2 text-left text-xs font-semibold uppercase tracking-wide text-white/40 hover:text-white/70"
        >
          Listas guardadas {showLists ? '▾' : '▸'}
        </button>
        {showLists && (
          <ul className="space-y-0.5 px-0">
            {lists.length === 0 && <p className="px-2 text-xs text-white/40">Sin listas todavía.</p>}
            {lists.map((list) => (
              <li key={list.id} className="truncate rounded-md px-2 py-1.5 text-sm text-white/80">
                {list.name}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="flex items-center gap-2 border-t border-white/10 p-2">
        <Avatar name={user.name} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-white/90">{user.name}</p>
          <button onClick={() => logout.mutate()} className="text-xs text-white/40 hover:text-status-discarded">
            Cerrar sesión
          </button>
        </div>
      </div>
    </aside>
  )
}
