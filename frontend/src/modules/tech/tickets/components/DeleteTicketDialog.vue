<script setup lang="ts">
import ConfirmDialog from '@/shared/components/ui/ConfirmDialog.vue'

withDefaults(
  defineProps<{
    open: boolean
    ticketId: string
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <ConfirmDialog
    :open="open"
    :title="`¿Eliminar ticket #${ticketId}?`"
    description="Esta acción no se puede deshacer"
    confirm-label="Eliminar"
    cancel-label="Cancelar"
    tone="danger"
    icon="alert-triangle"
    :loading="loading"
    @confirm="emit('confirm')"
    @cancel="emit('cancel')"
  />
</template>
