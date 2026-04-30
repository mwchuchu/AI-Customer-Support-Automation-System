import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,

      setAuth: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
      isAuthenticated: () => !!get().token,
      isAgent: () => ['agent', 'admin'].includes(get().user?.role),
      isAdmin: () => get().user?.role === 'admin',
    }),
    { name: 'ai-support-auth' }
  )
)
