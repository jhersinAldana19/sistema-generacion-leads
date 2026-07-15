import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { LoadingState } from '@/components/LoadingState'
import { cn } from '@/lib/utils'
import { useCurrentUser } from '@/features/auth/useAuth'
import { AppSidebar } from '@/features/chat/AppSidebar'
import { ChatComposer } from '@/features/chat/ChatComposer'
import { ChatEmptyState } from '@/features/chat/ChatEmptyState'
import { ChatMessage } from '@/features/chat/ChatMessage'
import { conversationsApi } from '@/features/chat/conversationsApi'
import { SearchTimelineItem } from '@/features/chat/SearchTimelineItem'
import { CriteriaCard } from '@/features/searches/CriteriaCard'
import { searchesApi } from '@/features/searches/searchesApi'
import { ResultDetailDrawer } from '@/features/results/ResultDetailDrawer'
import type { Search, SearchCriteria, SearchResultItem } from '@/types/api'

interface DraftCriteria {
  query: string
  criteria: SearchCriteria
  changeSummary: string | null
}

export function ChatPage() {
  const { data: user } = useCurrentUser()
  const queryClient = useQueryClient()

  const [activeConversationId, setActiveConversationId] = useState<number | null>(null)
  const [draft, setDraft] = useState<DraftCriteria | null>(null)
  const [selectedResult, setSelectedResult] = useState<SearchResultItem | null>(null)

  const { data: conversations = [] } = useQuery({
    queryKey: ['conversations'],
    queryFn: conversationsApi.list,
  })

  useEffect(() => {
    if (activeConversationId === null && conversations.length > 0) {
      setActiveConversationId(conversations[0].id)
    }
  }, [activeConversationId, conversations])

  const { data: messages = [] } = useQuery({
    queryKey: ['messages', activeConversationId],
    queryFn: () => conversationsApi.listMessages(activeConversationId!),
    enabled: activeConversationId !== null,
  })

  const { data: searches = [] } = useQuery({
    queryKey: ['conversation-searches', activeConversationId],
    queryFn: () => searchesApi.listForConversation(activeConversationId!),
    enabled: activeConversationId !== null,
  })

  const createConversation = useMutation({
    mutationFn: () => conversationsApi.create(),
    onSuccess: (conversation) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      setActiveConversationId(conversation.id)
      setDraft(null)
    },
  })

  const renameConversation = useMutation({
    mutationFn: ({ id, title }: { id: number; title: string }) => conversationsApi.rename(id, title),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['conversations'] }),
  })

  const deleteConversation = useMutation({
    mutationFn: (id: number) => conversationsApi.remove(id),
    onSuccess: (_data, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      if (activeConversationId === deletedId) {
        setActiveConversationId(null)
        setDraft(null)
      }
    },
  })

  const sendMessage = useMutation({
    mutationFn: async (text: string) => {
      const conversationId = activeConversationId!
      await conversationsApi.addMessage(conversationId, text)
      return searchesApi.interpret(conversationId, text, draft?.criteria)
    },
    onSuccess: (interpretation, text) => {
      queryClient.invalidateQueries({ queryKey: ['messages', activeConversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      setDraft({ query: text, criteria: interpretation.criteria, changeSummary: interpretation.change_summary_es })
    },
  })

  const createSearch = useMutation({
    mutationFn: (criteria: SearchCriteria) => {
      const conversationId = activeConversationId!
      return searchesApi.create(conversationId, draft!.query, criteria)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation-searches', activeConversationId] })
      setDraft(null)
    },
  })

  const timelineItems = useMemo(() => {
    type TimelineEntry =
      | { kind: 'message'; timestamp: string; message: (typeof messages)[number] }
      | { kind: 'search'; timestamp: string; search: Search }

    const items: TimelineEntry[] = [
      ...messages.map((message) => ({ kind: 'message' as const, timestamp: message.created_at, message })),
      ...searches.map((search) => ({ kind: 'search' as const, timestamp: search.created_at, search })),
    ]
    return items.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }, [messages, searches])

  const isEmptyConversation = timelineItems.length === 0 && !draft

  if (!user) {
    return <LoadingState />
  }

  return (
    <div className="flex h-svh bg-white dark:bg-dark-bg">
      <AppSidebar
        user={user}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => {
          setActiveConversationId(id)
          setDraft(null)
        }}
        onNewConversation={() => createConversation.mutate()}
        onRenameConversation={(id, title) => renameConversation.mutate({ id, title })}
        onDeleteConversation={(id) => deleteConversation.mutate(id)}
      />

      <main className="flex flex-1 flex-col overflow-hidden">
        {activeConversationId === null ? (
          <ChatEmptyState
            onSelectSuggestion={(text) => {
              createConversation.mutate(undefined, {
                onSuccess: (conversation) => {
                  setActiveConversationId(conversation.id)
                  conversationsApi.addMessage(conversation.id, text).then(() => {
                    queryClient.invalidateQueries({ queryKey: ['messages', conversation.id] })
                    queryClient.invalidateQueries({ queryKey: ['conversations'] })
                  })
                  searchesApi.interpret(conversation.id, text).then((interpretation) => {
                    setDraft({
                      query: text,
                      criteria: interpretation.criteria,
                      changeSummary: interpretation.change_summary_es,
                    })
                  })
                },
              })
            }}
          />
        ) : (
          <>
            <div className={cn('flex-1 overflow-y-auto', isEmptyConversation && 'flex flex-col')}>
              {isEmptyConversation ? (
                <ChatEmptyState onSelectSuggestion={(text) => sendMessage.mutate(text)} />
              ) : (
                <div className="mx-auto w-full max-w-3xl space-y-4 px-4 py-6">
                  {timelineItems.map((item) =>
                    item.kind === 'message' ? (
                      <ChatMessage
                        key={`msg-${item.message.id}`}
                        role={item.message.role}
                        content={item.message.content}
                      />
                    ) : (
                      <SearchTimelineItem
                        key={`search-${item.search.id}`}
                        search={item.search}
                        onSelectResult={setSelectedResult}
                      />
                    ),
                  )}

                  {draft && (
                    <CriteriaCard
                      criteria={draft.criteria}
                      changeSummary={draft.changeSummary}
                      isConfirming={createSearch.isPending}
                      onConfirm={(criteria) => createSearch.mutate(criteria)}
                    />
                  )}
                </div>
              )}
            </div>

            <div className="border-t border-gray-100 bg-white px-4 py-3 dark:border-dark-border dark:bg-dark-bg">
              <div className="mx-auto w-full max-w-3xl">
                <ChatComposer onSend={(text) => sendMessage.mutate(text)} disabled={sendMessage.isPending} />
              </div>
            </div>
          </>
        )}
      </main>

      <ResultDetailDrawer
        result={selectedResult}
        onClose={() => setSelectedResult(null)}
        onUpdated={setSelectedResult}
      />
    </div>
  )
}
