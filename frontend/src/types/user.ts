export type UserRole =
  | 'admin'
  | 'rh'
  | 'viewer'

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  name: string
  email: string
  password: string
  role: UserRole
  is_active: boolean
}

export interface UserUpdate {
  name?: string
  email?: string
  password?: string
  role?: UserRole
  is_active?: boolean
}
