import { api } from '@/services/apiClient'
import type { SearchResultItem } from '@/types/api'

export const resultsApi = {
  confirm: (id: number, notes?: string) => api.patch<SearchResultItem>(`/api/results/${id}/confirm`, { notes }),
  discard: (id: number, notes?: string) => api.patch<SearchResultItem>(`/api/results/${id}/discard`, { notes }),
  flagForReview: (id: number, notes?: string) => api.patch<SearchResultItem>(`/api/results/${id}/review`, { notes }),
}
