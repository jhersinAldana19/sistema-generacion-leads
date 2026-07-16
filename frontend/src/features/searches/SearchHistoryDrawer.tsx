import { Sheet, SheetBody, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import type { Search, SearchResultItem } from '@/types/api'
import { SearchTimelineItem } from '@/features/chat/SearchTimelineItem'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('es-PE', { day: 'numeric', month: 'long', year: 'numeric' })
}

export function SearchHistoryDrawer({
  search,
  onClose,
  onSelectResult,
}: {
  search: Search | null
  onClose: () => void
  onSelectResult: (result: SearchResultItem) => void
}) {
  if (!search) return null

  return (
    <Sheet open={Boolean(search)} onOpenChange={(open) => !open && onClose()}>
      <SheetHeader>
        <SheetTitle>Búsqueda del {formatDate(search.created_at)}</SheetTitle>
        <p className="mt-1 truncate text-sm text-gray-500 dark:text-dark-text-muted">{search.original_query}</p>
      </SheetHeader>

      <SheetBody>
        <SearchTimelineItem
          search={search}
          onSelectResult={(result) => {
            onSelectResult(result)
            onClose()
          }}
        />
      </SheetBody>
    </Sheet>
  )
}
