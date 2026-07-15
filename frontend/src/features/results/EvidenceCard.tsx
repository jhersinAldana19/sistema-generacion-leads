import { ExternalLink } from 'lucide-react'

export function EvidenceCard({
  evidenceText,
  sourceUrl,
  sourceDate,
}: {
  evidenceText: string
  sourceUrl: string
  sourceDate: string | null
}) {
  return (
    <div className="space-y-2 rounded-md border border-gray-100 bg-gray-50 p-3 dark:border-dark-border dark:bg-white/5">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-dark-text-muted">Evidencia</p>
      <blockquote className="border-l-2 border-gray-300 pl-3 text-sm italic text-gray-700 dark:border-dark-border dark:text-dark-text">
        “{evidenceText}”
      </blockquote>
      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-dark-text-muted">
        <span>{sourceDate ? `Fuente del ${sourceDate}` : 'Fecha de la fuente: pendiente de verificación'}</span>
        <a
          href={sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 font-medium text-brand hover:underline dark:text-blue-300"
        >
          Abrir fuente <ExternalLink className="size-3" />
        </a>
      </div>
    </div>
  )
}
