<script setup lang="ts">
import { useBalanceStore } from '@/stores/balance.store'
import AppButton from '@/shared/components/ui/AppButton.vue'
import { formatAmount } from '@/shared/utils/format'

const balanceStore = useBalanceStore()
</script>

<template>
  <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <div class="flex flex-wrap items-center gap-3">
      <span class="text-[13px] font-medium text-muted">Saldo disponible</span>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="balance in balanceStore.balances"
          :key="balance.currency"
          class="flex h-9 items-center gap-1.5 rounded-md border border-line bg-white px-3 text-[12px] leading-none"
        >
          <span class="font-semibold text-ink">{{ balance.currency }}</span>
          <span class="text-secondary">{{ formatAmount(balance.amount) }}</span>
        </div>
      </div>
    </div>
    <AppButton to="/comercio/saldo" variant="secondary" size="sm" class="min-w-[146px]">
      Ver saldo
    </AppButton>
  </div>
</template>
