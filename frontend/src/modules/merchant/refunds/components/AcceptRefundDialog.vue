<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import { formatCurrency } from '@/shared/utils/format'
import type { Refund } from '@/types'

const props = withDefaults(
  defineProps<{
    open: boolean
    refund: Refund | null
    available: number
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ accept: []; reject: []; cancel: [] }>()

const remaining = computed(() =>
  props.refund ? Math.max(0, props.available - props.refund.amount) : 0,
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
    <template v-if="refund">
      <h2 class="text-[24px] font-semibold leading-[1.5] text-ink">
        ¿Aceptar la devolución de {{ formatCurrency(refund.amount, refund.currency) }}?
      </h2>

      <div class="mt-6 rounded-lg bg-brand-100 px-5 py-4 text-[14px] leading-[1.5] text-brand-700">
        Se abonará a la tarjeta del cliente y se descontará de tu saldo.
      </div>

      <div class="mt-4 rounded-lg border border-line p-4">
        <div class="flex items-center justify-between gap-4 py-1 text-[13px]">
          <span class="text-muted">Saldo actual</span>
          <span class="font-semibold text-ink">{{ formatCurrency(available, refund.currency) }}</span>
        </div>
        <div class="flex items-center justify-between gap-4 py-1 text-[13px]">
          <span class="text-muted">Importe de la devolución</span>
          <span class="font-semibold text-ink">
            −{{ formatCurrency(refund.amount, refund.currency) }}
          </span>
        </div>
        <div class="mt-2 flex items-center justify-between gap-4 border-t border-line pt-3 text-[14px]">
          <span class="font-medium text-ink">Saldo resultante</span>
          <span class="font-semibold text-brand-700">
            {{ formatCurrency(remaining, refund.currency) }}
          </span>
        </div>
      </div>

      <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <AppButton variant="secondary" :disabled="loading" @click="emit('cancel')">
          Cancelar
        </AppButton>
        <AppButton variant="secondary" :disabled="loading" @click="emit('reject')">
          Rechazar
        </AppButton>
        <AppButton :loading="loading" @click="emit('accept')">Aceptar</AppButton>
      </div>
    </template>
  </AppModal>
</template>
