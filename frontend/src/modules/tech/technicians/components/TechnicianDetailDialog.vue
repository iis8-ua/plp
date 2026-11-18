<script setup lang="ts">
import AppModal from '@/shared/components/ui/AppModal.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import type { Technician } from '@/types'

defineProps<{
  open: boolean
  technician: Technician | null
}>()

const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <AppModal :open="open" size="sm" title="Perfil del técnico" @close="emit('close')">
    <template v-if="technician">
      <div class="space-y-4">
        <div>
          <p class="plp-micro">NOMBRE</p>
          <p class="mt-1 text-[14px] font-medium text-ink">{{ technician.name }}</p>
        </div>
        <div>
          <p class="plp-micro">CORREO</p>
          <p class="mt-1 text-[14px] font-medium text-ink">{{ technician.email }}</p>
        </div>
        <div>
          <p class="plp-micro">USUARIO</p>
          <p class="mt-1 text-[14px] font-medium text-ink">{{ technician.username }}</p>
        </div>
        <div class="flex items-center justify-between gap-4">
          <div>
            <p class="plp-micro">ROL</p>
            <p class="mt-1 text-[14px] font-medium text-ink">Técnico</p>
          </div>
          <div class="text-right">
            <p class="plp-micro">ESTADO</p>
            <p class="mt-1">
              <StatusBadge
                kind="company"
                :status="technician.status === 'Activo' ? 'activo' : 'dado-de-baja'"
              />
            </p>
          </div>
        </div>
      </div>

      <div class="mt-6 grid grid-cols-3 gap-3 rounded-lg bg-app p-4 text-center">
        <div>
          <p class="text-[20px] font-semibold text-brand-700">{{ technician.activity.assigned }}</p>
          <p class="text-[11px] leading-[1.5] text-muted">Asignados</p>
        </div>
        <div>
          <p class="text-[20px] font-semibold text-brand-700">{{ technician.activity.in_progress }}</p>
          <p class="text-[11px] leading-[1.5] text-muted">En proceso</p>
        </div>
        <div>
          <p class="text-[20px] font-semibold text-success-text">{{ technician.activity.closed }}</p>
          <p class="text-[11px] leading-[1.5] text-muted">Cerrados</p>
        </div>
      </div>
    </template>
  </AppModal>
</template>
