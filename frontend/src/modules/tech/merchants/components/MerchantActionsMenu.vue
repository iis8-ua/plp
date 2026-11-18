<script setup lang="ts">
import { computed } from 'vue'
import ActionMenu from '@/shared/components/ui/ActionMenu.vue'
import type { Company } from '@/types'

const props = defineProps<{ company: Company }>()
const emit = defineEmits<{ deactivate: [company: Company]; reactivate: [company: Company] }>()

const items = computed(() =>
  props.company.status === 'activo'
    ? [{ key: 'deactivate', label: 'Dar de baja', tone: 'danger' as const }]
    : [{ key: 'reactivate', label: 'Reactivar', tone: 'primary' as const }],
)
</script>

<template>
  <ActionMenu
    :items="items"
    :header="company.name"
    :ariaLabel="`Acciones de ${company.name}`"
    :width="176"
    @select="
      (key) => {
        if (key === 'deactivate') emit('deactivate', company)
        if (key === 'reactivate') emit('reactivate', company)
      }
    "
  />
</template>
