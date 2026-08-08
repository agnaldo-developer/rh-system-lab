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
  Block,
  Edit,
} from '@mui/icons-material'

import {
  createUser,
  deactivateUser,
  listUsers,
  updateUser,
} from '../../api/users'

import type {
  User,
  UserRole,
} from '../../types/user'


export function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [dialogOpen, setDialogOpen] =
    useState(false)

  const [editingUser, setEditingUser] =
    useState<User | null>(null)

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] =
    useState<UserRole>('viewer')
  const [isActive, setIsActive] =
    useState(true)


  async function loadUsers() {
    setLoading(true)
    setError('')

    try {
      const data = await listUsers()
      setUsers(data)
    } catch {
      setError(
        'Não foi possível carregar os usuários.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadUsers()
  }, [])


  function resetForm() {
    setName('')
    setEmail('')
    setPassword('')
    setRole('viewer')
    setIsActive(true)
  }


  function openCreateDialog() {
    setEditingUser(null)
    resetForm()
    setDialogOpen(true)
  }


  function openEditDialog(
    user: User,
  ) {
    setEditingUser(user)
    setName(user.name)
    setEmail(user.email)
    setPassword('')
    setRole(user.role)
    setIsActive(user.is_active)
    setDialogOpen(true)
  }


  async function handleSave() {
    try {
      if (editingUser) {
        const payload = {
          name,
          email,
          role,
          is_active: isActive,
          ...(password
            ? { password }
            : {}),
        }

        await updateUser(
          editingUser.id,
          payload,
        )
      } else {
        await createUser({
          name,
          email,
          password,
          role,
          is_active: isActive,
        })
      }

      setDialogOpen(false)
      await loadUsers()
    } catch {
      setError(
        'Não foi possível salvar o usuário.',
      )
    }
  }


  async function handleDeactivate(
    user: User,
  ) {
    const confirmed = window.confirm(
      `Deseja desativar o usuário "${user.name}"?`,
    )

    if (!confirmed) {
      return
    }

    try {
      await deactivateUser(user.id)
      await loadUsers()
    } catch {
      setError(
        'Não foi possível desativar o usuário.',
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
            Usuários
          </Typography>

          <Typography color="text.secondary">
            Gerencie acessos e perfis do RH System.
          </Typography>
        </Box>

        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={openCreateDialog}
        >
          Novo usuário
        </Button>
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
                <TableCell>Nome</TableCell>
                <TableCell>E-mail</TableCell>
                <TableCell>Perfil</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">
                  Ações
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {users.map((user) => (
                <TableRow
                  key={user.id}
                  hover
                >
                  <TableCell>
                    {user.name}
                  </TableCell>

                  <TableCell>
                    {user.email}
                  </TableCell>

                  <TableCell>
                    {user.role}
                  </TableCell>

                  <TableCell>
                    {user.is_active
                      ? 'Ativo'
                      : 'Inativo'}
                  </TableCell>

                  <TableCell align="right">
                    <IconButton
                      onClick={() =>
                        openEditDialog(user)
                      }
                    >
                      <Edit />
                    </IconButton>

                    <IconButton
                      color="warning"
                      disabled={!user.is_active}
                      onClick={() =>
                        handleDeactivate(user)
                      }
                    >
                      <Block />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
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
          {editingUser
            ? 'Editar usuário'
            : 'Novo usuário'}
        </DialogTitle>

        <DialogContent>
          <TextField
            fullWidth
            label="Nome"
            margin="normal"
            value={name}
            onChange={(event) =>
              setName(event.target.value)
            }
          />

          <TextField
            fullWidth
            label="E-mail"
            type="email"
            margin="normal"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
          />

          <TextField
            fullWidth
            label={
              editingUser
                ? 'Nova senha (opcional)'
                : 'Senha'
            }
            type="password"
            margin="normal"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
          />

          <TextField
            fullWidth
            select
            label="Perfil"
            margin="normal"
            value={role}
            onChange={(event) =>
              setRole(
                event.target.value as UserRole,
              )
            }
          >
            <MenuItem value="admin">
              Admin
            </MenuItem>

            <MenuItem value="rh">
              RH
            </MenuItem>

            <MenuItem value="viewer">
              Viewer
            </MenuItem>
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
            label="Usuário ativo"
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
            disabled={
              !name.trim()
              || !email.trim()
              || (
                !editingUser
                && !password.trim()
              )
            }
          >
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
