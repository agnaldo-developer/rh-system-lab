import { api } from './client'

import type {
  AuditLog,
} from '../types/audit'


export interface AuditLogFilters {
  action?: string
  entity_type?: string
  user_id?: number
}


export async function listAuditLogs(
  filters: AuditLogFilters = {},
): Promise<AuditLog[]> {
  const params = new URLSearchParams()

  params.set('limit', '100')

  if (filters.action) {
    params.set(
      'action',
      filters.action,
    )
  }

  if (filters.entity_type) {
    params.set(
      'entity_type',
      filters.entity_type,
    )
  }

  if (filters.user_id) {
    params.set(
      'user_id',
      String(filters.user_id),
    )
  }

  const response = await api.get<AuditLog[]>(
    `/api/v1/audit-logs?${params.toString()}`,
  )

  return response.data
}
