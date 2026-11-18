import type {
  CompanyStatus,
  Currency,
  PaymentStatus,
  RefundStatus,
  TicketStatus,
} from '@/types'

export const TICKET_STATUS_LABELS: Record<TicketStatus, string> = {
  abierto: 'Abierto',
  'en-proceso': 'En proceso',
  cerrado: 'Cerrado',
}

export const TICKET_STATUS_OPTIONS = [
  { value: 'abierto', label: 'Abierto' },
  { value: 'en-proceso', label: 'En proceso' },
  { value: 'cerrado', label: 'Cerrado' },
] as const

export const COMPANY_STATUS_LABELS: Record<CompanyStatus, string> = {
  activo: 'Activo',
  'dado-de-baja': 'Dado de baja',
}

export const PAYMENT_STATUS_LABELS: Record<PaymentStatus, string> = {
  aceptado: 'Aceptado',
  rechazado: 'Rechazado',
  pendiente: 'Pendiente',
  reembolsado: 'Reembolsado',
}

export const REFUND_STATUS_LABELS: Record<RefundStatus, string> = {
  pendiente: 'Solicitada',
  aceptada: 'Aceptada',
  rechazada: 'Rechazada',
}

export const CURRENCIES: Currency[] = ['EUR', 'USD', 'GBP']

export const CURRENCY_OPTIONS = CURRENCIES.map((currency) => ({
  value: currency,
  label: currency,
}))
