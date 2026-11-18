<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BrandLogo from '@/shared/components/layout/BrandLogo.vue'
import AppAvatar from '@/shared/components/ui/AppAvatar.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useUiStore } from '@/stores/ui.store'
import type { IconName } from '@/types/icons'

const props = defineProps<{ variant: 'tecnico' | 'comercio' }>()

const auth = useAuthStore()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()

interface NavItem {
  label: string
  to: string
  icon: IconName
  disabled?: boolean
}

const items = computed<NavItem[]>(() => {
  if (props.variant === 'comercio') {
    return [
      { label: 'Inicio', to: '/comercio/inicio', icon: 'home' },
      { label: 'Pagos', to: '/comercio/pagos', icon: 'card' },
      { label: 'Saldo', to: '/comercio/saldo', icon: 'wallet' },
      { label: 'Devoluciones', to: '/comercio/devoluciones', icon: 'refund' },
      { label: 'Tickets', to: '/comercio/tickets', icon: 'ticket' },
    ]
  }

  const techItems: NavItem[] = [
    { label: 'Tickets', to: '/tecnico/tickets', icon: 'ticket' },
    { label: 'Comercios', to: '/tecnico/comercios', icon: 'shop' },
  ]
  if (auth.role === 'admin') {
    techItems.push({ label: 'Técnicos', to: '/tecnico/tecnicos', icon: 'inbox' })
  }
  return techItems
})

const sectionLabel = computed(() => {
  if (props.variant === 'comercio') return 'ESPACIO COMERCIO'
  return auth.role === 'admin' ? 'ADMINISTRACIÓN' : 'ESPACIO TÉCNICO'
})

const profileRoute = computed(() =>
  props.variant === 'comercio' ? '/comercio/perfil' : '/tecnico/perfil',
)

const userSubtitle = computed(() =>
  props.variant === 'comercio' ? auth.user?.companyName ?? 'Comercio' : auth.user?.subtitle ?? '',
)

const avatarSrc = computed(() =>
  props.variant === 'tecnico' ? '/images/avatar-laura.jpg' : undefined,
)

function isActive(to: string): boolean {
  return route.path === to || route.path.startsWith(`${to}/`)
}

function go(to: string): void {
  ui.closeSidebar()
  void router.push(to)
}

async function handleLogout(): Promise<void> {
  ui.closeSidebar()
  const portal = props.variant
  await auth.logout()
  // Recarga completa para vaciar los stores y no arrastrar datos de otra sesión.
  window.location.assign(`/sesion-cerrada?portal=${portal}`)
}
</script>

<template>
  <div>
    <Transition
      enter-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-150"
      leave-to-class="opacity-0"
    >
      <button
        v-if="ui.sidebarOpen"
        type="button"
        class="fixed inset-0 z-40 bg-[rgba(15,23,42,0.45)] lg:hidden"
        aria-label="Cerrar menú"
        @click="ui.closeSidebar()"
      />
    </Transition>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-[224px] shrink-0 flex-col bg-brand-900 px-4 pb-4 pt-3 transition-transform duration-200 lg:sticky lg:top-0 lg:z-0 lg:h-screen lg:translate-x-0"
      :class="ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      aria-label="Navegación principal"
    >
      <button
        type="button"
        class="absolute right-2 top-2 grid size-10 place-items-center rounded-md text-brand-300 transition-colors hover:bg-white/10 hover:text-white lg:hidden"
        aria-label="Cerrar navegación"
        @click="ui.closeSidebar()"
      >
        <AppIcon name="x" :size="20" />
      </button>

      <div class="flex justify-center">
        <BrandLogo variant="sidebar" />
      </div>

      <p class="mt-4 px-3 text-[10px] font-semibold leading-[1.5] tracking-[0.02em] text-brand-300">
        {{ sectionLabel }}
      </p>

      <nav class="mt-2 flex flex-col gap-3">
        <button
          v-for="item in items"
          :key="item.to"
          type="button"
          class="relative flex h-12 w-full items-center gap-3 overflow-hidden rounded-md px-4 text-left transition-colors"
          :class="
            isActive(item.to)
              ? 'bg-brand-700 text-white'
              : 'text-brand-300 hover:bg-white/5 hover:text-white'
          "
          :aria-current="isActive(item.to) ? 'page' : undefined"
          @click="go(item.to)"
        >
          <span
            v-if="isActive(item.to)"
            class="absolute inset-y-0 left-0 w-[3px] rounded-r-sm bg-accent"
            aria-hidden="true"
          />
          <AppIcon :name="item.icon" :size="20" />
          <span class="text-[15px] leading-[1.5]" :class="isActive(item.to) ? 'font-semibold' : 'font-medium'">
            {{ item.label }}
          </span>
        </button>
      </nav>

      <div class="mt-auto">
        <div class="mx-2 h-px bg-[rgba(201,191,239,0.25)]" />
        <div class="flex items-center gap-3 px-1 pb-2 pt-5">
          <AppAvatar
            :name="auth.user?.name ?? 'Usuario'"
            :src="avatarSrc"
            :size="40"
            shape="circle"
            tone="brand"
          />
          <button
            type="button"
            class="flex min-w-0 flex-1 items-center justify-between gap-2 rounded-md px-1 py-1 text-left transition-colors hover:bg-white/5"
            :aria-label="'Ir a mi perfil'"
            @click="go(profileRoute)"
          >
            <span class="min-w-0">
              <span
                class="block truncate font-semibold leading-[1.5] text-white"
                :class="variant === 'comercio' ? 'text-[13px]' : 'text-[14px]'"
              >
                {{ auth.user?.name }}
              </span>
              <span class="block truncate text-[12px] leading-[1.5] text-brand-300">{{ userSubtitle }}</span>
            </span>
            <span class="flex shrink-0 items-center gap-1 text-[11px] font-medium text-brand-300">
              Mi perfil
              <AppIcon name="chevron-right" :size="14" />
            </span>
          </button>
        </div>
        <button
          type="button"
          class="mt-1 flex h-11 w-full items-center gap-3 rounded-md px-4 text-[14px] font-medium text-brand-300 transition-colors hover:bg-white/5 hover:text-white"
          @click="handleLogout"
        >
          <AppIcon name="logout" :size="20" />
          Cerrar sesión
        </button>
      </div>
    </aside>
  </div>
</template>
