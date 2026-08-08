import { api } from './client'

import type {
  User,
  UserCreate,
  UserUpdate,
} from '../types/user'


export async function listUsers(): Promise<User[]> {
  const response = await api.get<User[]>(
    '/api/v1/users',
  )

  return response.data
}


export async function createUser(
  data: UserCreate,
): Promise<User> {
  const response = await api.post<User>(
    '/api/v1/users',
    data,
  )

  return response.data
}


export async function updateUser(
  id: number,
  data: UserUpdate,
): Promise<User> {
  const response = await api.patch<User>(
    `/api/v1/users/${id}`,
    data,
  )

  return response.data
}


export async function deactivateUser(
  id: number,
): Promise<User> {
  const response = await api.delete<User>(
    `/api/v1/users/${id}`,
  )

  return response.data
}
