import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SearchStatusValue } from '@/types/api'
import { isTerminalStatus, searchesApi } from '@/features/searches/searchesApi'

const STATUS_LABEL: Record<SearchStatusValue, string> = {
  pending: 'En cola',
  running: 'Buscando contactos…',
  completed: 'Búsqueda completa',
  failed: 'La búsqueda tuvo un error',
  cancelled: 'Búsqueda cancelada',
}

export function SearchProgressCard({
  searchId,
  onStatusChange,
}: {
  searchId: number
  onStatusChange?: (status: SearchStatusValue) => void
}) {
  const { data } = useQuery({
    queryKey: ['search-status', searchId],
    queryFn: () => searchesApi.getStatus(searchId),
    refetchInterval: (query) => (query.state.data && isTerminalStatus(query.state.data.status) ? false : 3000),
  })

  const lastNotified = useRef<string | null>(null)
  useEffect(() => {
    if (data?.status && data.status !== lastNotified.current) {
      lastNotified.current = data.status
      onStatusChange?.(data.status)
    }
  }, [data?.status, onStatusChange])

  if (!data) return null

  const running = data.status === 'pending' || data.status === 'running'
  const progress = data.progress

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {running && <Loader2 className="size-4 animate-spin text-brand dark:text-blue-300" />}
          {STATUS_LABEL[data.status]}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt className="text-xs text-gray-400 dark:text-dark-text-muted">Empresas revisadas</dt>
            <dd className="font-medium text-gray-800 dark:text-dark-text">{progress.companies_reviewed}</dd>
          </div>
          <div>
            <dt className="text-xs text-gray-400 dark:text-dark-text-muted">Páginas analizadas</dt>
            <dd className="font-medium text-gray-800 dark:text-dark-text">{progress.pages_analyzed}</dd>
          </div>
          <div>
            <dt className="text-xs text-gray-400 dark:text-dark-text-muted">Páginas no accesibles</dt>
            <dd className="font-medium text-gray-800 dark:text-dark-text">{progress.pages_inaccessible}</dd>
          </div>
          <div>
            <dt className="text-xs text-gray-400 dark:text-dark-text-muted">Candidatos encontrados</dt>
            <dd className="font-medium text-gray-800 dark:text-dark-text">{progress.results_found}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  )
}
