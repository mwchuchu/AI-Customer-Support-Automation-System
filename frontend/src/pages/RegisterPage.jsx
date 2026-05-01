import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Bot, Mail, Lock, User, AlertCircle } from 'lucide-react'
import { authApi } from '../services/api'
import { useAuthStore } from '../store/authStore'
import styles from './AuthPage.module.css'

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', full_name: '', password: '', role: 'customer' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await authApi.register(form)
      setAuth(data.user, data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.header}>
          <div className={styles.iconWrap}><Bot size={28} /></div>
          <h1 className={styles.title}>Create Account</h1>
          <p className={styles.subtitle}>Join SupportAI workspace</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}><AlertCircle size={14} /> {error}</div>}

          <div className={styles.field}>
            <label>Full Name</label>
            <div className={styles.inputWrap}>
              <User size={15} className={styles.icon} />
              <input type="text" placeholder="Jane Smith" value={form.full_name} onChange={set('full_name')} required />
            </div>
          </div>
          <div className={styles.field}>
            <label>Email</label>
            <div className={styles.inputWrap}>
              <Mail size={15} className={styles.icon} />
              <input type="email" placeholder="you@example.com" value={form.email} onChange={set('email')} required />
            </div>
          </div>
          <div className={styles.field}>
            <label>Password</label>
            <div className={styles.inputWrap}>
              <Lock size={15} className={styles.icon} />
              <input type="password" placeholder="Min. 6 characters" value={form.password} onChange={set('password')} minLength={6} required />
            </div>
          </div>
          <div className={styles.field}>
            <label>Role</label>
            <div className={styles.inputWrap}>
              <User size={15} className={styles.icon} />
              <select value={form.role} onChange={set('role')}>
                <option value="customer">Customer</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </div>

          <button type="submit" className={styles.submit} disabled={loading}>
            {loading ? <span className={styles.spinner} /> : 'Create Account'}
          </button>
        </form>

        <p className={styles.footer}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
