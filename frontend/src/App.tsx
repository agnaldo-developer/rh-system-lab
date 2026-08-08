import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import {
  LoginPage,
} from './pages/auth/LoginPage'

import {
  DashboardPage,
} from './pages/dashboard/DashboardPage'

import {
  EmployeesPage,
} from './pages/employees/EmployeesPage'

import {
  DepartmentsPage,
} from './pages/departments/DepartmentsPage'

import {
  UsersPage,
} from './pages/users/UsersPage'

import {
  AuditPage,
} from './pages/audit/AuditPage'

import {
  MainLayout,
} from './layouts/MainLayout'

import {
  ProtectedRoute,
} from './routes/ProtectedRoute'

import {
  RoleRoute,
} from './routes/RoleRoute'


function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route
          path="/dashboard"
          element={
            <DashboardPage />
          }
        />

        <Route
          path="/employees"
          element={
            <EmployeesPage />
          }
        />

        <Route
          path="/departments"
          element={
            <DepartmentsPage />
          }
        />

        <Route
          path="/users"
          element={
            <RoleRoute
              allowedRoles={[
                'admin',
              ]}
            >
              <UsersPage />
            </RoleRoute>
          }
        />

        <Route
          path="/audit"
          element={
            <RoleRoute
              allowedRoles={[
                'admin',
              ]}
            >
              <AuditPage />
            </RoleRoute>
          }
        />
      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />
    </Routes>
  )
}

export default App