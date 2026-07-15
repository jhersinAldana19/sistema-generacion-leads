export function ContactMethodBadge({
  label,
  value,
  type,
}: {
  label: string
  value: string | null
  type?: string | null
}) {
  const isInferred = type === 'inferred'

  return (
    <div className="flex flex-col gap-0.5">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-dark-text-muted">{label}</p>
      {value ? (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-800 dark:text-dark-text">{value}</span>
          {isInferred && (
            <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[11px] font-medium text-status-review dark:bg-status-review/20 dark:text-orange-300">
              Inferido — no verificado
            </span>
          )}
        </div>
      ) : (
        <span className="text-sm text-gray-400 dark:text-dark-text-muted">No encontrado</span>
      )}
    </div>
  )
}
