export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'rh' | 'viewer'
  is_active: boolean
  created_at: string
  updated_at: string
}