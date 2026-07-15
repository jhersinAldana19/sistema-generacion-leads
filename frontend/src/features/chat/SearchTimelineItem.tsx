import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { ErrorState } from '@/components/ErrorState'
import type { Search, SearchResultItem, SearchStatusValue } from '@/types/api'
import { CriteriaCard } from '@/features/searches/CriteriaCard'
import { SearchProgressCard } from '@/features/searches/SearchProgressCard'
import { searchesApi } from '@/features/searches/searchesApi'
import { ExportButton } from '@/features/results/ExportButton'
import { InlineResultsTable } from '@/features/results/InlineResultsTable'

export function SearchTimelineItem({
  search,
  onSelectResult,
}: {
  search: Search
  onSelectResult: (result: SearchResultItem) => void
}) {
  const [status, setStatus] = useState<SearchStatusValue>(search.status)
  const isCompleted = status === 'completed'

  const { data: resultsData } = useQuery({
    queryKey: ['search-results', search.id],
    queryFn: () => searchesApi.getResults(search.id),
    enabled: isCompleted,
  })

  return (
    <div className="space-y-3">
      <CriteriaCard criteria={search.criteria_json} readOnly />

      {(status === 'pending' || status === 'running') && (
        <SearchProgressCard searchId={search.id} onStatusChange={setStatus} />
      )}

      {status === 'failed' && <ErrorState message={search.error_message ?? 'La búsqueda no pudo completarse.'} />}

      {status === 'cancelled' && (
        <p className="text-sm text-gray-500 dark:text-dark-text-muted">Búsqueda cancelada.</p>
      )}

      {isCompleted && resultsData && (
        <div className="space-y-2">
          <InlineResultsTable results={resultsData.results} onSelect={onSelectResult} />
          {resultsData.results.length > 0 && <ExportButton searchId={search.id} />}
        </div>
      )}
    </div>
  )
}
