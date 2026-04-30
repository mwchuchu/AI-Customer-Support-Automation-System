import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import TicketsPage from './pages/TicketsPage'
import TicketDetailPage from './pages/TicketDetailPage'
import NewTicketPage from './pages/NewTicketPage'
import AnalyticsPage from './pages/AnalyticsPage'
import Layout from './components/common/Layout'

function ProtectedRoute({ children }) {
  const token = useAuthStore((s) => s.token)
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index           element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"  element={<DashboardPage />} />
          <Route path="tickets"    element={<TicketsPage />} />
          <Route path="tickets/new"element={<NewTicketPage />} />
          <Route path="tickets/:id"element={<TicketDetailPage />} />
          <Route path="analytics"  element={<AnalyticsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
