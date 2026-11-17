import { computed, reactive, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Ticket, TicketFilters, TicketStatus } from '@/types'
import { deleteTicket, fetchTickets, updateTicket } from '@/services/tickets.service'
import { isWithinDays } from '@/shared/utils/format'

const DEFAULT_FILTERS: TicketFilters = {
  search: '',
  status: 'todos',
  company: 'todos',
  date: 'cualquiera',
  sort: 'abiertos-antiguos',
}

function todayISODate(): string {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

export const useTicketsStore = defineStore('tickets', () => {
  const tickets = ref<Ticket[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')
  const loaded = ref(false)
  const filters = reactive<TicketFilters>({ ...DEFAULT_FILTERS })
  const page = ref(1)
  const perPage = ref(5)

  const stats = computed(() => ({
    total: tickets.value.length,
    abierto: tickets.value.filter((ticket) => ticket.status === 'abierto').length,
    'en-proceso': tickets.value.filter((ticket) => ticket.status === 'en-proceso').length,
    cerrado: tickets.value.filter((ticket) => ticket.status === 'cerrado').length,
  }))

  const companies = computed(() =>
    [...new Set(tickets.value.map((ticket) => ticket.merchant))].sort((a, b) => a.localeCompare(b, 'es')),
  )

  const filtered = computed(() => {
    const search = filters.search.trim().toLowerCase()
    const today = todayISODate()
    return tickets.value.filter((ticket) => {
      if (filters.status !== 'todos' && ticket.status !== filters.status) return false
      if (filters.company !== 'todos' && ticket.merchant !== filters.company) return false
      if (filters.date === 'hoy' && !ticket.createdAt.startsWith(today)) return false
      if (filters.date === '7d' && !isWithinDays(ticket.createdAt, 7)) return false
      if (filters.date === '30d' && !isWithinDays(ticket.createdAt, 30)) return false
      if (!search) return true
      return (
        ticket.id.toLowerCase().includes(search) ||
        ticket.merchant.toLowerCase().includes(search) ||
        ticket.subject.toLowerCase().includes(search)
      )
    })
  })

  const sorted = computed(() => {
    const list = [...filtered.value]
    if (filters.sort === 'recientes') {
      return list.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))
    }
    if (filters.sort === 'antiguos') {
      return list.sort((a, b) => a.createdAt.localeCompare(b.createdAt))
    }
    const priority: Record<TicketStatus, number> = { abierto: 0, 'en-proceso': 1, cerrado: 2 }
    const featured = new Set(['1042', '1043', '1045', '1038', '1035'])
    return list.sort((a, b) => {
      const aFeatured = featured.has(a.id) ? 0 : 1
      const bFeatured = featured.has(b.id) ? 0 : 1
      if (aFeatured !== bFeatured) return aFeatured - bFeatured
      if (priority[a.status] !== priority[b.status]) return priority[a.status] - priority[b.status]
      if (a.status === 'abierto') return a.createdAt.localeCompare(b.createdAt)
      return b.updatedAt.localeCompare(a.updatedAt)
    })
  })

  const totalPages = computed(() => Math.max(1, Math.ceil(sorted.value.length / perPage.value)))
  const paginated = computed(() => {
    const start = (page.value - 1) * perPage.value
    return sorted.value.slice(start, start + perPage.value)
  })
  const rangeStart = computed(() => (sorted.value.length === 0 ? 0 : (page.value - 1) * perPage.value + 1))
  const rangeEnd = computed(() => Math.min(page.value * perPage.value, sorted.value.length))

  const lastUpdated = computed(() => {
    const values = tickets.value.map((ticket) => ticket.updatedAt)
    if (values.length === 0) return ''
    return values.reduce((latest, value) => (value > latest ? value : latest), values[0])
  })

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
      tickets.value = await fetchTickets()
      loaded.value = true
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudieron cargar los tickets.'
    } finally {
      loading.value = false
    }
  }

  function getById(id: string): Ticket | undefined {
    return tickets.value.find((ticket) => ticket.id === id)
  }

  async function saveTicket(id: string, status: TicketStatus, reply: string): Promise<Ticket> {
    saving.value = true
    error.value = ''
    try {
      const updated = await updateTicket(id, { status, reply })
      const index = tickets.value.findIndex((ticket) => ticket.id === id)
      if (index >= 0) tickets.value[index] = updated
      return updated
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudo guardar el ticket.'
      throw cause
    } finally {
      saving.value = false
    }
  }

  async function removeTicket(id: string): Promise<void> {
    saving.value = true
    error.value = ''
    try {
      await deleteTicket(id)
      tickets.value = tickets.value.filter((ticket) => ticket.id !== id)
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudo eliminar el ticket.'
      throw cause
    } finally {
      saving.value = false
    }
  }

  function clearFilters(): void {
    Object.assign(filters, DEFAULT_FILTERS)
    page.value = 1
  }

  return {
    tickets,
    loading,
    saving,
    error,
    loaded,
    filters,
    page,
    perPage,
    stats,
    companies,
    filtered,
    sorted,
    totalPages,
    paginated,
    rangeStart,
    rangeEnd,
    lastUpdated,
    load,
    getById,
    saveTicket,
    removeTicket,
    clearFilters,
  }
})
