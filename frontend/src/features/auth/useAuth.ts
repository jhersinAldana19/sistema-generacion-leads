import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { ApiError } from '@/services/apiClient'
import { authApi, type LoginPayload } from '@/features/auth/authApi'

const ME_QUERY_KEY = ['auth', 'me']

export function useCurrentUser() {
  return useQuery({
    queryKey: ME_QUERY_KEY,
    queryFn: authApi.me,
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: LoginPayload) => authApi.login(payload),
    onSuccess: (user) => {
      queryClient.setQueryData(ME_QUERY_KEY, user)
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.setQueryData(ME_QUERY_KEY, null)
      queryClient.clear()
    },
  })
}

export function isUnauthorized(error: unknown): boolean {
  return error instanceof ApiError && error.status === 401
}
