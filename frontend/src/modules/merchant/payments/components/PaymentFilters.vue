<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import { CURRENCY_OPTIONS } from '@/shared/utils/status'
import { usePaymentsStore } from '@/stores/payments.store'

const store = usePaymentsStore()

const statusOptions = [
  { value: 'todos', label: 'Todos los estados' },
  { value: 'aceptado', label: 'Aceptado' },
  { value: 'rechazado', label: 'Rechazado' },
  { value: 'pendiente', label: 'Pendiente' },
  { value: 'reembolsado', label: 'Reembolsado' },
]

const currencyOptions = [{ value: 'todas', label: 'Todas las monedas' }, ...CURRENCY_OPTIONS]

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
    store.filters.currency !== 'todas' ||
    store.filters.date !== 'cualquiera',
)
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(220px,330px)_192px_192px_200px_146px]">
    <AppInput
      v-model="store.filters.search"
      icon="search"
      placeholder="Cliente, concepto o factura"
      inputmode="search"
      aria-label="Buscar pagos"
    />
    <AppSelect v-model="store.filters.status" :options="statusOptions" :ariaLabel="'Filtrar por estado'" />
    <AppSelect v-model="store.filters.currency" :options="currencyOptions" :ariaLabel="'Filtrar por moneda'" />
    <AppSelect v-model="store.filters.date" :options="dateOptions" icon="calendar" :ariaLabel="'Filtrar por fecha'" />
    <AppButton variant="secondary" :disabled="!hasFilters" @click="store.clearFilters()">
      Limpiar
    </AppButton>
  </div>
</template>
