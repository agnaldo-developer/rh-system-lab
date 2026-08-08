export interface Employee {
  id: number
  first_name: string
  last_name: string
  email: string
  phone: string | null
  document: string
  hire_date: string
  salary: number
  department_id: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EmployeeCreate {
  first_name: string
  last_name: string
  email: string
  phone?: string
  document: string
  hire_date: string
  salary: number
  department_id: number
  is_active: boolean
}

export interface EmployeeUpdate {
  first_name?: string
  last_name?: string
  email?: string
  phone?: string
  document?: string
  hire_date?: string
  salary?: number
  department_id?: number
  is_active?: boolean
}
