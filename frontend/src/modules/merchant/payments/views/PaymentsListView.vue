<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBalanceStore } from '@/stores/balance.store'
import { usePaymentsStore } from '@/stores/payments.store'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import BalanceChips from '@/shared/components/data/BalanceChips.vue'
import DataTable, { type DataColumn } from '@/shared/components/data/DataTable.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppPagination from '@/shared/components/ui/AppPagination.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import EmptyState from '@/shared/components/ui/EmptyState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import PaymentFilters from '@/modules/merchant/payments/components/PaymentFilters.vue'
import { formatCurrency, formatDate, formatTime } from '@/shared/utils/format'

const store = usePaymentsStore()
const balances = useBalanceStore()
const router = useRouter()

const sortOptions = [
  { value: 'recientes', label: 'Más recientes primero' },
  { value: 'antiguos', label: 'Más antiguos primero' },
  { value: 'importe-desc', label: 'Importe mayor primero' },
]

const columns: DataColumn[] = [
  { key: 'createdAt', label: 'Fecha', class: 'w-[124px]', headerClass: 'w-[124px]' },
  { key: 'client', label: 'Cliente', class: 'w-[200px]', headerClass: 'w-[200px]' },
  { key: 'concept', label: 'Concepto' },
  { key: 'amount', label: 'Importe', class: 'w-[130px]', headerClass: 'w-[130px]' },
  { key: 'status', label: 'Estado', class: 'w-[120px]', headerClass: 'w-[120px]' },
  { key: 'reason', label: 'Motivo', class: 'w-[190px]', headerClass: 'w-[190px]' },
  { key: 'actions', label: 'Acciones', class: 'w-[100px]', headerClass: 'w-[100px]' },
]

const empty = computed(() => !store.loading && store.sorted.length === 0)

const reasonClass = (status: string): string => {
  if (status === 'rechazado') return 'text-danger'
  if (status === 'pendiente') return 'text-warning-text'
  return 'text-muted'
}

onMounted(() => {
  void balances.load()
  void store.load()
})
</script>

<template>
  <div class="space-y-6">
    <BalanceChips />

    <PageHeader
      title="Pagos recibidos"
      description="Consulta el estado, el motivo y el importe de cada operación."
    />

    <section class="rounded-lg border border-line bg-white">
      <div class="p-5">
        <PaymentFilters />
      </div>

      <div class="flex flex-col gap-3 px-5 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-[13px] font-medium leading-[1.5] text-muted">{{ store.sorted.length }} pagos</p>
        <div class="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
          <AppSelect
            v-model="store.filters.sort"
            :options="sortOptions"
            size="sm"
            class="w-full sm:w-[360px]"
            :ariaLabel="'Ordenar pagos'"
          />
        </div>
      </div>

      <EmptyState
        v-if="empty"
        title="No hay pagos que coincidan con los filtros"
        description="Prueba con otra búsqueda o restablece los filtros."
        action-label="Limpiar filtros"
        icon="search"
        @action="store.clearFilters()"
      />

      <template v-else>
        <DataTable :columns="columns" :rows="store.paginated" :loading="store.loading" :skeleton-rows="5">
          <template #cell-createdAt="{ row }">
            <div class="text-[12px] leading-[1.5] text-muted">
              <p>{{ formatDate(row.createdAt) }}</p>
              <p>{{ formatTime(row.createdAt).slice(0, 5) }}</p>
            </div>
          </template>
          <template #cell-client="{ row }">
            <div>
              <p class="font-semibold text-ink">{{ row.client }}</p>
              <p class="text-[12px] leading-[1.5] text-muted">{{ row.invoice }}</p>
            </div>
          </template>
          <template #cell-amount="{ row }">
            <span class="font-semibold text-ink">{{ formatCurrency(row.amount, row.currency) }}</span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge kind="payment" :status="row.status" />
          </template>
          <template #cell-reason="{ row }">
            <span class="text-[12px]" :class="reasonClass(row.status)">{{ row.reason }}</span>
          </template>
          <template #cell-actions="{ row }">
            <div class="flex justify-end">
              <AppButton
                variant="neutral"
                size="sm"
                class="min-w-14"
                @click="router.push(`/comercio/pagos/${row.id}`)"
              >
                Ver
              </AppButton>
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
            label="pagos"
            @update:page="store.page = $event"
          />
        </div>
      </template>
    </section>
  </div>
</template>
