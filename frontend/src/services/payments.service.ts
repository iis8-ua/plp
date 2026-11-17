import type { Currency, Payment, PaymentHistoryEntry, PaymentStatus } from '@/types'
import { request } from '@/services/http'
import { normalizeApiDate } from '@/shared/utils/format'

interface ApiProduct {
  name?: string
}

interface ApiPayment {
  transaction_id: string
  amount: number
  currency?: string
  client?: string
  reference?: string
  invoice?: string
  payment_method?: string
  status: string
  products?: ApiProduct[]
  created_at?: string
}

function toCurrency(value?: string): Currency {
  return value === 'USD' || value === 'GBP' ? value : 'EUR'
}

function mapStatus(status: string): PaymentStatus {
  return status === 'approved' ? 'aceptado' : 'rechazado'
}

function conceptFor(payment: ApiPayment): string {
  const products = (payment.products ?? [])
    .map((product) => product.name)
    .filter((name): name is string => Boolean(name))
  return products.length > 0 ? products.join(', ') : `Pago ${payment.transaction_id}`
}

function historyFor(payment: ApiPayment, status: PaymentStatus, concept: string, reason: string): PaymentHistoryEntry[] {
  const at = normalizeApiDate(payment.created_at ?? '')
  return [
    {
      id: `${payment.transaction_id}-h1`,
      at,
      title: 'Pago registrado',
      description: concept,
      tone: 'brand',
    },
    {
      id: `${payment.transaction_id}-h2`,
      at,
      title: status === 'aceptado' ? 'Aceptado · Pago correcto' : 'Rechazado',
      description: reason,
      tone: status === 'aceptado' ? 'accent' : 'danger',
    },
  ]
}

function mapApiPayment(payment: ApiPayment): Payment {
  const status = mapStatus(payment.status)
  const concept = conceptFor(payment)
  const reason = status === 'aceptado' ? 'Pago correcto' : 'Pago rechazado'

  return {
    id: payment.transaction_id,
    transactionId: payment.transaction_id,
    client: payment.client ?? '—',
    reference: payment.reference ?? payment.transaction_id,
    invoice: payment.invoice ?? payment.transaction_id,
    method: payment.payment_method ?? 'card',
    concept,
    amount: payment.amount,
    currency: toCurrency(payment.currency),
    status,
    reason,
    createdAt: normalizeApiDate(payment.created_at ?? ''),
    history: historyFor(payment, status, concept, reason),
  }
}

export async function fetchPayments(): Promise<Payment[]> {
  const response = await request<ApiPayment[]>('/payments')
  return response.map(mapApiPayment)
}
