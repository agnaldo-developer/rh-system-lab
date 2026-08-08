import { api } from './client'


export interface DashboardSummary {
  employees: number
  departments: number
  users: number
  auditLogs: number
}


export async function getDashboardSummary(): Promise<DashboardSummary> {
  const [
    employeesResponse,
    departmentsResponse,
    usersResponse,
    auditLogsResponse,
  ] = await Promise.all([
    api.get<unknown[]>(
      '/api/v1/employees?limit=100',
    ),
    api.get<unknown[]>(
      '/api/v1/departments?limit=100',
    ),
    api.get<unknown[]>(
      '/api/v1/users',
    ),
    api.get<unknown[]>(
      '/api/v1/audit-logs?limit=100',
    ),
  ])

  return {
    employees: employeesResponse.data.length,
    departments: departmentsResponse.data.length,
    users: usersResponse.data.length,
    auditLogs: auditLogsResponse.data.length,
  }
}
