import { api } from '@/services/apiClient'
import type { SavedList, SavedListItem, SavedListItemDetail } from '@/types/api'

export const listsApi = {
  create: (name: string, description?: string) => api.post<SavedList>('/api/lists', { name, description }),
  list: () => api.get<SavedList[]>('/api/lists'),
  remove: (listId: number) => api.delete<{ ok: boolean }>(`/api/lists/${listId}`),
  addItem: (listId: number, searchResultId: number, notes?: string) =>
    api.post<SavedListItem>(`/api/lists/${listId}/items`, { search_result_id: searchResultId, notes }),
  getItems: (listId: number) => api.get<SavedListItemDetail[]>(`/api/lists/${listId}/items`),
  removeItem: (listId: number, itemId: number) => api.delete<{ ok: boolean }>(`/api/lists/${listId}/items/${itemId}`),
}
