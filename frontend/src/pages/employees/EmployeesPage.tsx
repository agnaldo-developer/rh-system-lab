import {
  useEffect,
  useState,
} from 'react'

import {
  Alert,
  Box,
  Button,
  Checkbox,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'

import {
  Add,
  Delete,
  Edit,
} from '@mui/icons-material'

import {
  createEmployee,
  deleteEmployee,
  listEmployees,
  updateEmployee,
} from '../../api/employees'

import {
  listDepartments,
} from '../../api/departments'

import { useAuth } from '../../contexts/AuthContext'

import type {
  Employee,
} from '../../types/employee'

import type {
  Department,
} from '../../types/department'


export function EmployeesPage() {
  const { user } = useAuth()

  const canManage =
    user?.role === 'admin'
    || user?.role === 'rh'

  const [
    employees,
    setEmployees,
  ] = useState<Employee[]>([])

  const [
    departments,
    setDepartments,
  ] = useState<Department[]>([])

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState('')

  const [
    dialogOpen,
    setDialogOpen,
  ] = useState(false)

  const [
    editingEmployee,
    setEditingEmployee,
  ] = useState<Employee | null>(null)

  const [firstName, setFirstName] =
    useState('')

  const [lastName, setLastName] =
    useState('')

  const [email, setEmail] =
    useState('')

  const [phone, setPhone] =
    useState('')

  const [document, setDocument] =
    useState('')

  const [hireDate, setHireDate] =
    useState('')

  const [salary, setSalary] =
    useState('')

  const [
    departmentId,
    setDepartmentId,
  ] = useState('')

  const [
    isActive,
    setIsActive,
  ] = useState(true)


  async function loadData() {
    setLoading(true)
    setError('')

    try {
      const [
        employeeData,
        departmentData,
      ] = await Promise.all([
        listEmployees(),
        listDepartments(),
      ])

      setEmployees(employeeData)
      setDepartments(departmentData)
    } catch {
      setError(
        'Não foi possível carregar os funcionários.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadData()
  }, [])


  function resetForm() {
    setFirstName('')
    setLastName('')
    setEmail('')
    setPhone('')
    setDocument('')
    setHireDate('')
    setSalary('')
    setDepartmentId('')
    setIsActive(true)
  }


  function openCreateDialog() {
    setEditingEmployee(null)
    resetForm()
    setDialogOpen(true)
  }


  function openEditDialog(
    employee: Employee,
  ) {
    setEditingEmployee(employee)

    setFirstName(employee.first_name)
    setLastName(employee.last_name)
    setEmail(employee.email)
    setPhone(employee.phone ?? '')
    setDocument(employee.document)
    setHireDate(employee.hire_date)
    setSalary(String(employee.salary))
    setDepartmentId(
      String(employee.department_id),
    )
    setIsActive(employee.is_active)

    setDialogOpen(true)
  }


  async function handleSave() {
    try {
      const payload = {
        first_name: firstName,
        last_name: lastName,
        email,
        phone: phone || undefined,
        document,
        hire_date: hireDate,
        salary: Number(salary),
        department_id:
          Number(departmentId),
        is_active: isActive,
      }

      if (editingEmployee) {
        await updateEmployee(
          editingEmployee.id,
          payload,
        )
      } else {
        await createEmployee(payload)
      }

      setDialogOpen(false)
      await loadData()
    } catch {
      setError(
        'Não foi possível salvar o funcionário.',
      )
    }
  }


  async function handleDelete(
    employee: Employee,
  ) {
    const confirmed = window.confirm(
      `Deseja excluir ${employee.first_name} ${employee.last_name}?`,
    )

    if (!confirmed) {
      return
    }

    try {
      await deleteEmployee(
        employee.id,
      )

      await loadData()
    } catch {
      setError(
        'Não foi possível excluir o funcionário.',
      )
    }
  }


  function getDepartmentName(
    departmentIdValue: number,
  ) {
    return (
      departments.find(
        (department) =>
          department.id
          === departmentIdValue,
      )?.name ?? '-'
    )
  }


  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Box>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
            }}
          >
            Funcionários
          </Typography>

          <Typography color="text.secondary">
            Gerencie os funcionários da empresa.
          </Typography>
        </Box>

        {canManage && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={openCreateDialog}
          >
            Novo funcionário
          </Button>
        )}
      </Box>

      {error && (
        <Alert
          severity="error"
          sx={{
            mb: 3,
          }}
        >
          {error}
        </Alert>
      )}

      {loading ? (
        <Box
          sx={{
            minHeight: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer
          component={Paper}
          elevation={0}
          sx={{
            border:
              '1px solid #e5e7eb',
            borderRadius: 3,
          }}
        >
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nome</TableCell>
                <TableCell>E-mail</TableCell>
                <TableCell>
                  Departamento
                </TableCell>
                <TableCell>Admissão</TableCell>
                <TableCell>Salário</TableCell>
                <TableCell>Status</TableCell>

                {canManage && (
                  <TableCell align="right">
                    Ações
                  </TableCell>
                )}
              </TableRow>
            </TableHead>

            <TableBody>
              {employees.map(
                (employee) => (
                  <TableRow
                    key={employee.id}
                    hover
                  >
                    <TableCell>
                      {employee.first_name}{' '}
                      {employee.last_name}
                    </TableCell>

                    <TableCell>
                      {employee.email}
                    </TableCell>

                    <TableCell>
                      {getDepartmentName(
                        employee.department_id,
                      )}
                    </TableCell>

                    <TableCell>
                      {employee.hire_date}
                    </TableCell>

                    <TableCell>
                      R${' '}
                      {Number(
                        employee.salary,
                      ).toLocaleString(
                        'pt-BR',
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        },
                      )}
                    </TableCell>

                    <TableCell>
                      {employee.is_active
                        ? 'Ativo'
                        : 'Inativo'}
                    </TableCell>

                    {canManage && (
                      <TableCell align="right">
                        <IconButton
                          onClick={() =>
                            openEditDialog(
                              employee,
                            )
                          }
                        >
                          <Edit />
                        </IconButton>

                        <IconButton
                          color="error"
                          onClick={() =>
                            handleDelete(
                              employee,
                            )
                          }
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    )}
                  </TableRow>
                ),
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog
        open={dialogOpen}
        onClose={() =>
          setDialogOpen(false)
        }
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          {editingEmployee
            ? 'Editar funcionário'
            : 'Novo funcionário'}
        </DialogTitle>

        <DialogContent>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                md: '1fr 1fr',
              },
              gap: 2,
              mt: 1,
            }}
          >
            <TextField
              label="Nome"
              value={firstName}
              onChange={(event) =>
                setFirstName(
                  event.target.value,
                )
              }
            />

            <TextField
              label="Sobrenome"
              value={lastName}
              onChange={(event) =>
                setLastName(
                  event.target.value,
                )
              }
            />

            <TextField
              label="E-mail"
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value,
                )
              }
            />

            <TextField
              label="Telefone"
              value={phone}
              onChange={(event) =>
                setPhone(
                  event.target.value,
                )
              }
            />

            <TextField
              label="Documento"
              value={document}
              onChange={(event) =>
                setDocument(
                  event.target.value,
                )
              }
            />

            <TextField
              label="Data de admissão"
              type="date"
              slotProps={{
                inputLabel: {
                  shrink: true,
                },
              }}
              value={hireDate}
              onChange={(event) =>
                setHireDate(
                  event.target.value,
                )
              }
            />

            <TextField
              label="Salário"
              type="number"
              value={salary}
              onChange={(event) =>
                setSalary(
                  event.target.value,
                )
              }
            />

            <TextField
              select
              label="Departamento"
              value={departmentId}
              onChange={(event) =>
                setDepartmentId(
                  event.target.value,
                )
              }
            >
              {departments.map(
                (department) => (
                  <MenuItem
                    key={department.id}
                    value={department.id}
                  >
                    {department.name}
                  </MenuItem>
                ),
              )}
            </TextField>

            <FormControlLabel
              control={
                <Checkbox
                  checked={isActive}
                  onChange={(event) =>
                    setIsActive(
                      event.target.checked,
                    )
                  }
                />
              }
              label="Funcionário ativo"
            />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() =>
              setDialogOpen(false)
            }
          >
            Cancelar
          </Button>

          <Button
            variant="contained"
            onClick={handleSave}
            disabled={
              !firstName.trim()
              || !lastName.trim()
              || !email.trim()
              || !document.trim()
              || !hireDate
              || !salary
              || !departmentId
            }
          >
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}