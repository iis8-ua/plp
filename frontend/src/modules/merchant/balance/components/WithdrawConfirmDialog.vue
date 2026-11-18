<script setup lang="ts">
import { computed } from 'vue'
import ConfirmDialog from '@/shared/components/ui/ConfirmDialog.vue'
import { formatCurrency } from '@/shared/utils/format'
import type { Currency } from '@/types'

const props = withDefaults(
  defineProps<{
    open: boolean
    currency: Currency
    amount: number
    available: number
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()
const remaining = computed(() => Math.max(0, props.available - props.amount))
</script>

<template>
  <ConfirmDialog
    :open="open"
    :title="`¿Retirar ${formatCurrency(amount, currency)}?`"
    description="Revisa los importes antes de confirmar la retirada."
    confirm-label="Confirmar retirada"
    cancel-label="Cancelar"
    tone="primary"
    icon="wallet"
    size="lg"
    :loading="loading"
    @confirm="emit('confirm')"
    @cancel="emit('cancel')"
  >
    <div class="mt-5 rounded-lg border border-line bg-app p-4">
      <div class="flex items-center justify-between gap-4 py-1 text-[13px]">
        <span class="text-muted">Saldo disponible</span>
        <span class="font-semibold text-ink">{{ formatCurrency(available, currency) }}</span>
      </div>
      <div class="flex items-center justify-between gap-4 py-1 text-[13px]">
        <span class="text-muted">Importe a retirar</span>
        <span class="font-semibold text-ink">{{ formatCurrency(amount, currency) }}</span>
      </div>
      <div class="mt-2 flex items-center justify-between gap-4 border-t border-line pt-3 text-[14px]">
        <span class="font-medium text-ink">Saldo resultante</span>
        <span class="font-semibold text-success-text">{{ formatCurrency(remaining, currency) }}</span>
      </div>
    </div>
    <p class="mt-3 text-[12px] leading-[1.5] text-muted">
      El importe se descontará de tu saldo disponible.
    </p>
  </ConfirmDialog>
</template>
