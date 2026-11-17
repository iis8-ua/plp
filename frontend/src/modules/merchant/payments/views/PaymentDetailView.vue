<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBalanceStore } from '@/stores/balance.store'
import { usePaymentsStore } from '@/stores/payments.store'
import { useRefundsStore } from '@/stores/refunds.store'
import { useUiStore } from '@/stores/ui.store'
import AppBreadcrumbs from '@/shared/components/layout/AppBreadcrumbs.vue'
import BalanceChips from '@/shared/components/data/BalanceChips.vue'
import Timeline from '@/shared/components/data/Timeline.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import PageErrorState from '@/shared/components/ui/PageErrorState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import RefundRequestDialog from '@/modules/merchant/payments/components/RefundRequestDialog.vue'
import { formatCurrency, formatFullDateTime } from '@/shared/utils/format'

const route = useRoute()
const router = useRouter()
const payments = usePaymentsStore()
const balances = useBalanceStore()
const refunds = useRefundsStore()
const ui = useUiStore()

const refundOpen = ref(false)
const paymentId = computed(() => String(route.params.id ?? ''))
const payment = computed(() => payments.getById(paymentId.value))
const existingRefund = computed(() => (payment.value ? refunds.forPayment(payment.value.id) : undefined))

const title = computed(() => {
  if (!payment.value) return ''
  if (payment.value.status === 'aceptado') return 'Pago correcto'
  return payment.value.reason
})

const canRequest = computed(
  () => payment.value?.status === 'aceptado' && !existingRefund.value,
)

const refundHelper = computed(() => {
  if (existingRefund.value?.status === 'pendiente') return 'Tu solicitud de devolución está pendiente de revisión.'
  if (payment.value?.status === 'rechazado') return 'Solo se pueden devolver pagos aceptados'
  return ''
})

const history = computed(() => [...(payment.value?.history ?? [])])

async function confirmRefund(reason: string): Promise<void> {
  if (!payment.value) return
  try {
    await refunds.request(payment.value, reason)
    refundOpen.value = false
    ui.pushToast('success', 'Solicitud de devolución enviada')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo solicitar la devolución.')
  }
}

onMounted(async () => {
  await Promise.all([balances.load(), payments.load(), refunds.load()])
})
</script>

<template>
  <div class="space-y-6">
    <BalanceChips />

    <div v-if="payments.loading && !payment" class="space-y-4">
      <div class="h-4 w-40 animate-pulse rounded bg-line-soft" />
      <div class="h-72 animate-pulse rounded-lg bg-line-soft" />
    </div>

    <PageErrorState
      v-else-if="!payment"
      title="Pago no encontrado"
      description="No hemos podido localizar este pago o ya no está disponible."
      action-label="Volver al listado"
      @action="router.push('/comercio/pagos')"
    />

    <template v-else>
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <AppBreadcrumbs
          :items="[{ label: 'Pagos', to: '/comercio/pagos' }, { label: `Pago #${payment.id}` }]"
          separator=">"
        />
        <AppButton to="/comercio/pagos" variant="secondary" class="min-w-[212px]">
          Volver al listado
        </AppButton>
      </div>

      <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_392px]">
        <section class="rounded-lg border border-line bg-white p-6">
          <StatusBadge kind="payment" :status="payment.status" size="md" />
          <h2 class="mt-3 text-[20px] font-semibold leading-[1.5] text-ink">{{ title }}</h2>

          <div class="mt-6 grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
            <div>
              <p class="plp-micro">CLIENTE</p>
              <p class="mt-1 text-[14px] font-medium text-ink">{{ payment.client }}</p>
            </div>
            <div>
              <p class="plp-micro">CONCEPTO</p>
              <p class="mt-1 text-[14px] font-medium text-ink">{{ payment.concept }}</p>
            </div>
            <div>
              <p class="plp-micro">FECHA Y HORA</p>
              <p class="mt-1 text-[14px] font-medium text-ink">
                {{ formatFullDateTime(payment.createdAt) }}
              </p>
            </div>
            <div>
              <p class="plp-micro">N.º DE FACTURA DEL COMERCIO</p>
              <p class="mt-1 text-[14px] font-medium text-ink">{{ payment.invoice }}</p>
            </div>
          </div>

          <div class="mt-6 rounded-md bg-app p-4">
            <p class="text-[12px] leading-[1.5] text-muted">Importe total</p>
            <p class="mt-1 text-[20px] font-semibold leading-[1.5] text-ink">
              {{ formatCurrency(payment.amount, payment.currency) }}
            </p>
          </div>
        </section>

        <div class="space-y-6">
          <section class="rounded-lg border border-line bg-white p-6">
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Acciones</h2>

            <AppButton
              v-if="payment.status !== 'rechazado'"
              block
              class="mt-5"
              :disabled="!canRequest"
              @click="refundOpen = true"
            >
              {{ existingRefund?.status === 'pendiente' ? 'Devolución solicitada' : 'Solicitar devolución' }}
            </AppButton>

            <p v-if="refundHelper" class="mt-3 text-[12px] leading-[1.5] text-muted">
              {{ refundHelper }}
            </p>
            <p class="mt-3 text-[12px] leading-[1.5] text-muted">
              La devolución siempre es por el importe total
            </p>
          </section>

          <section class="rounded-lg border border-line bg-white p-6">
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Historial del pago</h2>
            <div class="mt-5">
              <Timeline :entries="history" show-seconds />
            </div>
          </section>
        </div>
      </div>

      <RefundRequestDialog
        :open="refundOpen"
        :payment="payment"
        :loading="refunds.saving"
        @confirm="confirmRefund"
        @cancel="refundOpen = false"
      />
    </template>
  </div>
</template>
