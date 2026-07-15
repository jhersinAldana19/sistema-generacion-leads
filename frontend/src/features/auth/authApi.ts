import { api } from '@/services/apiClient'
import type { User } from '@/types/api'

export interface LoginPayload {
  email: string
  password: string
  remember_me: boolean
}

export const authApi = {
  login: (payload: LoginPayload) => api.post<User>('/api/auth/login', payload),
  logout: () => api.post<{ ok: boolean }>('/api/auth/logout'),
  me: () => api.get<User>('/api/auth/me'),
}
