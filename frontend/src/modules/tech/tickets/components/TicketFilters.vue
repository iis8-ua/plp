<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import { useTicketsStore } from '@/stores/tickets.store'

const store = useTicketsStore()

const statusOptions = [
  { value: 'todos', label: 'Todos los estados' },
  { value: 'abierto', label: 'Abierto' },
  { value: 'en-proceso', label: 'En proceso' },
  { value: 'cerrado', label: 'Cerrado' },
]

const dateOptions = [
  { value: 'cualquiera', label: 'Cualquier fecha' },
  { value: 'hoy', label: 'Hoy' },
  { value: '7d', label: 'Últimos 7 días' },
  { value: '30d', label: 'Últimos 30 días' },
]

const companyOptions = computed(() => [
  { value: 'todos', label: 'Todos los comercios' },
  ...store.companies.map((company) => ({ value: company, label: company })),
])

const hasFilters = computed(
  () =>
    Boolean(store.filters.search) ||
    store.filters.status !== 'todos' ||
    store.filters.company !== 'todos' ||
    store.filters.date !== 'cualquiera',
)
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(220px,330px)_192px_196px_200px_146px]">
    <AppInput
      v-model="store.filters.search"
      icon="search"
      placeholder="Buscar por asunto o comercio"
      inputmode="search"
      aria-label="Buscar tickets"
    />
    <AppSelect v-model="store.filters.status" :options="statusOptions" :ariaLabel="'Filtrar por estado'" />
    <AppSelect v-model="store.filters.company" :options="companyOptions" :ariaLabel="'Filtrar por comercio'" />
    <AppSelect v-model="store.filters.date" :options="dateOptions" icon="calendar" :ariaLabel="'Filtrar por fecha'" />
    <AppButton variant="secondary" :disabled="!hasFilters" @click="store.clearFilters()">
      Limpiar
    </AppButton>
  </div>
</template>
