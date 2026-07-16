import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { listsApi } from '@/features/lists/listsApi'

export function SavedListSelector({ searchResultId }: { searchResultId: number }) {
  const queryClient = useQueryClient()
  const [selectedListId, setSelectedListId] = useState<string>('')
  const [newListName, setNewListName] = useState('')
  const [feedback, setFeedback] = useState<string | null>(null)

  const { data: lists = [] } = useQuery({ queryKey: ['lists'], queryFn: listsApi.list })

  const addItem = useMutation({
    mutationFn: (listId: number) => listsApi.addItem(listId, searchResultId),
  })

  const createAndAddList = useMutation({
    mutationFn: async (name: string) => {
      const list = await listsApi.create(name)
      await listsApi.addItem(list.id, searchResultId)
      return list
    },
    onSuccess: (list) => {
      queryClient.invalidateQueries({ queryKey: ['lists'] })
      setSelectedListId(String(list.id))
      setNewListName('')
      setFeedback(`Creada "${list.name}" y agregado a ella.`)
    },
  })

  const handleAddToExisting = () => {
    if (!selectedListId) return
    const list = lists.find((l) => String(l.id) === selectedListId)
    addItem.mutate(Number(selectedListId), {
      onSuccess: () => setFeedback(`Agregado a "${list?.name ?? 'la lista'}".`),
    })
  }

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">
        Agregar a lista
      </p>
      {lists.length === 0 ? (
        <p className="text-xs text-gray-500 dark:text-dark-text-muted">
          Aún no tienes listas guardadas — crea la primera abajo.
        </p>
      ) : (
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
          <Button size="sm" variant="outline" disabled={!selectedListId || addItem.isPending} onClick={handleAddToExisting}>
            Agregar
          </Button>
        </div>
      )}

      <div className="flex gap-2">
        <Input
          placeholder="Nueva lista…"
          value={newListName}
          onChange={(event) => setNewListName(event.target.value)}
        />
        <Button
          size="sm"
          variant="ghost"
          disabled={!newListName.trim() || createAndAddList.isPending}
          onClick={() => createAndAddList.mutate(newListName.trim())}
        >
          Crear y agregar
        </Button>
      </div>

      {feedback && (
        <p className="flex items-center gap-1 text-xs font-medium text-status-confirmed">
          <Check className="size-3.5" /> {feedback}
        </p>
      )}
    </div>
  )
}
