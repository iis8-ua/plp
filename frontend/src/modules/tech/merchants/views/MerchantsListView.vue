<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useMerchantsStore } from '@/stores/merchants.store'
import { useUiStore } from '@/stores/ui.store'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import DataTable, { type DataColumn } from '@/shared/components/data/DataTable.vue'
import StatCard from '@/shared/components/data/StatCard.vue'
import AppAvatar from '@/shared/components/ui/AppAvatar.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import AppPagination from '@/shared/components/ui/AppPagination.vue'
import EmptyState from '@/shared/components/ui/EmptyState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import ConfirmMerchantDialog from '@/modules/tech/merchants/components/ConfirmMerchantDialog.vue'
import MerchantActionsMenu from '@/modules/tech/merchants/components/MerchantActionsMenu.vue'
import MerchantFilters from '@/modules/tech/merchants/components/MerchantFilters.vue'
import MerchantFormModal from '@/modules/tech/merchants/components/MerchantFormModal.vue'
import { formatDate } from '@/shared/utils/format'
import type { Company } from '@/types'

const store = useMerchantsStore()
const ui = useUiStore()

const createOpen = ref(false)
const confirmOpen = ref(false)
const selected = ref<Company | null>(null)
const mode = ref<'deactivate' | 'reactivate'>('deactivate')

const columns: DataColumn[] = [
  { key: 'name', label: 'Nombre del comercio' },
  { key: 'id', label: 'ID', class: 'w-[180px]', headerClass: 'w-[180px]' },
  { key: 'registeredAt', label: 'Fecha de registro', class: 'w-[220px]', headerClass: 'w-[220px]', mobile: false },
  { key: 'status', label: 'Estado', class: 'w-[180px]', headerClass: 'w-[180px]' },
  { key: 'actions', label: 'Acciones', class: 'w-[112px]', headerClass: 'w-[112px]' },
]

const sortLabel = computed(() =>
  store.filters.sort === 'recientes' ? 'Más recientes primero' : 'Orden alfabético por nombre',
)

const noResults = computed(
  () => !store.loading && store.companies.length > 0 && store.sorted.length === 0,
)

function onCreated(company: Company): void {
  store.filters.search = ''
  store.filters.status = 'todos'
  store.filters.sort = 'recientes'
  store.page = 1
  ui.pushToast('success', `Comercio ${company.name} creado correctamente`)
}

function askDeactivate(company: Company): void {
  selected.value = company
  mode.value = 'deactivate'
  confirmOpen.value = true
}

function askReactivate(company: Company): void {
  selected.value = company
  mode.value = 'reactivate'
  confirmOpen.value = true
}

async function confirmAction(): Promise<void> {
  if (!selected.value) return
  try {
    if (mode.value === 'deactivate') {
      await store.deactivateCompany(selected.value)
      ui.pushToast('success', 'Comercio dado de baja correctamente')
    } else {
      await store.reactivate(selected.value)
      ui.pushToast('success', 'Comercio reactivado correctamente')
    }
    confirmOpen.value = false
    selected.value = null
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo completar la acción.')
  }
}

onMounted(() => {
  void store.load()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Comercios"
      description="Da de alta comercios y gestiona su acceso a PLP."
    >
      <template #actions>
        <AppButton @click="createOpen = true">
          <AppIcon name="plus" :size="18" /> Nuevo comercio
        </AppButton>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
      <StatCard label="Total de comercios" :value="store.stats.total" context="Registrados en la plataforma" tone="brand" />
      <StatCard label="Activos" :value="store.stats.activo" context="Con acceso a PLP" tone="success" />
      <StatCard label="Dados de baja" :value="store.stats['dado-de-baja']" context="Histórico conservado" tone="neutral" />
    </div>

    <section
      v-if="!store.loading && store.companies.length === 0"
      class="rounded-lg border border-line bg-white"
    >
      <EmptyState
        title="Aún no hay comercios. Crea el primero"
        description="Da de alta un comercio para que pueda empezar a operar con PLP."
        action-label="+ Nuevo comercio"
        icon="shop"
        @action="createOpen = true"
      />
    </section>

    <section v-else class="rounded-lg border border-line bg-white">
      <div class="p-5">
        <MerchantFilters />
      </div>

      <div class="flex flex-col gap-2 px-5 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-[13px] font-medium leading-[1.5] text-muted">
          {{ store.sorted.length }} comercios
        </p>
        <p class="text-[12px] leading-[1.5] text-muted">{{ sortLabel }}</p>
      </div>

      <EmptyState
        v-if="noResults"
        title="No hay comercios que coincidan con los filtros"
        description="Prueba con otra búsqueda o restablece los filtros."
        action-label="Limpiar filtros"
        icon="search"
        @action="store.clearFilters()"
      />

      <template v-else>
        <DataTable
          :columns="columns"
          :rows="store.paginated"
          :loading="store.loading"
          :skeleton-rows="7"
        >
          <template #cell-name="{ row }">
            <div class="flex items-center gap-3">
              <AppAvatar
                :name="row.name"
                :size="32"
                shape="square"
                :tone="row.status === 'activo' ? 'brand' : 'neutral'"
              />
              <span class="truncate font-medium text-ink">{{ row.name }}</span>
            </div>
          </template>
          <template #cell-id="{ row }">
            <span class="text-[12px] text-muted">{{ row.id }}</span>
          </template>
          <template #cell-registeredAt="{ row }">
            <span class="text-[12px] text-muted">{{ formatDate(row.registeredAt) }}</span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge kind="company" :status="row.status" />
          </template>
          <template #cell-actions="{ row }">
            <div class="flex justify-end">
              <MerchantActionsMenu
                :company="row"
                @deactivate="askDeactivate"
                @reactivate="askReactivate"
              />
            </div>
          </template>
        </DataTable>

        <div class="border-t border-line px-5 py-4">
          <AppPagination
            :page="store.page"
            :total-pages="store.totalPages"
            :range-start="store.rangeStart"
            :range-end="store.rangeEnd"
            :total="store.sorted.length"
            label="comercios"
            @update:page="store.page = $event"
          />
        </div>
      </template>
    </section>

    <MerchantFormModal :open="createOpen" @close="createOpen = false" @created="onCreated" />
    <ConfirmMerchantDialog
      :open="confirmOpen"
      :company="selected"
      :mode="mode"
      :loading="store.saving"
      @confirm="confirmAction"
      @cancel="confirmOpen = false"
    />
  </div>
</template>
