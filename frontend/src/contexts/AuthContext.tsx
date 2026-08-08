import {
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react'

import {
  getCurrentUser,
  loginRequest,
} from '../api/auth'

import type {
  LoginRequest,
  User,
} from '../types/auth'

interface AuthContextData {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextData | undefined>(
  undefined,
)

export function AuthProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      setLoading(false)
      return
    }

    getCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('access_token')
        setUser(null)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  async function login(
    credentials: LoginRequest,
  ): Promise<void> {
    const tokenResponse = await loginRequest(
      credentials,
    )

    localStorage.setItem(
      'access_token',
      tokenResponse.access_token,
    )

    try {
      const authenticatedUser = await getCurrentUser()

      setUser(authenticatedUser)
    } catch (error) {
      localStorage.removeItem('access_token')
      throw error
    }
  }

  function logout(): void {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: Boolean(user),
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextData {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error(
      'useAuth must be used inside AuthProvider',
    )
  }

  return context
}
