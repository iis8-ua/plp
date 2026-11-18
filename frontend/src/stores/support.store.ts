import { computed, reactive, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Ticket, TicketStatus } from '@/types'
import { addTicketMessage, createTicket, fetchTickets } from '@/services/tickets.service'

interface SupportFilters {
  search: string
  status: TicketStatus | 'todos'
}

const DEFAULT_FILTERS: SupportFilters = {
  search: '',
  status: 'todos',
}

export const useSupportStore = defineStore('support', () => {
  const tickets = ref<Ticket[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')
  const loaded = ref(false)
  const filters = reactive<SupportFilters>({ ...DEFAULT_FILTERS })
  const page = ref(1)
  const perPage = ref(5)

  const stats = computed(() => ({
    total: tickets.value.length,
    abierto: tickets.value.filter((ticket) => ticket.status === 'abierto').length,
    'en-proceso': tickets.value.filter((ticket) => ticket.status === 'en-proceso').length,
    cerrado: tickets.value.filter((ticket) => ticket.status === 'cerrado').length,
  }))

  const filtered = computed(() => {
    const search = filters.search.trim().toLowerCase()
    return tickets.value.filter((ticket) => {
      if (filters.status !== 'todos' && ticket.status !== filters.status) return false
      if (!search) return true
      return (
        ticket.id.toLowerCase().includes(search) ||
        ticket.subject.toLowerCase().includes(search)
      )
    })
  })

  const sorted = computed(() =>
    [...filtered.value].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)),
  )

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

  /** El último mensaje del técnico indica una respuesta nueva para el comercio. */
  function hasNewReply(ticket: Ticket): boolean {
    return ticket.messages.at(-1)?.role === 'tecnico'
  }

  function replace(ticket: Ticket): void {
    const index = tickets.value.findIndex((candidate) => candidate.id === ticket.id)
    if (index >= 0) tickets.value[index] = ticket
    else tickets.value.unshift(ticket)
  }

  async function create(payload: {
    companyId: string
    companyName: string
    subject: string
    description: string
  }): Promise<Ticket> {
    saving.value = true
    error.value = ''
    try {
      const ticket = await createTicket(payload)
      replace(ticket)
      return ticket
    } finally {
      saving.value = false
    }
  }

  async function comment(ticketId: string, message: string): Promise<Ticket> {
    saving.value = true
    error.value = ''
    try {
      const ticket = await addTicketMessage(ticketId, message)
      replace(ticket)
      return ticket
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
    filtered,
    sorted,
    totalPages,
    paginated,
    rangeStart,
    rangeEnd,
    load,
    getById,
    hasNewReply,
    create,
    comment,
    clearFilters,
  }
})
