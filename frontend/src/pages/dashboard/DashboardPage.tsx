import {
  useEffect,
  useState,
} from 'react'

import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
} from '@mui/material'

import {
  Apartment,
  FactCheck,
  Groups,
  ManageAccounts,
} from '@mui/icons-material'

import {
  getDashboardSummary,
} from '../../api/dashboard'

import type {
  DashboardSummary,
} from '../../api/dashboard'


export function DashboardPage() {
  const [
    summary,
    setSummary,
  ] = useState<DashboardSummary | null>(null)

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState('')


  useEffect(() => {
    getDashboardSummary()
      .then(setSummary)
      .catch(() => {
        setError(
          'Não foi possível carregar os dados do dashboard.',
        )
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])


  const cards = [
    {
      title: 'Funcionários',
      value: summary?.employees ?? 0,
      icon: <Groups />,
    },
    {
      title: 'Departamentos',
      value: summary?.departments ?? 0,
      icon: <Apartment />,
    },
    {
      title: 'Usuários',
      value: summary?.users ?? 0,
      icon: <ManageAccounts />,
    },
    {
      title: 'Auditorias',
      value: summary?.auditLogs ?? 0,
      icon: <FactCheck />,
    },
  ]


  return (
    <Box>
      <Typography
        variant="h4"
        sx={{
          fontWeight: 700,
          mb: 1,
        }}
      >
        Dashboard
      </Typography>

      <Typography
        color="text.secondary"
        sx={{
          mb: 4,
        }}
      >
        Visão geral do RH System.
      </Typography>

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
            minHeight: 240,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress />
        </Box>
      ) : (
        <Grid
          container
          spacing={3}
        >
          {cards.map((card) => (
            <Grid
              key={card.title}
              size={{
                xs: 12,
                sm: 6,
                lg: 3,
              }}
            >
              <Card
                elevation={0}
                sx={{
                  border:
                    '1px solid #e5e7eb',
                  borderRadius: 3,
                }}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent:
                        'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        {card.title}
                      </Typography>

                      <Typography
                        variant="h4"
                        sx={{
                          mt: 1,
                          fontWeight: 700,
                        }}
                      >
                        {card.value}
                      </Typography>
                    </Box>

                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        backgroundColor:
                          '#e8f1f8',
                        color: '#0f4c81',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent:
                          'center',
                      }}
                    >
                      {card.icon}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )
}