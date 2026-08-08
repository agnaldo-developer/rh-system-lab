import {
  Navigate,
} from 'react-router-dom'

import {
  useAuth,
} from '../contexts/AuthContext'

import type {
  UserRole,
} from '../types/user'


interface RoleRouteProps {
  children: React.ReactNode
  allowedRoles: UserRole[]
}


export function RoleRoute({
  children,
  allowedRoles,
}: RoleRouteProps) {
  const {
    user,
    loading,
  } = useAuth()

  if (loading) {
    return <div>Carregando...</div>
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    )
  }

  if (
    !allowedRoles.includes(
      user.role,
    )
  ) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  return children
}
