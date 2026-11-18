<script setup lang="ts">
import ConfirmDialog from '@/shared/components/ui/ConfirmDialog.vue'
import type { Company } from '@/types'

withDefaults(
  defineProps<{
    open: boolean
    company: Company | null
    mode: 'deactivate' | 'reactivate'
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <ConfirmDialog
    :open="open"
    :title="
      mode === 'deactivate'
        ? `¿Dar de baja ${company?.name ?? 'este comercio'}?`
        : `¿Reactivar ${company?.name ?? 'este comercio'}?`
    "
    :description="
      mode === 'deactivate'
        ? 'El comercio dejará de tener acceso a PLP. El histórico se conservará.'
        : 'El comercio volverá a tener acceso a PLP.'
    "
    :confirm-label="mode === 'deactivate' ? 'Dar de baja' : 'Reactivar'"
    cancel-label="Cancelar"
    :tone="mode === 'deactivate' ? 'danger' : 'primary'"
    :icon="mode === 'deactivate' ? 'alert-triangle' : 'check'"
    :loading="loading"
    @confirm="emit('confirm')"
    @cancel="emit('cancel')"
  />
</template>
