<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import { useRefundsStore } from '@/stores/refunds.store'

const store = useRefundsStore()

const statusOptions = [
  { value: 'todos', label: 'Todos los estados' },
  { value: 'pendiente', label: 'Solicitada' },
  { value: 'aceptada', label: 'Aceptada' },
  { value: 'rechazada', label: 'Rechazada' },
]

const dateOptions = [
  { value: 'cualquiera', label: 'Cualquier fecha' },
  { value: 'hoy', label: 'Hoy' },
  { value: '7d', label: 'Últimos 7 días' },
  { value: '30d', label: 'Últimos 30 días' },
]

const hasFilters = computed(
  () =>
    Boolean(store.filters.search) ||
    store.filters.status !== 'todos' ||
    store.filters.date !== 'cualquiera',
)
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(240px,1fr)_196px_196px_192px]">
    <AppInput
      v-model="store.filters.search"
      icon="search"
      placeholder="Cliente o ID de pago"
      inputmode="search"
      aria-label="Buscar devoluciones"
    />
    <AppSelect v-model="store.filters.status" :options="statusOptions" :ariaLabel="'Filtrar por estado'" />
    <AppSelect v-model="store.filters.date" :options="dateOptions" icon="calendar" :ariaLabel="'Filtrar por fecha'" />
    <AppButton variant="secondary" :disabled="!hasFilters" @click="store.clearFilters()">
      Limpiar
    </AppButton>
  </div>
</template>
