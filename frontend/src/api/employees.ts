import { api } from './client'

import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
} from '../types/employee'


export async function listEmployees(): Promise<Employee[]> {
  const response = await api.get<Employee[]>(
    '/api/v1/employees?limit=100',
  )

  return response.data
}


export async function createEmployee(
  data: EmployeeCreate,
): Promise<Employee> {
  const response = await api.post<Employee>(
    '/api/v1/employees',
    data,
  )

  return response.data
}


export async function updateEmployee(
  id: number,
  data: EmployeeUpdate,
): Promise<Employee> {
  const response = await api.patch<Employee>(
    `/api/v1/employees/${id}`,
    data,
  )

  return response.data
}


export async function deleteEmployee(
  id: number,
): Promise<void> {
  await api.delete(
    `/api/v1/employees/${id}`,
  )
}
