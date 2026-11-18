<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import AuthCard from '@/shared/components/layout/AuthCard.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'

const route = useRoute()
const portal = computed(() => (route.query.portal === 'comercio' ? 'comercio' : 'tecnico'))
const copy = computed(() =>
  portal.value === 'comercio'
    ? {
        portalLabel: 'PORTAL DE COMERCIOS',
        footer: 'Gestiona tus cobros, sin complicaciones.',
        message: 'Has salido del portal de comercios de forma segura.',
        to: '/acceso-comercio',
        button: 'Volver a iniciar sesión',
      }
    : {
        portalLabel: 'PORTAL DE SOPORTE',
        footer: 'Soporte de pagos, sin complicaciones.',
        message: 'Has salido del portal de soporte de forma segura.',
        to: '/acceso-tecnico',
        button: 'Volver a iniciar sesión',
      },
)
</script>

<template>
  <AuthLayout :portal-label="copy.portalLabel" :footer-message="copy.footer" centered>
    <AuthCard compact>
      <h1 class="text-[28px] font-semibold leading-[1.5] text-ink">Sesión cerrada</h1>
      <p class="mt-2 text-[14px] leading-[1.5] text-muted">{{ copy.message }}</p>
      <AppButton :to="copy.to" size="lg" block class="mt-8">{{ copy.button }}</AppButton>
    </AuthCard>
  </AuthLayout>
</template>
