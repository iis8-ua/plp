<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useBalanceStore } from '@/stores/balance.store'
import { useUiStore } from '@/stores/ui.store'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import InlineAlert from '@/shared/components/ui/InlineAlert.vue'
import WithdrawConfirmDialog from '@/modules/merchant/balance/components/WithdrawConfirmDialog.vue'
import { formatAmount, formatCurrency } from '@/shared/utils/format'
import { CURRENCY_OPTIONS } from '@/shared/utils/status'
import type { Currency } from '@/types'

const store = useBalanceStore()
const ui = useUiStore()

const currency = ref<Currency>('EUR')
const amountText = ref('')
const error = ref('')
const actionError = ref('')
const confirmOpen = ref(false)

const available = computed(() => store.balanceFor(currency.value))
const amount = computed(() => parseAmount(amountText.value))

function parseAmount(value: string): number {
  const normalized = value
    .trim()
    .replace(/\s/g, '')
    .replace(/\.(?=\d{3}\b)/g, '')
    .replace(',', '.')
  return Number(normalized)
}

function setAll(): void {
  amountText.value = formatAmount(available.value)
  error.value = ''
  actionError.value = ''
}

function validate(): boolean {
  if (!amountText.value.trim() || Number.isNaN(amount.value) || amount.value <= 0) {
    error.value = 'El importe no es válido'
    return false
  }
  if (amount.value > available.value) {
    error.value = 'El importe supera tu saldo disponible'
    return false
  }
  error.value = ''
  return true
}

function submit(): void {
  actionError.value = ''
  if (!validate()) return
  confirmOpen.value = true
}

async function confirm(): Promise<void> {
  try {
    const newBalance = await store.withdraw(currency.value, amount.value)
    confirmOpen.value = false
    amountText.value = ''
    actionError.value = ''
    ui.pushToast(
      'success',
      `Retirada realizada. Tu nuevo saldo es ${formatCurrency(newBalance, currency.value)}`,
    )
  } catch (cause) {
    confirmOpen.value = false
    actionError.value =
      cause instanceof Error ? cause.message : 'No se ha podido completar la acción. Inténtalo de nuevo'
  }
}

watch(currency, () => {
  amountText.value = ''
  error.value = ''
  actionError.value = ''
})
</script>

<template>
  <section class="rounded-lg border border-line bg-white p-6">
    <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Retirar fondos</h2>

    <div class="mt-5 space-y-4">
      <AppSelect
        v-model="currency"
        :options="CURRENCY_OPTIONS"
        label="Moneda"
        :ariaLabel="'Moneda de la retirada'"
      />

      <div>
        <AppInput
          v-model="amountText"
          label="Importe a retirar"
          placeholder="0,00"
          inputmode="decimal"
          :suffix="currency"
          :invalid="Boolean(error)"
          @update:model-value="error = ''; actionError = ''"
        />
        <div class="mt-2 flex items-center justify-between gap-4">
          <p class="text-[12px] leading-[1.5] text-muted">
            Disponible: {{ formatCurrency(available, currency) }}
          </p>
          <button
            type="button"
            class="text-[13px] font-semibold text-brand-700 hover:underline"
            @click="setAll"
          >
            Retirar todo
          </button>
        </div>
        <p v-if="error" class="mt-2 text-[12px] leading-[1.5] text-danger">{{ error }}</p>
      </div>

      <InlineAlert v-if="actionError" tone="error" @dismiss="actionError = ''">
        {{ actionError }}
      </InlineAlert>

      <AppButton block :loading="store.saving" @click="submit">Retirar</AppButton>
    </div>

    <WithdrawConfirmDialog
      :open="confirmOpen"
      :currency="currency"
      :amount="amount"
      :available="available"
      :loading="store.saving"
      @confirm="confirm"
      @cancel="confirmOpen = false"
    />
  </section>
</template>
