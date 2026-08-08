import { api } from './client'

import type {
  Department,
  DepartmentCreate,
  DepartmentUpdate,
} from '../types/department'


export async function listDepartments(): Promise<Department[]> {
  const response = await api.get<Department[]>(
    '/api/v1/departments?limit=100',
  )

  return response.data
}


export async function createDepartment(
  data: DepartmentCreate,
): Promise<Department> {
  const response = await api.post<Department>(
    '/api/v1/departments',
    data,
  )

  return response.data
}


export async function updateDepartment(
  id: number,
  data: DepartmentUpdate,
): Promise<Department> {
  const response = await api.patch<Department>(
    `/api/v1/departments/${id}`,
    data,
  )

  return response.data
}


export async function deleteDepartment(
  id: number,
): Promise<void> {
  await api.delete(
    `/api/v1/departments/${id}`,
  )
}
