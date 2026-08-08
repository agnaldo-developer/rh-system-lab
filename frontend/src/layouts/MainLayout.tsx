import {
  Box,
  Button,
  Divider,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from '@mui/material'

import {
  Apartment as ApartmentIcon,
  Dashboard as DashboardIcon,
  FactCheck as FactCheckIcon,
  Groups as GroupsIcon,
  Logout as LogoutIcon,
  ManageAccounts as ManageAccountsIcon,
} from '@mui/icons-material'

import {
  NavLink,
  Outlet,
  useNavigate,
} from 'react-router-dom'

import { useAuth } from '../contexts/AuthContext'


const drawerWidth = 240


export function MainLayout() {
  const {
    user,
    logout,
  } = useAuth()

  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const menuItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: <DashboardIcon />,
      roles: ['admin', 'rh', 'viewer'],
    },
    {
      label: 'Funcionários',
      path: '/employees',
      icon: <GroupsIcon />,
      roles: ['admin', 'rh', 'viewer'],
    },
    {
      label: 'Departamentos',
      path: '/departments',
      icon: <ApartmentIcon />,
      roles: ['admin', 'rh', 'viewer'],
    },
    {
      label: 'Usuários',
      path: '/users',
      icon: <ManageAccountsIcon />,
      roles: ['admin'],
    },
    {
      label: 'Auditoria',
      path: '/audit',
      icon: <FactCheckIcon />,
      roles: ['admin'],
    },
  ]

  const visibleMenuItems = menuItems.filter(
    (item) =>
      user
        ? item.roles.includes(user.role)
        : false,
  )

  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: '#f4f6f8',
      }}
    >
      <Box
        component="aside"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          backgroundColor: '#0f2740',
          color: 'white',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box
          sx={{
            px: 3,
            py: 3,
          }}
        >
          <Typography
            variant="h5"
            sx={{
              fontWeight: 700,
            }}
          >
            RH System
          </Typography>

          <Typography
            variant="body2"
            sx={{
              opacity: 0.7,
              mt: 0.5,
            }}
          >
            Gestão de Pessoas
          </Typography>
        </Box>

        <Divider
          sx={{
            borderColor: 'rgba(255,255,255,0.1)',
          }}
        />

        <List
          sx={{
            px: 1.5,
            py: 2,
            flexGrow: 1,
          }}
        >
          {visibleMenuItems.map((item) => (
            <ListItemButton
              key={item.path}
              component={NavLink}
              to={item.path}
              sx={{
                color: 'white',
                borderRadius: 2,
                mb: 0.5,

                '&.active': {
                  backgroundColor:
                    'rgba(255,255,255,0.12)',
                },

                '&:hover': {
                  backgroundColor:
                    'rgba(255,255,255,0.08)',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: 'inherit',
                  minWidth: 40,
                }}
              >
                {item.icon}
              </ListItemIcon>

              <ListItemText
                primary={item.label}
              />
            </ListItemButton>
          ))}
        </List>

        <Divider
          sx={{
            borderColor: 'rgba(255,255,255,0.1)',
          }}
        />

        <Box
          sx={{
            p: 2,
          }}
        >
          <Button
            fullWidth
            startIcon={<LogoutIcon />}
            onClick={handleLogout}
            sx={{
              color: 'white',
              justifyContent: 'flex-start',
            }}
          >
            Sair
          </Button>
        </Box>
      </Box>

      <Box
        sx={{
          flexGrow: 1,
          minWidth: 0,
        }}
      >
        <Box
          component="header"
          sx={{
            height: 72,
            backgroundColor: 'white',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            px: 4,
          }}
        >
          <Box>
            <Typography
              variant="body2"
              color="text.secondary"
            >
              Usuário autenticado
            </Typography>

            <Typography
              sx={{
                fontWeight: 600,
              }}
            >
              {user?.name ?? '-'}
            </Typography>
          </Box>

          <Box
            sx={{
              textAlign: 'right',
            }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
            >
              Perfil
            </Typography>

            <Typography
              sx={{
                fontWeight: 600,
                textTransform: 'uppercase',
              }}
            >
              {user?.role ?? '-'}
            </Typography>
          </Box>
        </Box>

        <Box
          component="main"
          sx={{
            p: 4,
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  )
}