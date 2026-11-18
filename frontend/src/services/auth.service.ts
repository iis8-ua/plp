import type { AuthUser, Portal, Session } from '@/types'
import { ApiError } from '@/services/errors'
import { request } from '@/services/http'

interface LoginResponse {
  token: string
  token_type: string
  expires_in?: number
  user: AuthUser & { force_password_change?: boolean }
}

export async function login(username: string, password: string, portal: Portal): Promise<Session> {
  const normalized = username.trim()

  const response = await request<LoginResponse>('/login', {
    method: 'POST',
    query: { user: normalized },
    body: { password },
    auth: false,
  })

  if (!response.user?.role) {
    throw new ApiError('La respuesta de autenticación no incluye el usuario.', 500, 'INVALID_RESPONSE')
  }

  const isMerchantAccount = response.user.role === 'comercio'
  if ((portal === 'comercio') !== isMerchantAccount) {
    throw new ApiError(
      portal === 'comercio'
        ? 'Este usuario no pertenece al portal de comercios.'
        : 'Este usuario no pertenece al portal técnico.',
      401,
      'INVALID_PORTAL',
    )
  }

  const user: AuthUser = {
    ...response.user,
    forcePasswordChange: response.user.force_password_change ?? false,
  }

  return { token: response.token, user }
}

export async function logout(): Promise<void> {
  await request<{ message: string }>('/logout', { method: 'POST' })
}
