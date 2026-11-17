<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import PageErrorState from '@/shared/components/ui/PageErrorState.vue'

const auth = useAuthStore()
const router = useRouter()

function goHome(): void {
  void router.push(auth.isAuthenticated ? auth.homeRoute : '/acceso-tecnico')
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-app">
    <header class="flex h-16 items-center gap-3 border-b border-line bg-white px-4 lg:h-24 lg:px-8">
      <span class="grid size-9 place-items-center rounded-md bg-brand-100 text-brand-700">
        <AppIcon name="ban" :size="20" />
      </span>
      <p class="text-[14px] font-semibold text-ink">PLP · Pasa La Pasta</p>
    </header>
    <main class="flex flex-1 items-center justify-center px-4">
      <PageErrorState
        title="Página no encontrada"
        description="La dirección que has introducido no existe o ya no está disponible."
        action-label="Ir al inicio"
        @action="goHome"
      />
    </main>
    <footer class="flex justify-center px-4 pb-6">
      <RouterLink to="/acceso-tecnico" class="text-[13px] text-muted hover:text-brand-700">
        Acceso técnicos
      </RouterLink>
      <span class="mx-2 text-muted">·</span>
      <RouterLink to="/acceso-comercio" class="text-[13px] text-muted hover:text-brand-700">
        Acceso comercios
      </RouterLink>
    </footer>
  </div>
</template>
