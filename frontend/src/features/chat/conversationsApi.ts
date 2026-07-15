import { api } from '@/services/apiClient'
import type { Conversation, Message } from '@/types/api'

export const conversationsApi = {
  create: (title?: string) => api.post<Conversation>('/api/conversations', { title }),
  list: () => api.get<Conversation[]>('/api/conversations'),
  get: (id: number) => api.get<Conversation>(`/api/conversations/${id}`),
  rename: (id: number, title: string) => api.patch<Conversation>(`/api/conversations/${id}`, { title }),
  remove: (id: number) => api.delete<{ ok: boolean }>(`/api/conversations/${id}`),
  addMessage: (id: number, content: string) => api.post<Message>(`/api/conversations/${id}/messages`, { content }),
  listMessages: (id: number) => api.get<Message[]>(`/api/conversations/${id}/messages`),
}
