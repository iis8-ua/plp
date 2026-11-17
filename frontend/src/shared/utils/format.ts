import type { Currency } from '@/types'

const MONTHS = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

interface DateParts {
  year: string
  month: number
  day: string
  hours: string
  minutes: string
  seconds: string
}

function parse(value: string): DateParts {
  const [datePart = '2026-01-01', timePart = '00:00:00'] = value.replace(' ', 'T').split('T')
  const [year = '2026', month = '01', day = '01'] = datePart.split('-')
  const [hours = '00', minutes = '00', seconds = '00'] = timePart.split(':')
  return { year, month: Number(month) - 1, day, hours, minutes, seconds }
}

export function formatDate(value: string): string {
  if (!value) return '—'
  const { year, month, day } = parse(value)
  return `${Number(day)} ${MONTHS[month]} ${year}`
}

export function formatDateTime(value: string): string {
  if (!value) return '—'
  const { month, day, hours, minutes } = parse(value)
  return `${Number(day)} ${MONTHS[month]} · ${hours}:${minutes}`
}

export function formatFullDateTime(value: string): string {
  if (!value) return '—'
  const { year, month, day, hours, minutes } = parse(value)
  return `${Number(day)} ${MONTHS[month]} ${year} · ${hours}:${minutes}`
}

export function formatTime(value: string): string {
  if (!value) return '—'
  const { hours, minutes, seconds } = parse(value)
  return `${hours}:${minutes}:${seconds}`
}

export function formatFullDateTimeSeconds(value: string): string {
  if (!value) return '—'
  const { year, month, day, hours, minutes, seconds } = parse(value)
  return `${Number(day)} ${MONTHS[month]} ${year} · ${hours}:${minutes}:${seconds}`
}

export function formatAmount(value: number): string {
  const fixed = Math.abs(value).toFixed(2)
  const [integer, decimals] = fixed.split('.')
  const grouped = integer.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  return `${value < 0 ? '-' : ''}${grouped},${decimals}`
}

export function formatCurrency(value: number, currency: Currency = 'EUR'): string {
  return `${formatAmount(value)} ${currency}`
}

export function initials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}

function todayISODate(): string {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

/** Normaliza una fecha ISO de la API a `YYYY-MM-DDTHH:mm:ss` (sin zona). */
export function normalizeApiDate(value: string): string {
  if (!value) return ''
  return value.replace('Z', '').replace(/\.\d+$/, '').slice(0, 19)
}

export function isWithinDays(value: string, days: number, reference = todayISODate()): boolean {
  if (!value) return false
  const date = new Date(`${value.slice(0, 10)}T00:00:00`)
  const base = new Date(`${reference}T00:00:00`)
  const diff = (base.getTime() - date.getTime()) / 86_400_000
  return diff >= 0 && diff < days
}
