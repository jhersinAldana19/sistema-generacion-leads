import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, Trash2 } from 'lucide-react'

import { Avatar } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/EmptyState'
import { LoadingState } from '@/components/LoadingState'
import { Sheet, SheetBody, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { downloadUrl } from '@/services/apiClient'
import type { SavedList, SavedListItemDetail, SearchResultItem } from '@/types/api'
import { StatusBadge } from '@/features/results/StatusBadge'
import { listsApi } from '@/features/lists/listsApi'

function toSearchResultItem(item: SavedListItemDetail): SearchResultItem {
  return {
    id: item.search_result_id,
    search_id: 0,
    result_data_json: item.result_data_json,
    match_score: null,
    status: item.result_status,
    review_status: 'pending',
    created_at: item.created_at,
    reviewed_at: null,
  }
}

export function SavedListDrawer({
  list,
  onClose,
  onSelectResult,
}: {
  list: SavedList | null
  onClose: () => void
  onSelectResult: (result: SearchResultItem) => void
}) {
  const queryClient = useQueryClient()

  const { data: items, isLoading } = useQuery({
    queryKey: ['list-items', list?.id],
    queryFn: () => listsApi.getItems(list!.id),
    enabled: list !== null,
  })

  if (!list) return null

  const handleRemove = async (itemId: number) => {
    await listsApi.removeItem(list.id, itemId)
    queryClient.invalidateQueries({ queryKey: ['list-items', list.id] })
  }

  return (
    <Sheet open={Boolean(list)} onOpenChange={(open) => !open && onClose()}>
      <SheetHeader>
        <SheetTitle>{list.name}</SheetTitle>
        {list.description && (
          <p className="mt-1 text-sm text-gray-500 dark:text-dark-text-muted">{list.description}</p>
        )}
        {items && items.length > 0 && (
          <Button
            size="sm"
            variant="outline"
            className="mt-2 w-fit"
            onClick={() => window.open(downloadUrl(`/api/lists/${list.id}/export`), '_blank')}
          >
            <Download className="size-4" />
            Exportar Excel
          </Button>
        )}
      </SheetHeader>

      <SheetBody>
        {isLoading && <LoadingState label="Cargando lista…" />}

        {items && items.length === 0 && (
          <EmptyState title="Esta lista está vacía" description="Agrega resultados desde el panel de detalle." />
        )}

        {items && items.length > 0 && (
          <ul className="space-y-2">
            {items.map((item) => {
              const data = item.result_data_json
              return (
                <li key={item.id}>
                  <button
                    onClick={() => {
                      onSelectResult(toSearchResultItem(item))
                      onClose()
                    }}
                    className="flex w-full items-center gap-3 rounded-lg border border-gray-200 p-3 text-left hover:border-brand dark:border-dark-border dark:hover:border-dark-text-muted"
                  >
                    <Avatar name={data.full_name} variant="auto" className="h-9 w-9 shrink-0 text-xs" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-900 dark:text-dark-text">
                        {data.full_name}
                      </p>
                      <p className="truncate text-xs text-gray-500 dark:text-dark-text-muted">
                        {data.job_title} · {data.company_name}
                      </p>
                      <p className="truncate text-xs text-gray-500 dark:text-dark-text-muted">
                        {data.direct_email ?? data.company_email ?? 'Sin correo'}
                        {' · '}
                        {data.direct_phone ?? data.company_phone ?? 'Sin teléfono'}
                      </p>
                    </div>
                    <StatusBadge status={item.result_status} />
                    <span
                      role="button"
                      tabIndex={0}
                      onClick={(event) => {
                        event.stopPropagation()
                        handleRemove(item.id)
                      }}
                      aria-label="Quitar de la lista"
                      className="rounded p-1.5 text-gray-400 hover:bg-red-100 hover:text-status-discarded dark:text-dark-text-muted dark:hover:bg-status-discarded/20"
                    >
                      <Trash2 className="size-3.5" />
                    </span>
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </SheetBody>
    </Sheet>
  )
}
