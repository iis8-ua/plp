<script setup lang="ts">
import { computed } from 'vue'
import ConfirmDialog from '@/shared/components/ui/ConfirmDialog.vue'
import type { Technician } from '@/types'

const props = withDefaults(
  defineProps<{
    open: boolean
    technician: Technician | null
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()

const deactivating = computed(() => props.technician?.status === 'Activo')

const title = computed(() => {
  if (!props.technician) return ''
  return deactivating.value
    ? `¿Desactivar a ${props.technician.name}?`
    : `¿Reactivar a ${props.technician.name}?`
})

const description = computed(() =>
  deactivating.value
    ? 'El técnico dejará de poder iniciar sesión y se invalidarán sus tokens. Podrás reactivarlo más adelante.'
    : 'El técnico volverá a poder iniciar sesión con su cuenta.',
)
</script>

<template>
  <ConfirmDialog
    :open="open"
    :title="title"
    :description="description"
    :confirm-label="deactivating ? 'Desactivar' : 'Activar'"
    cancel-label="Cancelar"
    :tone="deactivating ? 'danger' : 'primary'"
    icon="ban"
    :loading="loading"
    @confirm="emit('confirm')"
    @cancel="emit('cancel')"
  />
</template>
