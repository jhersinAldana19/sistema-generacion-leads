import { api } from '@/services/apiClient'
import type {
  InterpretResponse,
  Search,
  SearchCriteria,
  SearchResultsOut,
  SearchStatusOut,
} from '@/types/api'

export const searchesApi = {
  interpret: (conversationId: number, query: string, previousCriteria?: SearchCriteria) =>
    api.post<InterpretResponse>('/api/searches/interpret', {
      conversation_id: conversationId,
      query,
      previous_criteria: previousCriteria ?? null,
    }),

  create: (conversationId: number, originalQuery: string, criteria: SearchCriteria) =>
    api.post<Search>('/api/searches', {
      conversation_id: conversationId,
      original_query: originalQuery,
      criteria,
    }),

  get: (searchId: number) => api.get<Search>(`/api/searches/${searchId}`),

  getStatus: (searchId: number) => api.get<SearchStatusOut>(`/api/searches/${searchId}/status`),

  getResults: (searchId: number) => api.get<SearchResultsOut>(`/api/searches/${searchId}/results`),

  cancel: (searchId: number) => api.post<Search>(`/api/searches/${searchId}/cancel`),

  export: (searchId: number) => api.post<{ export_id: number; file_name: string }>(`/api/searches/${searchId}/export`),

  listForConversation: (conversationId: number) =>
    api.get<Search[]>(`/api/conversations/${conversationId}/searches`),
}

const TERMINAL_STATUSES = new Set(['completed', 'failed', 'cancelled'])

export function isTerminalStatus(status: string): boolean {
  return TERMINAL_STATUSES.has(status)
}
