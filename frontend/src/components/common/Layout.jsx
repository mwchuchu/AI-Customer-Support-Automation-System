import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import {
  LayoutDashboard, Ticket, BarChart3, LogOut, Bot, Plus, Users
} from 'lucide-react'
import styles from './Layout.module.css'

export default function Layout() {
  const { user, logout, isAdmin } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  const navItems = [
    { to: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/tickets',    icon: Ticket,           label: 'Tickets' },
    ...(isAdmin() ? [{ to: '/analytics', icon: BarChart3, label: 'Analytics' }] : []),
  ]

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <Bot size={22} className={styles.logoIcon} />
          <div>
            <span className={styles.logoText}>SupportAI</span>
            <span className={styles.logoSub}>Powered by Gemini</span>
          </div>
        </div>

        <nav className={styles.nav}>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.active : ''}`
              }
            >
              <Icon size={16} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <button
          className={styles.newTicketBtn}
          onClick={() => navigate('/tickets/new')}
        >
          <Plus size={16} /> New Ticket
        </button>

        <div className={styles.userSection}>
          <div className={styles.userInfo}>
            <div className={styles.avatar}>
              {user?.full_name?.[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <div className={styles.userName}>{user?.full_name}</div>
              <div className={styles.userRole}>{user?.role}</div>
            </div>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout} title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}
