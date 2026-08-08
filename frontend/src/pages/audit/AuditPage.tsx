import {
  useEffect,
  useState,
} from 'react'

import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
  Refresh,
  Visibility,
} from '@mui/icons-material'

import {
  listAuditLogs,
} from '../../api/audit'

import {
  listUsers,
} from '../../api/users'

import type {
  AuditLog,
} from '../../types/audit'

import type {
  User,
} from '../../types/user'


export function AuditPage() {
  const [
    logs,
    setLogs,
  ] = useState<AuditLog[]>([])

  const [
    users,
    setUsers,
  ] = useState<User[]>([])

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState('')

  const [
    action,
    setAction,
  ] = useState('')

  const [
    entityType,
    setEntityType,
  ] = useState('')

  const [
    userId,
    setUserId,
  ] = useState('')

  const [
    selectedLog,
    setSelectedLog,
  ] = useState<AuditLog | null>(null)


  async function loadAuditLogs() {
    setLoading(true)
    setError('')

    try {
      const data = await listAuditLogs({
        action:
          action || undefined,
        entity_type:
          entityType || undefined,
        user_id:
          userId
            ? Number(userId)
            : undefined,
      })

      setLogs(data)
    } catch {
      setError(
        'Não foi possível carregar os registros de auditoria.',
      )
    } finally {
      setLoading(false)
    }
  }


  async function loadUsers() {
    try {
      const data = await listUsers()
      setUsers(data)
    } catch {
      setUsers([])
    }
  }


  useEffect(() => {
    loadUsers()
    loadAuditLogs()
  }, [])


  function getUserName(
    id: number | null,
  ) {
    if (id === null) {
      return '-'
    }

    return (
      users.find(
        (user) =>
          user.id === id,
      )?.name
      ?? `Usuário #${id}`
    )
  }


  function formatDate(
    value: string,
  ) {
    return new Date(
      value,
    ).toLocaleString(
      'pt-BR',
    )
  }


  function getActionColor(
    value: string,
  ):
    | 'default'
    | 'success'
    | 'warning'
    | 'error'
    | 'info' {
    switch (value) {
      case 'CREATE':
      case 'LOGIN_SUCCESS':
        return 'success'

      case 'UPDATE':
        return 'info'

      case 'DELETE':
      case 'DEACTIVATE':
        return 'warning'

      case 'LOGIN_FAILED':
        return 'error'

      default:
        return 'default'
    }
  }


  function clearFilters() {
    setAction('')
    setEntityType('')
    setUserId('')

    setTimeout(() => {
      loadAuditLogs()
    }, 0)
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
            Auditoria
          </Typography>

          <Typography
            color="text.secondary"
          >
            Consulte as atividades registradas no RH System.
          </Typography>
        </Box>

        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadAuditLogs}
        >
          Atualizar
        </Button>
      </Box>

      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 3,
          border:
            '1px solid #e5e7eb',
          borderRadius: 3,
        }}
      >
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              md: '1fr 1fr 1fr auto',
            },
            gap: 2,
          }}
        >
          <TextField
            select
            label="Ação"
            value={action}
            onChange={(event) =>
              setAction(
                event.target.value,
              )
            }
          >
            <MenuItem value="">
              Todas
            </MenuItem>

            <MenuItem value="CREATE">
              CREATE
            </MenuItem>

            <MenuItem value="UPDATE">
              UPDATE
            </MenuItem>

            <MenuItem value="DELETE">
              DELETE
            </MenuItem>

            <MenuItem value="DEACTIVATE">
              DEACTIVATE
            </MenuItem>

            <MenuItem value="LOGIN_SUCCESS">
              LOGIN_SUCCESS
            </MenuItem>

            <MenuItem value="LOGIN_FAILED">
              LOGIN_FAILED
            </MenuItem>
          </TextField>

          <TextField
            select
            label="Entidade"
            value={entityType}
            onChange={(event) =>
              setEntityType(
                event.target.value,
              )
            }
          >
            <MenuItem value="">
              Todas
            </MenuItem>

            <MenuItem value="employee">
              Funcionário
            </MenuItem>

            <MenuItem value="department">
              Departamento
            </MenuItem>

            <MenuItem value="user">
              Usuário
            </MenuItem>

            <MenuItem value="authentication">
              Autenticação
            </MenuItem>
          </TextField>

          <TextField
            select
            label="Usuário"
            value={userId}
            onChange={(event) =>
              setUserId(
                event.target.value,
              )
            }
          >
            <MenuItem value="">
              Todos
            </MenuItem>

            {users.map(
              (user) => (
                <MenuItem
                  key={user.id}
                  value={user.id}
                >
                  {user.name}
                </MenuItem>
              ),
            )}
          </TextField>

          <Box
            sx={{
              display: 'flex',
              gap: 1,
              alignItems: 'center',
            }}
          >
            <Button
              variant="contained"
              onClick={loadAuditLogs}
            >
              Filtrar
            </Button>

            <Button
              onClick={clearFilters}
            >
              Limpar
            </Button>
          </Box>
        </Box>
      </Paper>

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
                <TableCell>
                  Data/Hora
                </TableCell>

                <TableCell>
                  Usuário
                </TableCell>

                <TableCell>
                  Ação
                </TableCell>

                <TableCell>
                  Entidade
                </TableCell>

                <TableCell>
                  ID Entidade
                </TableCell>

                <TableCell>
                  Request ID
                </TableCell>

                <TableCell align="right">
                  Detalhes
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {logs.map(
                (log) => (
                  <TableRow
                    key={log.id}
                    hover
                  >
                    <TableCell>
                      {formatDate(
                        log.created_at,
                      )}
                    </TableCell>

                    <TableCell>
                      {getUserName(
                        log.user_id,
                      )}
                    </TableCell>

                    <TableCell>
                      <Chip
                        size="small"
                        label={log.action}
                        color={
                          getActionColor(
                            log.action,
                          )
                        }
                      />
                    </TableCell>

                    <TableCell>
                      {log.entity_type}
                    </TableCell>

                    <TableCell>
                      {log.entity_id ?? '-'}
                    </TableCell>

                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          maxWidth: 200,
                          overflow: 'hidden',
                          textOverflow:
                            'ellipsis',
                          whiteSpace:
                            'nowrap',
                        }}
                      >
                        {log.request_id ?? '-'}
                      </Typography>
                    </TableCell>

                    <TableCell align="right">
                      <Button
                        size="small"
                        startIcon={
                          <Visibility />
                        }
                        onClick={() =>
                          setSelectedLog(
                            log,
                          )
                        }
                      >
                        Ver
                      </Button>
                    </TableCell>
                  </TableRow>
                ),
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog
        open={
          selectedLog !== null
        }
        onClose={() =>
          setSelectedLog(null)
        }
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          Detalhes da auditoria
        </DialogTitle>

        <DialogContent>
          {selectedLog && (
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                mt: 1,
              }}
            >
              <Typography>
                <strong>ID:</strong>{' '}
                {selectedLog.id}
              </Typography>

              <Typography>
                <strong>Ação:</strong>{' '}
                {selectedLog.action}
              </Typography>

              <Typography>
                <strong>Entidade:</strong>{' '}
                {selectedLog.entity_type}
              </Typography>

              <Typography>
                <strong>Usuário:</strong>{' '}
                {getUserName(
                  selectedLog.user_id,
                )}
              </Typography>

              <Typography>
                <strong>Request ID:</strong>{' '}
                {selectedLog.request_id ?? '-'}
              </Typography>

              <Typography>
                <strong>Data:</strong>{' '}
                {formatDate(
                  selectedLog.created_at,
                )}
              </Typography>

              <Box>
                <Typography
                  sx={{
                    fontWeight: 700,
                    mb: 1,
                  }}
                >
                  Details
                </Typography>

                <Box
                  component="pre"
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    backgroundColor:
                      '#0f172a',
                    color: '#e2e8f0',
                    overflow: 'auto',
                    fontSize: 13,
                  }}
                >
                  {JSON.stringify(
                    selectedLog.details,
                    null,
                    2,
                  )}
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() =>
              setSelectedLog(null)
            }
          >
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}