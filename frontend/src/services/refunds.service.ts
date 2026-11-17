import type { Currency, Payment, Refund, RefundStatus } from '@/types'
import { request } from '@/services/http'
import { normalizeApiDate } from '@/shared/utils/format'

interface ApiRefund {
  id: string
  transaction_id: string
  reference?: string
  amount: number
  currency?: string
  client?: string
  status: string
  reason?: string
  created_at?: string
}

interface RefundRequestResponse {
  request_id: string
  transaction_id: string
  status: string
}

interface RefundActionResponse {
  refund: ApiRefund
  balance: number
}

export interface RefundActionResult {
  refund: Refund
  balance: number
}

function toCurrency(value?: string): Currency {
  return value === 'USD' || value === 'GBP' ? value : 'EUR'
}

function mapStatus(status: string): RefundStatus {
  if (status === 'accepted') return 'aceptada'
  if (status === 'rejected') return 'rechazada'
  return 'pendiente'
}

function mapApiRefund(refund: ApiRefund): Refund {
  return {
    id: refund.id,
    transactionId: refund.transaction_id,
    paymentId: refund.transaction_id,
    reference: refund.reference ?? refund.transaction_id,
    client: refund.client ?? '—',
    amount: refund.amount,
    currency: toCurrency(refund.currency),
    reason: refund.reason ?? 'Devolución solicitada',
    status: mapStatus(refund.status),
    createdAt: normalizeApiDate(refund.created_at ?? ''),
  }
}

export async function fetchRefunds(): Promise<Refund[]> {
  const response = await request<ApiRefund[]>('/refunds')
  return response.map(mapApiRefund)
}

export async function requestRefund(payment: Payment, reason = ''): Promise<Refund> {
  const response = await request<RefundRequestResponse>('/refunds/request', {
    method: 'POST',
    query: { transaction_id: payment.transactionId, reason: reason.trim() || undefined },
    auth: false,
  })

  return {
    id: response.request_id,
    transactionId: response.transaction_id,
    paymentId: payment.id,
    reference: payment.reference,
    client: payment.client,
    amount: payment.amount,
    currency: payment.currency,
    reason: reason.trim() || 'Solicitud desde el portal del comercio',
    status: mapStatus(response.status),
    createdAt: new Date().toISOString().slice(0, 19),
  }
}

export async function acceptRefund(transactionId: string): Promise<RefundActionResult> {
  const response = await request<RefundActionResponse>('/refunds/accept', {
    method: 'POST',
    query: { transaction_id: transactionId },
  })
  return { refund: mapApiRefund(response.refund), balance: response.balance }
}

export async function rejectRefund(transactionId: string): Promise<RefundActionResult> {
  const response = await request<RefundActionResponse>('/refunds/reject', {
    method: 'POST',
    query: { transaction_id: transactionId },
  })
  return { refund: mapApiRefund(response.refund), balance: response.balance }
}
