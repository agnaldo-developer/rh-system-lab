import { api } from './client'

import type {
  LoginRequest,
  TokenResponse,
  User,
} from '../types/auth'

export async function loginRequest(
  credentials: LoginRequest,
): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>(
    '/api/v1/auth/login',
    credentials,
  )

  return response.data
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>(
    '/api/v1/users/me',
  )

  return response.data
}
