<script setup lang="ts">
import { onMounted } from 'vue'
import { useBalanceStore } from '@/stores/balance.store'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import BalanceCards from '@/modules/merchant/home/components/BalanceCards.vue'
import WithdrawForm from '@/modules/merchant/balance/components/WithdrawForm.vue'

const store = useBalanceStore()

onMounted(() => {
  void store.load()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Saldo y retirada de fondos"
      description="Retira tu saldo disponible en la moneda que elijas."
    />

    <BalanceCards highlight="EUR" />

    <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_368px]">
      <WithdrawForm />

      <aside class="h-fit rounded-lg border border-line bg-white p-6">
        <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Antes de retirar</h2>
        <p class="mt-3 text-[14px] leading-[1.5] text-secondary">
          Selecciona la moneda y revisa el importe. Solo puedes retirar el saldo disponible en esa
          moneda.
        </p>
        <p class="mt-4 text-[14px] leading-[1.5] text-secondary">
          Siempre te pediremos confirmación antes de descontar el importe de tu saldo.
        </p>
      </aside>
    </div>
  </div>
</template>
