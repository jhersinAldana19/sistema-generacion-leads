import { useState, type KeyboardEvent } from 'react'
import { Send } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

export function ChatComposer({
  onSend,
  disabled = false,
}: {
  onSend: (message: string) => void
  disabled?: boolean
}) {
  const [value, setValue] = useState('')

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <div className="flex items-end gap-2 rounded-2xl border border-gray-300 bg-white p-2 shadow-sm focus-within:border-brand">
      <Textarea
        rows={1}
        placeholder="Escribe tu búsqueda, por ejemplo: Busca jefes de operaciones de empresas portuarias en Perú"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className="max-h-32 border-none shadow-none focus-visible:ring-0"
      />
      <Button size="icon" className="rounded-full" onClick={submit} disabled={disabled || !value.trim()} aria-label="Enviar">
        <Send className="size-4" />
      </Button>
    </div>
  )
}
