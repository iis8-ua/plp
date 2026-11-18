<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import { useMerchantsStore } from '@/stores/merchants.store'

const store = useMerchantsStore()

const statusOptions = [
  { value: 'todos', label: 'Todos los estados' },
  { value: 'activo', label: 'Activos' },
  { value: 'dado-de-baja', label: 'Dados de baja' },
]

const sortOptions = [
  { value: 'nombre-az', label: 'Nombre A–Z' },
  { value: 'recientes', label: 'Más recientes' },
]

const hasFilters = computed(
  () => Boolean(store.filters.search) || store.filters.status !== 'todos',
)
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(220px,330px)_224px_224px_146px]">
    <AppInput
      v-model="store.filters.search"
      icon="search"
      placeholder="Buscar por nombre"
      inputmode="search"
      aria-label="Buscar comercios"
    />
    <AppSelect v-model="store.filters.status" :options="statusOptions" :ariaLabel="'Filtrar por estado'" />
    <AppSelect v-model="store.filters.sort" :options="sortOptions" :ariaLabel="'Ordenar comercios'" />
    <AppButton variant="secondary" :disabled="!hasFilters" @click="store.clearFilters()">
      Limpiar
    </AppButton>
  </div>
</template>
