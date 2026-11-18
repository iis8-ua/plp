import 'vue-router'
import type { Portal, UserRole } from '@/types'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    guestOnly?: boolean
    portal?: Portal
    /** Roles con acceso a la ruta. Si se omite, cualquier rol del portal puede entrar. */
    roles?: UserRole[]
  }
}
