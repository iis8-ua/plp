<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useBalanceStore } from '@/stores/balance.store'
import { usePaymentsStore } from '@/stores/payments.store'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import DataTable, { type DataColumn } from '@/shared/components/data/DataTable.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import BalanceCards from '@/modules/merchant/home/components/BalanceCards.vue'
import PaymentSummary from '@/modules/merchant/home/components/PaymentSummary.vue'
import { formatCurrency, formatDateTime, formatFullDateTime } from '@/shared/utils/format'
import type { Payment } from '@/types'

const auth = useAuthStore()
const balances = useBalanceStore()
const payments = usePaymentsStore()

const latest = computed<Payment[]>(() =>
  [...payments.payments].sort((a, b) => b.createdAt.localeCompare(a.createdAt)).slice(0, 5),
)

const updatedAt = computed(() => latest.value[0]?.createdAt ?? '')

const columns: DataColumn[] = [
  { key: 'client', label: 'Cliente' },
  { key: 'amount', label: 'Importe', class: 'w-[180px]', headerClass: 'w-[180px]' },
  { key: 'status', label: 'Estado', class: 'w-[180px]', headerClass: 'w-[180px]' },
  { key: 'createdAt', label: 'Fecha', class: 'w-[180px]', headerClass: 'w-[180px]' },
]

onMounted(() => {
  void balances.load()
  void payments.load()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      :title="`Hola, ${auth.user?.name ?? 'comercio'}`"
      description="Consulta tus cobros y gestiona el saldo de tu comercio."
    >
      <template #actions>
        <AppButton to="/comercio/saldo">Retirar fondos</AppButton>
      </template>
    </PageHeader>

    <BalanceCards highlight="EUR" />

    <PaymentSummary
      :accepted="payments.stats.aceptado"
      :rejected="payments.stats.rechazado"
      :total="payments.stats.total"
    />

    <section class="rounded-lg border border-line bg-white">
      <div class="flex items-center justify-between gap-4 px-5 py-4">
        <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Últimos pagos</h2>
        <RouterLink to="/comercio/pagos" class="text-[14px] font-semibold text-brand-700 hover:underline">
          Ver todos los pagos
        </RouterLink>
      </div>

      <div v-if="!payments.loading && payments.payments.length === 0" class="px-6 py-14 text-center">
        <h3 class="text-[20px] font-semibold leading-[1.5] text-ink">Aún sin pagos</h3>
        <p class="mt-2 text-[14px] leading-[1.5] text-muted">
          Cuando recibas tu primer pago, aparecerá aquí.
        </p>
      </div>

      <template v-else>
        <DataTable :columns="columns" :rows="latest" :loading="payments.loading" :skeleton-rows="5">
          <template #cell-client="{ row }">
            <div>
              <p class="font-semibold text-ink">{{ row.client }}</p>
              <p class="text-[12px] text-muted">{{ row.invoice }}</p>
            </div>
          </template>
          <template #cell-amount="{ row }">
            <span class="font-semibold text-ink">{{ formatCurrency(row.amount, row.currency) }}</span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge kind="payment" :status="row.status" />
          </template>
          <template #cell-createdAt="{ row }">
            <span class="text-[12px] text-muted">{{ formatDateTime(row.createdAt) }}</span>
          </template>
        </DataTable>
      </template>

      <div v-if="updatedAt" class="border-t border-line px-5 py-3">
        <p class="text-[12px] leading-[1.5] text-muted">
          Actualizado el {{ formatFullDateTime(updatedAt) }}
        </p>
      </div>
    </section>
  </div>
</template>
