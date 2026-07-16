import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, X } from 'lucide-react'

import logoWhite from '@/assets/branding/logo-tecport-blanco.webp'
import { Avatar } from '@/components/ui/avatar'
import { ThemeToggle } from '@/components/ThemeToggle'
import { cn } from '@/lib/utils'
import type { Conversation, SavedList, SearchListItem, User } from '@/types/api'
import { useLogout } from '@/features/auth/useAuth'
import { ConversationList } from '@/features/chat/ConversationList'
import { listsApi } from '@/features/lists/listsApi'
import { searchesApi } from '@/features/searches/searchesApi'

export function AppSidebar({
  user,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onRenameConversation,
  onDeleteConversation,
  onSelectList,
  onSelectSearch,
  open,
  onClose,
}: {
  user: User
  conversations: Conversation[]
  activeConversationId: number | null
  onSelectConversation: (id: number) => void
  onNewConversation: () => void
  onRenameConversation: (id: number, title: string) => void
  onDeleteConversation: (id: number) => void
  onSelectList: (list: SavedList) => void
  onSelectSearch: (search: SearchListItem) => void
  open: boolean
  onClose: () => void
}) {
  const logout = useLogout()
  const [showLists, setShowLists] = useState(false)
  const [showSearches, setShowSearches] = useState(false)
  const { data: lists = [] } = useQuery({ queryKey: ['lists'], queryFn: listsApi.list, enabled: showLists })
  const { data: searches = [] } = useQuery({
    queryKey: ['all-searches'],
    queryFn: searchesApi.listAll,
    enabled: showSearches,
  })

  return (
    <>
      {open && <div className="fixed inset-0 z-40 bg-black/40 md:hidden" onClick={onClose} />}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex h-full w-64 max-w-[85vw] shrink-0 flex-col bg-brand-dark transition-transform duration-200 ease-out',
          'md:static md:z-auto md:w-60 md:max-w-none md:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="relative flex items-center justify-center px-3 pb-3 pt-5">
          <img src={logoWhite} alt="Tecport" className="h-11 w-auto" />
          <div className="absolute right-2 top-3 flex items-center gap-1">
            <ThemeToggle />
            <button
              onClick={onClose}
              aria-label="Cerrar menú"
              className="rounded-md p-1.5 text-white/60 hover:bg-white/10 hover:text-white md:hidden"
            >
              <X className="size-4" />
            </button>
          </div>
        </div>

        <div className="p-2">
          <button
            onClick={() => {
              onNewConversation()
              onClose()
            }}
            className="flex w-full items-center gap-2 rounded-lg bg-brand-light px-3 py-2 text-left text-sm font-semibold text-white shadow-sm hover:bg-white/20"
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
            onSelect={(id) => {
              onSelectConversation(id)
              onClose()
            }}
            onRename={onRenameConversation}
            onDelete={onDeleteConversation}
          />

          <button
            onClick={() => setShowSearches((value) => !value)}
            className="mt-4 w-full px-2 pb-1 pt-2 text-left text-xs font-semibold uppercase tracking-wide text-white/40 hover:text-white/70"
          >
            Búsquedas {showSearches ? '▾' : '▸'}
          </button>
          {showSearches && (
            <ul className="space-y-0.5 px-0">
              {searches.length === 0 && <p className="px-2 text-xs text-white/40">Sin búsquedas todavía.</p>}
              {searches.map((search) => (
                <li key={search.id}>
                  <button
                    onClick={() => {
                      onSelectSearch(search)
                      onClose()
                    }}
                    className="flex w-full flex-col rounded-md px-2 py-1.5 text-left hover:bg-white/10"
                  >
                    <span className="truncate text-sm text-white/80">
                      {search.criteria_json.summary_es || search.original_query}
                    </span>
                    <span className="text-xs text-white/40">{search.result_count} resultado(s)</span>
                  </button>
                </li>
              ))}
            </ul>
          )}

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
                <li key={list.id}>
                  <button
                    onClick={() => {
                      onSelectList(list)
                      onClose()
                    }}
                    className="w-full truncate rounded-md px-2 py-1.5 text-left text-sm text-white/80 hover:bg-white/10"
                  >
                    {list.name}
                  </button>
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
    </>
  )
}
