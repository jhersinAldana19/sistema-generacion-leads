import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { listsApi } from '@/features/lists/listsApi'

export function SavedListSelector({ searchResultId }: { searchResultId: number }) {
  const queryClient = useQueryClient()
  const [selectedListId, setSelectedListId] = useState<string>('')
  const [newListName, setNewListName] = useState('')
  const [feedback, setFeedback] = useState<string | null>(null)

  const { data: lists = [] } = useQuery({ queryKey: ['lists'], queryFn: listsApi.list })

  const createList = useMutation({
    mutationFn: (name: string) => listsApi.create(name),
    onSuccess: (list) => {
      queryClient.invalidateQueries({ queryKey: ['lists'] })
      setSelectedListId(String(list.id))
      setNewListName('')
    },
  })

  const addItem = useMutation({
    mutationFn: (listId: number) => listsApi.addItem(listId, searchResultId),
    onSuccess: () => setFeedback('Agregado a la lista.'),
  })

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-dark-text-muted">
        Agregar a lista
      </p>
      <div className="flex gap-2">
        <select
          className="h-9 flex-1 rounded-md border border-gray-300 bg-white px-2 text-sm dark:border-dark-border dark:bg-dark-surface dark:text-dark-text"
          value={selectedListId}
          onChange={(event) => setSelectedListId(event.target.value)}
        >
          <option value="">Selecciona una lista…</option>
          {lists.map((list) => (
            <option key={list.id} value={list.id}>
              {list.name}
            </option>
          ))}
        </select>
        <Button
          size="sm"
          variant="outline"
          disabled={!selectedListId || addItem.isPending}
          onClick={() => selectedListId && addItem.mutate(Number(selectedListId))}
        >
          Agregar
        </Button>
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="Nueva lista…"
          value={newListName}
          onChange={(event) => setNewListName(event.target.value)}
        />
        <Button
          size="sm"
          variant="ghost"
          disabled={!newListName.trim() || createList.isPending}
          onClick={() => createList.mutate(newListName.trim())}
        >
          Crear
        </Button>
      </div>

      {feedback && <p className="text-xs text-status-confirmed">{feedback}</p>}
    </div>
  )
}
