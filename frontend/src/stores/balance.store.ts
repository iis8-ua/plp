import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { BalanceAccount, Currency } from '@/types'
import { fetchBalances, withdraw as withdrawService } from '@/services/balance.service'

export const useBalanceStore = defineStore('balance', () => {
  const balances = ref<BalanceAccount[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')
  const loaded = ref(false)

  const totalEur = computed(() => balanceFor('EUR'))

  async function load(force = false): Promise<void> {
    if (loaded.value && !force) return
    loading.value = true
    error.value = ''
    try {
      balances.value = await fetchBalances()
      loaded.value = true
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudo cargar el saldo.'
    } finally {
      loading.value = false
    }
  }

  function balanceFor(currency: Currency): number {
    return balances.value.find((balance) => balance.currency === currency)?.amount ?? 0
  }

  async function withdraw(currency: Currency, amount: number): Promise<number> {
    saving.value = true
    error.value = ''
    try {
      const result = await withdrawService(currency, amount)
      const index = balances.value.findIndex((balance) => balance.currency === result.currency)
      if (index >= 0) {
        balances.value[index] = { currency: result.currency, amount: result.balance }
      } else {
        balances.value.push({ currency: result.currency, amount: result.balance })
      }
      return result.balance
    } finally {
      saving.value = false
    }
  }

  return { balances, loading, saving, error, loaded, totalEur, load, balanceFor, withdraw }
})
