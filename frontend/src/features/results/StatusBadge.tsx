import { Badge, type BadgeProps } from '@/components/ui/badge'
import type { ResultStatus } from '@/types/api'

const STATUS_CONFIG: Record<ResultStatus, { label: string; variant: BadgeProps['variant'] }> = {
  candidate: { label: 'Candidato', variant: 'candidate' },
  probable: { label: 'Probable', variant: 'probable' },
  confirmed: { label: 'Confirmado', variant: 'confirmed' },
  outdated: { label: 'Fuente antigua', variant: 'outdated' },
  needs_review: { label: 'Requiere revisión', variant: 'review' },
  discarded: { label: 'Descartado', variant: 'discarded' },
}

export function StatusBadge({ status }: { status: ResultStatus }) {
  const config = STATUS_CONFIG[status]
  return <Badge variant={config.variant}>{config.label}</Badge>
}
