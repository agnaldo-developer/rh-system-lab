import { Navigate } from 'react-router-dom'

import { useAuth } from '../contexts/AuthContext'


export function ProtectedRoute({
  children,
}: {
  children: React.ReactNode
}) {
  const {
    isAuthenticated,
    loading,
  } = useAuth()

  if (loading) {
    return <div>Carregando...</div>
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    )
  }

  return children
}
