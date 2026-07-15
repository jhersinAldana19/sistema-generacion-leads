import { useMutation } from '@tanstack/react-query'
import { Download } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { downloadUrl } from '@/services/apiClient'
import { searchesApi } from '@/features/searches/searchesApi'

export function ExportButton({ searchId }: { searchId: number }) {
  const exportMutation = useMutation({
    mutationFn: () => searchesApi.export(searchId),
    onSuccess: (data) => {
      window.open(downloadUrl(`/api/exports/${data.export_id}/download`), '_blank')
    },
  })

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => exportMutation.mutate()}
      disabled={exportMutation.isPending}
    >
      <Download className="size-4" />
      {exportMutation.isPending ? 'Exportando…' : 'Exportar Excel'}
    </Button>
  )
}
