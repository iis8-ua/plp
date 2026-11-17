<script setup lang="ts">
import { computed } from 'vue'
import type { CompanyStatus, PaymentStatus, RefundStatus, TicketStatus } from '@/types'
import {
  COMPANY_STATUS_LABELS,
  PAYMENT_STATUS_LABELS,
  REFUND_STATUS_LABELS,
  TICKET_STATUS_LABELS,
} from '@/shared/utils/status'

type Kind = 'ticket' | 'company' | 'payment' | 'refund'
type Tone = 'success' | 'warning' | 'info' | 'danger' | 'neutral'

const props = withDefaults(
  defineProps<{
    kind: Kind
    status: TicketStatus | CompanyStatus | PaymentStatus | RefundStatus
    size?: 'sm' | 'md'
  }>(),
  { size: 'sm' },
)

const config = computed<{ label: string; tone: Tone }>(() => {
  if (props.kind === 'ticket') {
    const status = props.status as TicketStatus
    const tone: Tone =
      status === 'abierto' ? 'warning' : status === 'en-proceso' ? 'info' : 'success'
    return { label: TICKET_STATUS_LABELS[status], tone }
  }
  if (props.kind === 'company') {
    const status = props.status as CompanyStatus
    return {
      label: COMPANY_STATUS_LABELS[status],
      tone: status === 'activo' ? 'success' : 'neutral',
    }
  }
  if (props.kind === 'payment') {
    const status = props.status as PaymentStatus
    const tone: Tone =
      status === 'aceptado'
        ? 'success'
        : status === 'rechazado'
          ? 'danger'
          : status === 'en-proceso'
            ? 'warning'
            : 'neutral'
    return { label: PAYMENT_STATUS_LABELS[status], tone }
  }
  const status = props.status as RefundStatus
  const tone: Tone =
    status === 'pendiente' ? 'warning' : status === 'aceptada' ? 'success' : 'danger'
  return { label: REFUND_STATUS_LABELS[status], tone }
})

const tones: Record<Tone, string> = {
  success: 'bg-success-bg text-success-text',
  warning: 'bg-warning-bg text-warning-text',
  info: 'bg-info-bg text-info-text',
  danger: 'bg-danger-bg text-danger',
  neutral: 'bg-neutral-bg text-neutral-text',
}
</script>

<template>
  <span
    class="inline-flex h-7 w-fit items-center justify-center rounded-pill px-2 font-medium leading-none"
    :class="[tones[config.tone], size === 'md' ? 'text-[14px]' : 'text-[12px]']"
  >
    {{ config.label }}
  </span>
</template>
