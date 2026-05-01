import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Attach token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login:    (data) => api.post('/auth/login', data),
  me:       ()     => api.get('/auth/me'),
}

// ── Tickets ───────────────────────────────────
export const ticketsApi = {
  create: (data)             => api.post('/tickets/', data),
  list:   (params)           => api.get('/tickets/', { params }),
  get:    (id)               => api.get(`/tickets/${id}`),
  update: (id, data)         => api.patch(`/tickets/${id}`, data),
}

// ── Analytics ─────────────────────────────────
export const analyticsApi = {
  summary: () => api.get('/analytics/summary'),
}

export default api
