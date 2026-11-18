<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBalanceStore } from '@/stores/balance.store'
import { useRefundsStore } from '@/stores/refunds.store'
import { useUiStore } from '@/stores/ui.store'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import DataTable, { type DataColumn } from '@/shared/components/data/DataTable.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppPagination from '@/shared/components/ui/AppPagination.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import EmptyState from '@/shared/components/ui/EmptyState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import AcceptRefundDialog from '@/modules/merchant/refunds/components/AcceptRefundDialog.vue'
import RefundFilters from '@/modules/merchant/refunds/components/RefundFilters.vue'
import { formatCurrency, formatDate, formatTime } from '@/shared/utils/format'
import type { Refund } from '@/types'

const store = useRefundsStore()
const balances = useBalanceStore()
const ui = useUiStore()
const router = useRouter()

const selected = ref<Refund | null>(null)
const confirmOpen = ref(false)

const sortOptions = [
  { value: 'recientes', label: 'Más recientes primero' },
  { value: 'antiguos', label: 'Más antiguos primero' },
  { value: 'importe-desc', label: 'Importe mayor primero' },
]

const columns: DataColumn[] = [
  { key: 'createdAt', label: 'Fecha', class: 'w-[124px]', headerClass: 'w-[124px]' },
  { key: 'paymentId', label: 'ID pago', class: 'w-[120px]', headerClass: 'w-[120px]' },
  { key: 'client', label: 'Cliente', class: 'w-[170px]', headerClass: 'w-[170px]' },
  { key: 'amount', label: 'Importe', class: 'w-[130px]', headerClass: 'w-[130px]' },
  { key: 'reason', label: 'Motivo', class: 'w-[220px]', headerClass: 'w-[220px]' },
  { key: 'status', label: 'Estado', class: 'w-[120px]', headerClass: 'w-[120px]', mobile: false },
  { key: 'actions', label: 'Acciones', class: 'w-[290px]', headerClass: 'w-[290px]' },
]

const empty = computed(() => !store.loading && store.sorted.length === 0)

function openAccept(refund: Refund): void {
  selected.value = refund
  confirmOpen.value = true
}

const available = computed(() =>
  selected.value ? balances.balanceFor(selected.value.currency) : 0,
)

async function confirmAccept(): Promise<void> {
  if (!selected.value) return
  try {
    const amount = selected.value.amount
    const currency = selected.value.currency
    await store.accept(selected.value.id)
    await balances.load(true)
    confirmOpen.value = false
    selected.value = null
    ui.pushToast('success', `Devolución de ${formatCurrency(amount, currency)} aceptada`)
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo aceptar la devolución.')
  }
}

async function confirmReject(): Promise<void> {
  if (!selected.value) return
  try {
    await store.reject(selected.value.id)
    confirmOpen.value = false
    selected.value = null
    ui.pushToast('success', 'Devolución rechazada')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo rechazar la devolución.')
  }
}

onMounted(() => {
  void store.load()
  void balances.load()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Devoluciones"
      description="Gestiona las solicitudes de devolución de tus clientes."
    />

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
      <div class="rounded-lg border border-line bg-white p-5">
        <div class="flex items-start justify-between gap-3">
          <p class="text-[14px] font-medium leading-[1.5] text-muted">Solicitadas</p>
          <span class="rounded-pill bg-warning-bg px-2.5 py-1 text-[11px] font-semibold leading-none text-warning-text">
            Solicitadas
          </span>
        </div>
        <p class="mt-2 text-[32px] font-semibold leading-[1.2] text-ink">{{ store.stats.pendiente }}</p>
        <p class="mt-2 text-[12px] leading-[1.5] text-muted">Pendientes de tu revisión</p>
      </div>
      <div class="rounded-lg border border-line bg-white p-5">
        <div class="flex items-start justify-between gap-3">
          <p class="text-[14px] font-medium leading-[1.5] text-muted">Aceptadas</p>
          <span class="rounded-pill bg-success-bg px-2.5 py-1 text-[11px] font-semibold leading-none text-success-text">
            Aceptadas
          </span>
        </div>
        <p class="mt-2 text-[32px] font-semibold leading-[1.2] text-ink">{{ store.stats.aceptada }}</p>
        <p class="mt-2 text-[12px] leading-[1.5] text-muted">Abonadas al cliente</p>
      </div>
      <div class="rounded-lg border border-line bg-white p-5">
        <div class="flex items-start justify-between gap-3">
          <p class="text-[14px] font-medium leading-[1.5] text-muted">Rechazadas</p>
          <span class="rounded-pill bg-danger-bg px-2.5 py-1 text-[11px] font-semibold leading-none text-danger">
            Rechazadas
          </span>
        </div>
        <p class="mt-2 text-[32px] font-semibold leading-[1.2] text-ink">{{ store.stats.rechazada }}</p>
        <p class="mt-2 text-[12px] leading-[1.5] text-muted">Solicitudes no aprobadas</p>
      </div>
    </div>

    <section class="rounded-lg border border-line bg-white">
      <div class="p-5">
        <RefundFilters />
      </div>

      <div class="flex flex-col gap-3 px-5 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-[13px] font-medium leading-[1.5] text-muted">
          {{ store.sorted.length }} devoluciones
        </p>
        <div class="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
          <AppSelect
            v-model="store.filters.sort"
            :options="sortOptions"
            size="sm"
            class="w-full sm:w-[336px]"
            :ariaLabel="'Ordenar devoluciones'"
          />
        </div>
      </div>

      <EmptyState
        v-if="empty"
        title="No hay devoluciones que coincidan con los filtros"
        description="Prueba con otra búsqueda o restablece los filtros."
        action-label="Limpiar filtros"
        icon="refund"
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
          <template #cell-paymentId="{ row }">
            <span class="text-[13px] font-semibold text-brand-700">{{ row.reference }}</span>
          </template>
          <template #cell-client="{ row }">
            <span class="text-ink">{{ row.client }}</span>
          </template>
          <template #cell-amount="{ row }">
            <span class="font-semibold text-ink">{{ formatCurrency(row.amount, row.currency) }}</span>
          </template>
          <template #cell-reason="{ row }">
            <span class="text-[12px] text-muted">{{ row.reason }}</span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge kind="refund" :status="row.status" />
          </template>
          <template #cell-actions="{ row }">
            <div class="flex justify-end gap-2">
              <template v-if="row.status === 'pendiente'">
                <AppButton size="sm" class="min-w-[118px]" @click="openAccept(row)">Aceptar</AppButton>
                <AppButton
                  variant="secondary"
                  size="sm"
                  class="min-w-[118px]"
                  @click="openAccept(row)"
                >
                  Rechazar
                </AppButton>
              </template>
              <AppButton
                v-else
                variant="secondary"
                size="sm"
                class="min-w-[130px]"
                @click="router.push(`/comercio/pagos/${row.transactionId}`)"
              >
                Ver pago
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
            label="devoluciones"
            @update:page="store.page = $event"
          />
        </div>
      </template>
    </section>

    <AcceptRefundDialog
      :open="confirmOpen"
      :refund="selected"
      :available="available"
      :loading="store.saving"
      @accept="confirmAccept"
      @reject="confirmReject"
      @cancel="confirmOpen = false"
    />
  </div>
</template>
