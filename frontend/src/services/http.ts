import { ApiError } from '@/services/errors'

const env = import.meta.env as Record<string, string | undefined>

export const API_BASE = env.VITE_API_BASE_URL ?? '/api'

const REQUEST_TIMEOUT_MS = 15_000

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  query?: Record<string, string | number | undefined>
  body?: unknown
  auth?: boolean
}

interface StoredSession {
  token?: string
  user?: { role?: string }
}

function readStoredSession(): StoredSession | null {
  try {
    const raw = localStorage.getItem('plp.session')
    if (!raw) return null
    return JSON.parse(raw) as StoredSession
  } catch {
    return null
  }
}

function readToken(): string {
  return readStoredSession()?.token ?? ''
}

function loginRouteForSession(): string {
  return readStoredSession()?.user?.role === 'comercio' ? '/acceso-comercio' : '/acceso-tecnico'
}

function handleUnauthorized(): void {
  localStorage.removeItem('plp.session')
  window.location.assign(loginRouteForSession())
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', query, body, auth = true } = options

  const url = new URL(`${API_BASE}${path}`, window.location.origin)

  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== '') url.searchParams.set(key, String(value))
  })

  const headers: Record<string, string> = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  if (auth) {
    const token = readToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }

  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(url.toString(), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    })
  } catch {
    throw new ApiError('No se pudo conectar con el servidor. Inténtalo de nuevo.', 0, 'NETWORK_ERROR')
  } finally {
    window.clearTimeout(timeout)
  }

  if (!response.ok) {
    if (response.status === 401 && auth && readToken()) {
      handleUnauthorized()
    }

    let message = `Error ${response.status}`
    let code: string | undefined
    try {
      const payload = (await response.json()) as { message?: string; code?: string }
      message = payload.message ?? message
      code = payload.code
    } catch {
      // La respuesta no era JSON.
    }
    throw new ApiError(message, response.status, code)
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}
