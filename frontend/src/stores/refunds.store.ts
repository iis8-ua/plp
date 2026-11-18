import { computed, reactive, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Payment, Refund, RefundFilters } from '@/types'
import { acceptRefund, fetchRefunds, rejectRefund, requestRefund } from '@/services/refunds.service'
import { isWithinDays } from '@/shared/utils/format'

const DEFAULT_FILTERS: RefundFilters = {
  search: '',
  status: 'todos',
  date: 'cualquiera',
  sort: 'recientes',
}

function todayISODate(): string {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

export const useRefundsStore = defineStore('refunds', () => {
  const refunds = ref<Refund[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')
  const loaded = ref(false)
  const filters = reactive<RefundFilters>({ ...DEFAULT_FILTERS })
  const page = ref(1)
  const perPage = ref(5)

  const stats = computed(() => ({
    total: refunds.value.length,
    pendiente: refunds.value.filter((refund) => refund.status === 'pendiente').length,
    aceptada: refunds.value.filter((refund) => refund.status === 'aceptada').length,
    rechazada: refunds.value.filter((refund) => refund.status === 'rechazada').length,
  }))

  const filtered = computed(() => {
    const search = filters.search.trim().toLowerCase()
    const today = todayISODate()
    return refunds.value.filter((refund) => {
      if (filters.status !== 'todos' && refund.status !== filters.status) return false
      if (filters.date === 'hoy' && !refund.createdAt.startsWith(today)) return false
      if (filters.date === '7d' && !isWithinDays(refund.createdAt, 7)) return false
      if (filters.date === '30d' && !isWithinDays(refund.createdAt, 30)) return false
      if (!search) return true
      return (
        refund.client.toLowerCase().includes(search) ||
        refund.reference.toLowerCase().includes(search) ||
        refund.transactionId.toLowerCase().includes(search) ||
        refund.id.toLowerCase().includes(search)
      )
    })
  })

  const sorted = computed(() => {
    const list = [...filtered.value]
    if (filters.sort === 'antiguos') return list.sort((a, b) => a.createdAt.localeCompare(b.createdAt))
    if (filters.sort === 'importe-desc') return list.sort((a, b) => b.amount - a.amount)
    return list.sort((a, b) => b.createdAt.localeCompare(a.createdAt))
  })

  const totalPages = computed(() => Math.max(1, Math.ceil(sorted.value.length / perPage.value)))
  const paginated = computed(() => {
    const start = (page.value - 1) * perPage.value
    return sorted.value.slice(start, start + perPage.value)
  })
  const rangeStart = computed(() =>
    sorted.value.length === 0 ? 0 : (page.value - 1) * perPage.value + 1,
  )
  const rangeEnd = computed(() => Math.min(page.value * perPage.value, sorted.value.length))

  watch(
    () => ({ ...filters }),
    () => {
      page.value = 1
    },
    { deep: true },
  )

  watch(totalPages, (value) => {
    if (page.value > value) page.value = value
  })

  async function load(force = false): Promise<void> {
    if (loaded.value && !force) return
    loading.value = true
    error.value = ''
    try {
      refunds.value = await fetchRefunds()
      loaded.value = true
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudieron cargar las devoluciones.'
    } finally {
      loading.value = false
    }
  }

  function replace(refund: Refund): void {
    const index = refunds.value.findIndex((candidate) => candidate.id === refund.id)
    if (index >= 0) refunds.value[index] = refund
  }

  async function request(payment: Payment, reason = ''): Promise<Refund> {
    saving.value = true
    error.value = ''
    try {
      const refund = await requestRefund(payment, reason)
      refunds.value = [refund, ...refunds.value]
      return refund
    } finally {
      saving.value = false
    }
  }

  async function accept(refundId: string): Promise<number> {
    saving.value = true
    error.value = ''
    try {
      const result = await acceptRefund(refundId)
      replace(result.refund)
      return result.balance
    } finally {
      saving.value = false
    }
  }

  async function reject(refundId: string): Promise<void> {
    saving.value = true
    error.value = ''
    try {
      const result = await rejectRefund(refundId)
      replace(result.refund)
    } finally {
      saving.value = false
    }
  }

  function forPayment(paymentId: string): Refund | undefined {
    return refunds.value.find(
      (refund) => refund.paymentId === paymentId || refund.transactionId === paymentId,
    )
  }

  function clearFilters(): void {
    Object.assign(filters, DEFAULT_FILTERS)
    page.value = 1
  }

  return {
    refunds,
    loading,
    saving,
    error,
    loaded,
    filters,
    page,
    perPage,
    stats,
    filtered,
    sorted,
    totalPages,
    paginated,
    rangeStart,
    rangeEnd,
    load,
    request,
    accept,
    reject,
    forPayment,
    clearFilters,
  }
})
