const SUGGESTIONS = [
  'Busca jefes de operaciones de empresas portuarias en Perú',
  'Encuentra gerentes de mantenimiento de empresas mineras en Chile',
  'Busca responsables de logística de empresas industriales en Colombia',
  'Encuentra proveedores de repuestos hidráulicos en Chile',
]

export function ChatEmptyState({ onSelectSuggestion }: { onSelectSuggestion: (text: string) => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-4 text-center">
      <div>
        <h1 className="text-xl font-semibold text-gray-800 dark:text-dark-text">¿A quién quieres investigar hoy?</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-dark-text-muted">
          Describe el cargo, sector o país que buscas y te muestro contactos con fuente y evidencia.
        </p>
      </div>
      <div className="grid w-full max-w-lg gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSelectSuggestion(suggestion)}
            className="rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-left text-sm text-gray-600 shadow-sm hover:border-brand hover:text-brand dark:border-dark-border dark:bg-dark-surface dark:text-dark-text-muted dark:hover:border-dark-text-muted dark:hover:text-dark-text"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}
