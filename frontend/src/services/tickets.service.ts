import type { Ticket, TicketHistoryEntry, TicketMessage, TicketStatus } from '@/types'
import { request } from '@/services/http'
import { normalizeApiDate } from '@/shared/utils/format'

interface ApiTicketHistoryEntry {
  id: string
  at: string
  title: string
  description?: string
  author?: string
}

interface ApiTicketMessage {
  id: string
  author: string
  role: 'comercio' | 'tecnico'
  message: string
  created_at: string
}

interface ApiTicket {
  id: string
  company_id: string
  company_name?: string
  subject?: string
  description?: string
  status: string
  reply?: string
  created_at: string
  updated_at?: string
  history?: ApiTicketHistoryEntry[]
  messages?: ApiTicketMessage[]
  assignee?: { id: string; name: string } | null
}

const STATUS_FROM_API: Record<string, TicketStatus> = {
  open: 'abierto',
  in_progress: 'en-proceso',
  closed: 'cerrado',
}

const STATUS_TO_API: Record<TicketStatus, string> = {
  abierto: 'open',
  'en-proceso': 'in_progress',
  cerrado: 'closed',
}

function toneFor(title: string): TicketHistoryEntry['tone'] {
  if (title.toLowerCase().includes('cerrad')) return 'accent'
  if (title.toLowerCase().includes('rechaz')) return 'danger'
  return 'brand'
}

function mapHistory(entry: ApiTicketHistoryEntry): TicketHistoryEntry {
  return {
    id: entry.id,
    at: normalizeApiDate(entry.at),
    title: entry.title,
    description: entry.description,
    author: entry.author,
    tone: toneFor(entry.title),
  }
}

function mapMessage(message: ApiTicketMessage): TicketMessage {
  return {
    id: message.id,
    author: message.author,
    role: message.role,
    message: message.message,
    createdAt: normalizeApiDate(message.created_at),
  }
}

function mapApiTicket(ticket: ApiTicket): Ticket {
  const createdAt = normalizeApiDate(ticket.created_at)
  const subject = ticket.subject ?? `Ticket ${ticket.id}`

  return {
    id: ticket.id,
    companyId: ticket.company_id,
    merchant: ticket.company_name ?? ticket.company_id,
    subject,
    status: STATUS_FROM_API[ticket.status] ?? 'abierto',
    createdAt,
    updatedAt: normalizeApiDate(ticket.updated_at ?? ticket.created_at),
    openedAt: createdAt,
    description: ticket.description ?? '',
    reply: ticket.reply ?? '',
    history:
      ticket.history && ticket.history.length > 0
        ? ticket.history.map(mapHistory)
        : [
            {
              id: `${ticket.id}-h1`,
              at: createdAt,
              title: 'Ticket abierto',
              description: ticket.description ?? '',
              tone: 'brand',
            },
          ],
    messages: (ticket.messages ?? []).map(mapMessage),
    assignee: ticket.assignee ?? null,
  }
}

export async function fetchTickets(): Promise<Ticket[]> {
  const response = await request<ApiTicket[]>('/tickets')
  return response.map(mapApiTicket)
}

export async function createTicket(payload: {
  companyId: string
  companyName: string
  subject: string
  description: string
}): Promise<Ticket> {
  const response = await request<ApiTicket>('/ticket/add', {
    method: 'POST',
    body: {
      company_id: payload.companyId,
      company_name: payload.companyName,
      subject: payload.subject,
      description: payload.description,
    },
  })
  return mapApiTicket(response)
}

export async function addTicketMessage(ticketId: string, message: string): Promise<Ticket> {
  const response = await request<ApiTicket>('/ticket/message', {
    method: 'POST',
    query: { id: ticketId },
    body: { message },
  })
  return mapApiTicket(response)
}

export async function assignTicket(
  ticketId: string,
  payload: { technicianId?: string; assignToMe?: boolean; unassign?: boolean },
): Promise<Ticket> {
  const response = await request<ApiTicket>('/ticket/assign', {
    method: 'PUT',
    query: { id: ticketId },
    body: {
      technician_id: payload.technicianId ?? '',
      assign_to_me: payload.assignToMe ?? false,
      unassign: payload.unassign ?? false,
    },
  })
  return mapApiTicket(response)
}

export async function updateTicket(
  ticketId: string,
  changes: { status: TicketStatus; reply: string },
): Promise<Ticket> {
  const response = await request<ApiTicket>('/ticket/update', {
    method: 'PUT',
    query: { id: ticketId },
    body: { status: STATUS_TO_API[changes.status], reply: changes.reply },
  })
  return mapApiTicket(response)
}

export async function deleteTicket(ticketId: string): Promise<void> {
  await request<{ message: string }>('/ticket/delete', {
    method: 'DELETE',
    query: { id: ticketId },
  })
}
