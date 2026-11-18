<script setup lang="ts">
import { useBalanceStore } from '@/stores/balance.store'
import { formatAmount } from '@/shared/utils/format'
import type { Currency } from '@/types'

withDefaults(defineProps<{ highlight?: Currency; compact?: boolean }>(), {
  highlight: 'EUR',
  compact: false,
})

const store = useBalanceStore()
</script>

<template>
  <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
    <div
      v-for="balance in store.balances"
      :key="balance.currency"
      class="rounded-lg border p-5"
      :class="balance.currency === highlight ? 'border-brand-200 bg-brand-100' : 'border-line bg-white'"
    >
      <p class="text-[14px] font-medium leading-[1.5] text-muted">
        Saldo disponible · {{ balance.currency }}
      </p>
      <p class="mt-2 flex flex-wrap items-baseline gap-1.5 leading-none text-ink">
        <span class="text-[32px] font-semibold leading-[1.2] tracking-[-0.01em]">
          {{ formatAmount(balance.amount) }}
        </span>
        <span class="text-[18px] font-semibold">{{ balance.currency }}</span>
      </p>
      <p class="mt-3 text-[12px] leading-[1.5] text-muted">Disponible para retirar</p>
    </div>
  </div>
</template>
