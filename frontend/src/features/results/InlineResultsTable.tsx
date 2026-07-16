import { Users } from 'lucide-react'

import { EmptyState } from '@/components/EmptyState'
import { Avatar } from '@/components/ui/avatar'
import type { SearchResultItem } from '@/types/api'
import { StatusBadge } from '@/features/results/StatusBadge'

export function InlineResultsTable({
  results,
  onSelect,
}: {
  results: SearchResultItem[]
  onSelect: (result: SearchResultItem) => void
}) {
  if (results.length === 0) {
    return (
      <EmptyState
        title="No se encontraron candidatos que cumplan el criterio"
        description="Puedes ajustar los criterios (país, sector, cargo) o pedir que se incluyan más fuentes."
      />
    )
  }

  return (
    <div className="w-full overflow-hidden rounded-xl border border-gray-200 shadow-sm dark:border-dark-border">
      <div className="flex items-center gap-2 border-b border-gray-200 bg-white px-3 py-2.5 dark:border-dark-border dark:bg-dark-surface">
        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-brand/10 text-brand dark:bg-white/10 dark:text-dark-text">
          <Users className="size-3.5" />
        </span>
        <p className="text-sm font-semibold text-gray-800 dark:text-dark-text">
          {results.length} {results.length === 1 ? 'candidato encontrado' : 'candidatos encontrados'}
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-500 dark:bg-white/5 dark:text-dark-text-muted">
            <tr>
              <th className="px-3 py-2 font-medium">Persona</th>
              <th className="px-3 py-2 font-medium">Cargo</th>
              <th className="px-3 py-2 font-medium">Empresa</th>
              <th className="px-3 py-2 font-medium">País</th>
              <th className="px-3 py-2 font-medium">Correo</th>
              <th className="px-3 py-2 font-medium">Teléfono</th>
              <th className="px-3 py-2 font-medium">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-dark-border dark:bg-dark-surface">
            {results.map((result) => {
              const data = result.result_data_json
              return (
                <tr
                  key={result.id}
                  onClick={() => onSelect(result)}
                  className="cursor-pointer hover:bg-gray-50 dark:hover:bg-dark-surface-hover"
                >
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <Avatar name={data.full_name} variant="auto" className="h-7 w-7 text-[11px]" />
                      <span className="font-medium text-gray-900 dark:text-dark-text">{data.full_name}</span>
                    </div>
                  </td>
                  <td className="px-3 py-2 text-gray-600 dark:text-dark-text-muted">{data.job_title}</td>
                  <td className="px-3 py-2 text-gray-600 dark:text-dark-text-muted">{data.company_name}</td>
                  <td className="px-3 py-2 text-gray-600 dark:text-dark-text-muted">{data.country ?? '—'}</td>
                  <td className="px-3 py-2 text-gray-600 dark:text-dark-text-muted">
                    {data.direct_email ?? data.company_email ?? '—'}
                  </td>
                  <td className="px-3 py-2 text-gray-600 dark:text-dark-text-muted">
                    {data.direct_phone ?? data.company_phone ?? '—'}
                  </td>
                  <td className="px-3 py-2">
                    <StatusBadge status={result.status} />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
