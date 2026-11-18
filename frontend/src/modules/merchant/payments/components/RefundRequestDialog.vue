<script setup lang="ts">
import { ref, watch } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import AppTextarea from '@/shared/components/ui/AppTextarea.vue'
import { formatCurrency, formatFullDateTime } from '@/shared/utils/format'
import type { Payment } from '@/types'

const props = withDefaults(
  defineProps<{
    open: boolean
    payment: Payment | null
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ confirm: [reason: string]; cancel: [] }>()

const reason = ref('')

watch(
  () => props.open,
  (open) => {
    if (open) reason.value = ''
  },
)
</script>

<template>
  <AppModal
    :open="open"
    size="lg"
    hide-header
    :close-on-overlay="!loading"
    @close="emit('cancel')"
  >
    <template v-if="payment">
      <h2 class="text-[24px] font-semibold leading-[1.5] text-ink">Solicitar devolución</h2>
      <p class="mt-1 text-[14px] leading-[1.5] text-muted">
        Revisa los datos del pago antes de solicitar la devolución.
      </p>

      <div class="mt-6 rounded-lg border border-line p-5">
        <div class="grid grid-cols-1 gap-x-8 gap-y-4 sm:grid-cols-2">
          <div>
            <p class="text-[12px] leading-[1.5] text-muted">Cliente</p>
            <p class="mt-0.5 text-[14px] font-medium leading-[1.5] text-ink">{{ payment.client }}</p>
          </div>
          <div>
            <p class="text-[12px] leading-[1.5] text-muted">Concepto</p>
            <p class="mt-0.5 text-[14px] font-medium leading-[1.5] text-ink">{{ payment.concept }}</p>
          </div>
          <div>
            <p class="text-[12px] leading-[1.5] text-muted">Fecha</p>
            <p class="mt-0.5 text-[14px] font-medium leading-[1.5] text-ink">
              {{ formatFullDateTime(payment.createdAt) }}
            </p>
          </div>
          <div>
            <p class="text-[12px] leading-[1.5] text-muted">Factura</p>
            <p class="mt-0.5 text-[14px] font-medium leading-[1.5] text-ink">{{ payment.invoice }}</p>
          </div>
        </div>
      </div>

      <div class="mt-4 rounded-lg bg-app px-5 py-4">
        <p class="text-[12px] leading-[1.5] text-muted">Importe total</p>
        <p class="mt-1 text-[28px] font-semibold leading-[1.2] text-ink">
          {{ formatCurrency(payment.amount, payment.currency) }}
        </p>
        <p class="mt-1 text-[12px] leading-[1.5] text-muted">
          La devolución siempre es por el importe total
        </p>
      </div>

      <div class="mt-6">
        <AppTextarea
          v-model="reason"
          label="Motivo (opcional)"
          placeholder="Describe el motivo de la devolución"
          :rows="3"
        />
      </div>

      <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-[200px_minmax(0,1fr)]">
        <AppButton variant="secondary" :disabled="loading" @click="emit('cancel')">
          Cancelar
        </AppButton>
        <AppButton :loading="loading" @click="emit('confirm', reason)">
          Solicitar devolución
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
