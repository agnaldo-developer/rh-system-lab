import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  TextField,
  Typography,
} from '@mui/material'

import { useAuth } from '../../contexts/AuthContext'


export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(
    event: React.FormEvent,
  ) {
    event.preventDefault()

    setLoading(true)
    setError('')

    try {
      await login({
        email,
        password,
      })

      navigate('/dashboard')
    } catch {
      setError(
        'E-mail ou senha inválidos.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          md: '1fr 1fr',
        },
      }}
    >
      <Box
        sx={{
          display: {
            xs: 'none',
            md: 'flex',
          },
          alignItems: 'center',
          justifyContent: 'center',
          p: 6,
          color: 'white',
          background:
            'linear-gradient(135deg, #082f49 0%, #0f4c81 100%)',
        }}
      >
        <Box sx={{ maxWidth: 480 }}>
          <Typography
            variant="h2"
            gutterBottom
            sx={{
              fontWeight: 700,
            }}
          >
            RH System
          </Typography>

          <Typography
            variant="h6"
            sx={{
              opacity: 0.9,
              lineHeight: 1.6,
            }}
          >
            Gestão de pessoas, departamentos,
            usuários e auditoria em um único sistema.
          </Typography>
        </Box>
      </Box>

      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
          backgroundColor: '#f4f6f8',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            width: '100%',
            maxWidth: 420,
            p: 4,
            borderRadius: 3,
          }}
        >
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
            }}
          >
            Bem-vindo de volta!
          </Typography>

          <Typography
            color="text.secondary"
            sx={{ mt: 1, mb: 3 }}
          >
            Faça login para acessar o RH System.
          </Typography>

          {error && (
            <Alert
              severity="error"
              sx={{ mb: 2 }}
            >
              {error}
            </Alert>
          )}

          <Box
            component="form"
            onSubmit={handleSubmit}
          >
            <TextField
              fullWidth
              label="E-mail"
              type="email"
              autoComplete="email"
              margin="normal"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />

            <TextField
              fullWidth
              label="Senha"
              type="password"
              autoComplete="current-password"
              margin="normal"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              required
            />

            <Button
              fullWidth
              variant="contained"
              type="submit"
              size="large"
              disabled={loading}
              sx={{
                mt: 3,
                py: 1.4,
              }}
            >
              {loading ? (
                <CircularProgress
                  size={24}
                  color="inherit"
                />
              ) : (
                'Entrar'
              )}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  )
}
