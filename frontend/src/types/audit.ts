export interface AuditLog {
  id: number
  user_id: number | null
  action: string
  entity_type: string
  entity_id: number | null
  request_id: string | null
  details: Record<string, unknown> | null
  created_at: string
}
