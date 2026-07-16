import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ExternalLink } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Sheet, SheetBody, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import type { SearchResultItem } from '@/types/api'
import { SavedListSelector } from '@/features/lists/SavedListSelector'
import { ContactMethodBadge } from '@/features/results/ContactMethodBadge'
import { EvidenceCard } from '@/features/results/EvidenceCard'
import { resultsApi } from '@/features/results/resultsApi'
import { StatusBadge } from '@/features/results/StatusBadge'

const MISSING_FIELD_LABEL: Record<string, string> = {
  direct_email: 'Correo directo',
  direct_phone: 'Teléfono directo',
  linkedin_url: 'LinkedIn',
  city: 'Ciudad',
  source_date: 'Fecha de la fuente',
}

export function ResultDetailDrawer({
  result,
  onClose,
  onUpdated,
}: {
  result: SearchResultItem | null
  onClose: () => void
  onUpdated: (updated: SearchResultItem) => void
}) {
  const queryClient = useQueryClient()

  const invalidateResults = (searchId: number) => {
    queryClient.invalidateQueries({ queryKey: ['search-results', searchId] })
  }

  const confirmMutation = useMutation({
    mutationFn: () => resultsApi.confirm(result!.id),
    onSuccess: (updated) => {
      onUpdated(updated)
      invalidateResults(updated.search_id)
    },
  })
  const discardMutation = useMutation({
    mutationFn: () => resultsApi.discard(result!.id),
    onSuccess: (updated) => {
      onUpdated(updated)
      invalidateResults(updated.search_id)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: () => resultsApi.flagForReview(result!.id),
    onSuccess: (updated) => {
      onUpdated(updated)
      invalidateResults(updated.search_id)
    },
  })

  if (!result) return null
  const data = result.result_data_json

  return (
    <Sheet open={Boolean(result)} onOpenChange={(open) => !open && onClose()}>
      <SheetHeader>
        <SheetTitle>{data.full_name}</SheetTitle>
        <div className="mt-1 flex items-center gap-2">
          <StatusBadge status={result.status} />
          <span className="text-sm text-gray-500 dark:text-dark-text-muted">{data.job_title}</span>
        </div>
      </SheetHeader>

      <SheetBody>
        <section className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">Empresa</p>
            <p className="text-gray-800 dark:text-dark-text">{data.company_name}</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">Sector</p>
            <p className="text-gray-800 dark:text-dark-text">{data.industry ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">País</p>
            <p className="text-gray-800 dark:text-dark-text">{data.country ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">Ciudad</p>
            <p className="text-gray-800 dark:text-dark-text">{data.city ?? '—'}</p>
          </div>
        </section>

        <section className="space-y-3 border-t border-gray-100 pt-3 dark:border-dark-border">
          <ContactMethodBadge label="Correo directo" value={data.direct_email} type={data.direct_email_type} />
          <ContactMethodBadge label="Correo corporativo" value={data.company_email} />
          <ContactMethodBadge label="Teléfono directo" value={data.direct_phone} type={data.direct_phone_type} />
          <ContactMethodBadge label="Teléfono de empresa" value={data.company_phone} />
          <ContactMethodBadge label="LinkedIn" value={data.linkedin_url} />
          {data.company_website && (
            <a
              href={data.company_website}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 text-sm font-medium text-brand hover:underline dark:text-blue-300"
            >
              Sitio web de la empresa <ExternalLink className="size-3" />
            </a>
          )}
        </section>

        <section className="border-t border-gray-100 pt-3 dark:border-dark-border">
          <EvidenceCard evidenceText={data.evidence_text} sourceUrl={data.source_url} sourceDate={data.source_date} />
        </section>

        {data.missing_fields.length > 0 && (
          <section className="border-t border-gray-100 pt-3 dark:border-dark-border">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">Campos faltantes</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-dark-text-muted">
              {data.missing_fields.map((field) => MISSING_FIELD_LABEL[field] ?? field).join(', ')}
            </p>
          </section>
        )}

        <section className="border-t border-gray-100 pt-3 dark:border-dark-border">
          <SavedListSelector searchResultId={result.id} />
        </section>

        <section className="flex flex-wrap gap-2 border-t border-gray-100 pt-3 dark:border-dark-border">
          <Button size="sm" onClick={() => confirmMutation.mutate()} disabled={confirmMutation.isPending}>
            Confirmar
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => reviewMutation.mutate()}
            disabled={reviewMutation.isPending}
          >
            Marcar para revisión
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => discardMutation.mutate()}
            disabled={discardMutation.isPending}
          >
            Descartar
          </Button>
        </section>
      </SheetBody>
    </Sheet>
  )
}
