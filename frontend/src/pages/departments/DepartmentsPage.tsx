import {
  useEffect,
  useState,
} from 'react'

import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
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
  createDepartment,
  deleteDepartment,
  listDepartments,
  updateDepartment,
} from '../../api/departments'

import { useAuth } from '../../contexts/AuthContext'

import type {
  Department,
} from '../../types/department'


export function DepartmentsPage() {
  const { user } = useAuth()

  const canManage =
    user?.role === 'admin'
    || user?.role === 'rh'

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
    editingDepartment,
    setEditingDepartment,
  ] = useState<Department | null>(null)

  const [
    name,
    setName,
  ] = useState('')

  const [
    description,
    setDescription,
  ] = useState('')


  async function loadDepartments() {
    setLoading(true)
    setError('')

    try {
      const data = await listDepartments()
      setDepartments(data)
    } catch {
      setError(
        'Não foi possível carregar os departamentos.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadDepartments()
  }, [])


  function openCreateDialog() {
    setEditingDepartment(null)
    setName('')
    setDescription('')
    setDialogOpen(true)
  }


  function openEditDialog(
    department: Department,
  ) {
    setEditingDepartment(department)
    setName(department.name)
    setDescription(
      department.description ?? '',
    )
    setDialogOpen(true)
  }


  async function handleSave() {
    try {
      if (editingDepartment) {
        await updateDepartment(
          editingDepartment.id,
          {
            name,
            description,
          },
        )
      } else {
        await createDepartment({
          name,
          description,
        })
      }

      setDialogOpen(false)
      await loadDepartments()
    } catch {
      setError(
        'Não foi possível salvar o departamento.',
      )
    }
  }


  async function handleDelete(
    department: Department,
  ) {
    const confirmed = window.confirm(
      `Deseja excluir o departamento "${department.name}"?`,
    )

    if (!confirmed) {
      return
    }

    try {
      await deleteDepartment(
        department.id,
      )

      await loadDepartments()
    } catch {
      setError(
        'Não foi possível excluir o departamento.',
      )
    }
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
            Departamentos
          </Typography>

          <Typography color="text.secondary">
            Gerencie os departamentos da empresa.
          </Typography>
        </Box>

        {canManage && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={openCreateDialog}
          >
            Novo departamento
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
            border: '1px solid #e5e7eb',
            borderRadius: 3,
          }}
        >
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Nome</TableCell>
                <TableCell>
                  Descrição
                </TableCell>

                {canManage && (
                  <TableCell align="right">
                    Ações
                  </TableCell>
                )}
              </TableRow>
            </TableHead>

            <TableBody>
              {departments.map(
                (department) => (
                  <TableRow
                    key={department.id}
                    hover
                  >
                    <TableCell>
                      {department.id}
                    </TableCell>

                    <TableCell>
                      {department.name}
                    </TableCell>

                    <TableCell>
                      {department.description || '-'}
                    </TableCell>

                    {canManage && (
                      <TableCell align="right">
                        <IconButton
                          onClick={() =>
                            openEditDialog(
                              department,
                            )
                          }
                        >
                          <Edit />
                        </IconButton>

                        <IconButton
                          color="error"
                          onClick={() =>
                            handleDelete(
                              department,
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
        maxWidth="sm"
      >
        <DialogTitle>
          {editingDepartment
            ? 'Editar departamento'
            : 'Novo departamento'}
        </DialogTitle>

        <DialogContent>
          <TextField
            fullWidth
            label="Nome"
            margin="normal"
            value={name}
            onChange={(event) =>
              setName(
                event.target.value,
              )
            }
          />

          <TextField
            fullWidth
            label="Descrição"
            margin="normal"
            multiline
            rows={3}
            value={description}
            onChange={(event) =>
              setDescription(
                event.target.value,
              )
            }
          />
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
            disabled={!name.trim()}
          >
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}