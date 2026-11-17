import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Portal, Session } from '@/types'
import { login as loginService, logout as logoutService } from '@/services/auth.service'

const STORAGE_KEY = 'plp.session'

function readStoredSession(): Session | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Session
    if (!parsed?.token || !parsed?.user?.role) return null
    return parsed
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const session = ref<Session | null>(readStoredSession())
  const loading = ref(false)
  const error = ref('')

  const user = computed(() => session.value?.user ?? null)
  const token = computed(() => session.value?.token ?? '')
  const isAuthenticated = computed(() => Boolean(session.value?.token))
  const role = computed(() => session.value?.user.role ?? null)
  const homeRoute = computed(() => {
    if (role.value === 'comercio') return '/comercio/inicio'
    return '/tecnico/tickets'
  })
  const loginRoute = computed(() => (role.value === 'comercio' ? '/acceso-comercio' : '/acceso-tecnico'))

  function persist(next: Session | null): void {
    session.value = next
    if (next) localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    else localStorage.removeItem(STORAGE_KEY)
  }

  async function login(username: string, password: string, portal: Portal): Promise<void> {
    loading.value = true
    error.value = ''
    try {
      const next = await loginService(username, password, portal)
      persist(next)
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudo iniciar sesión.'
      throw cause
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    loading.value = true
    try {
      await logoutService()
    } catch {
      // El cierre de sesión local debe completarse aunque falle la API.
    } finally {
      persist(null)
      loading.value = false
    }
  }

  function clearError(): void {
    error.value = ''
  }

  return {
    session,
    user,
    token,
    isAuthenticated,
    role,
    loading,
    error,
    homeRoute,
    loginRoute,
    login,
    logout,
    clearError,
  }
})
