import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import type { Portal } from '@/types'

/** Ruta que muestra el estado "Acceso restringido" para cada portal. */
const ACCESS_DENIED_ROUTE: Partial<Record<Portal, string>> = {
  tecnico: 'tech-access-restricted',
  comercio: 'merchant-home',
}

export function installGuards(router: Router): void {
  router.beforeEach((to) => {
    const auth = useAuthStore()

    if (to.meta.guestOnly && auth.isAuthenticated) {
      return auth.homeRoute
    }

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return to.meta.portal === 'comercio' ? '/acceso-comercio' : '/acceso-tecnico'
    }

    if (to.meta.portal === 'comercio' && auth.isAuthenticated && auth.role !== 'comercio') {
      return auth.homeRoute
    }

    if (to.meta.portal === 'tecnico' && auth.isAuthenticated && auth.role === 'comercio') {
      return auth.homeRoute
    }

    if (to.meta.roles?.length && auth.role && !to.meta.roles.includes(auth.role)) {
      const deniedRoute = to.meta.portal ? ACCESS_DENIED_ROUTE[to.meta.portal] : undefined
      return deniedRoute && deniedRoute !== to.name ? { name: deniedRoute } : auth.homeRoute
    }

    return true
  })

  router.afterEach((to) => {
    const title = to.meta.title ?? 'PLP · Pasa La Pasta'
    document.title = title === 'PLP · Pasa La Pasta' ? title : `${title} · PLP`
  })
}
