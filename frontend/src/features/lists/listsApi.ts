import { api } from '@/services/apiClient'
import type { SavedList, SavedListItem } from '@/types/api'

export const listsApi = {
  create: (name: string, description?: string) => api.post<SavedList>('/api/lists', { name, description }),
  list: () => api.get<SavedList[]>('/api/lists'),
  addItem: (listId: number, searchResultId: number, notes?: string) =>
    api.post<SavedListItem>(`/api/lists/${listId}/items`, { search_result_id: searchResultId, notes }),
  removeItem: (listId: number, itemId: number) => api.delete<{ ok: boolean }>(`/api/lists/${listId}/items/${itemId}`),
}
