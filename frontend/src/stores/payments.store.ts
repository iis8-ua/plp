import { computed, reactive, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Payment, PaymentFilters } from '@/types'
import { fetchPayments } from '@/services/payments.service'
import { isWithinDays } from '@/shared/utils/format'

const DEFAULT_FILTERS: PaymentFilters = {
  search: '',
  status: 'todos',
  currency: 'todas',
  date: 'cualquiera',
  sort: 'recientes',
}

function todayISODate(): string {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

export const usePaymentsStore = defineStore('payments', () => {
  const payments = ref<Payment[]>([])
  const loading = ref(false)
  const error = ref('')
  const loaded = ref(false)
  const filters = reactive<PaymentFilters>({ ...DEFAULT_FILTERS })
  const page = ref(1)
  const perPage = ref(5)

  const stats = computed(() => ({
    total: payments.value.length,
    aceptado: payments.value.filter((payment) => payment.status === 'aceptado').length,
    rechazado: payments.value.filter((payment) => payment.status === 'rechazado').length,
  }))

  const filtered = computed(() => {
    const search = filters.search.trim().toLowerCase()
    const today = todayISODate()
    return payments.value.filter((payment) => {
      if (filters.status !== 'todos' && payment.status !== filters.status) return false
      if (filters.currency !== 'todas' && payment.currency !== filters.currency) return false
      if (filters.date === 'hoy' && !payment.createdAt.startsWith(today)) return false
      if (filters.date === '7d' && !isWithinDays(payment.createdAt, 7)) return false
      if (filters.date === '30d' && !isWithinDays(payment.createdAt, 30)) return false
      if (!search) return true
      return (
        payment.transactionId.toLowerCase().includes(search) ||
        payment.concept.toLowerCase().includes(search) ||
        payment.client.toLowerCase().includes(search) ||
        payment.invoice.toLowerCase().includes(search) ||
        payment.reference.toLowerCase().includes(search)
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
  const rangeStart = computed(() => (sorted.value.length === 0 ? 0 : (page.value - 1) * perPage.value + 1))
  const rangeEnd = computed(() => Math.min(page.value * perPage.value, sorted.value.length))
  const latestPayments = computed(() => sorted.value.slice(0, 5))

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
      payments.value = await fetchPayments()
      loaded.value = true
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudieron cargar los pagos.'
    } finally {
      loading.value = false
    }
  }

  function getById(id: string): Payment | undefined {
    return payments.value.find((payment) => payment.id === id || payment.transactionId === id)
  }

  function clearFilters(): void {
    Object.assign(filters, DEFAULT_FILTERS)
    page.value = 1
  }

  return {
    payments,
    loading,
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
    latestPayments,
    load,
    getById,
    clearFilters,
  }
})
