import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'

import { useCurrentUser } from '@/features/auth/useAuth'
import { LoadingState } from '@/components/LoadingState'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { data: user, isLoading, isError } = useCurrentUser()

  if (isLoading) {
    return <LoadingState label="Verificando sesión…" />
  }

  if (isError || !user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
