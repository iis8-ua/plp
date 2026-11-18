export type UserRole = 'admin' | 'tecnico' | 'comercio'
export type Portal = 'tecnico' | 'comercio'

export interface AuthUser {
  id: string
  name: string
  role: UserRole
  subtitle: string
  companyId?: string
  companyName?: string
  forcePasswordChange?: boolean
}

export interface Session {
  token: string
  user: AuthUser
}

export type TicketStatus = 'abierto' | 'en-proceso' | 'cerrado'

export interface TicketHistoryEntry {
  id: string
  at: string
  title: string
  description?: string
  author?: string
  tone?: 'brand' | 'accent' | 'danger'
}

export interface TicketMessage {
  id: string
  author: string
  role: 'comercio' | 'tecnico'
  message: string
  createdAt: string
}

export interface Ticket {
  id: string
  companyId: string
  merchant: string
  subject: string
  status: TicketStatus
  createdAt: string
  updatedAt: string
  openedAt: string
  description: string
  reply: string
  history: TicketHistoryEntry[]
  messages: TicketMessage[]
  assignee: { id: string; name: string } | null
}

export interface TechnicianActivity {
  assigned: number
  open: number
  in_progress: number
  closed: number
}

export interface Technician {
  id: string
  name: string
  email: string
  username: string
  role: 'tecnico'
  status: 'Activo' | 'Inactivo'
  activity: TechnicianActivity
  password?: string
}

export interface TechnicianCreatePayload {
  name: string
  email: string
  username: string
  password: string
  force_change: boolean
}

export interface CompanyProfile {
  id: string
  nombre: string
  status: CompanyStatus
  registeredAt: string
  razonSocial: string
  cif: string
  tipoEmpresa: string
  actividadEconomica: string
  direccion: string
  codigoPostal: string
  ciudad: string
  provincia: string
  pais: string
  telefono: string
  email: string
  web: string
}

export interface UserProfile {
  id: string
  name: string
  email: string
  username: string
  role: UserRole
  status: 'Activo' | 'Inactivo'
  company: CompanyProfile | null
  activity: TechnicianActivity | null
}

export type CompanyStatus = 'activo' | 'dado-de-baja'

export interface Company {
  id: string
  name: string
  initials: string
  registeredAt: string
  status: CompanyStatus
}

export type PaymentStatus = 'aceptado' | 'rechazado' | 'pendiente' | 'reembolsado'
export type Currency = 'EUR' | 'USD' | 'GBP'

export interface PaymentHistoryEntry {
  id: string
  at: string
  title: string
  description?: string
  tone?: 'brand' | 'accent' | 'danger'
}

export interface Payment {
  id: string
  transactionId: string
  client: string
  reference: string
  invoice: string
  method: string
  concept: string
  amount: number
  currency: Currency
  status: PaymentStatus
  reason: string
  createdAt: string
  history: PaymentHistoryEntry[]
}

export interface BalanceAccount {
  currency: Currency
  amount: number
}

export type RefundStatus = 'pendiente' | 'aceptada' | 'rechazada'

export interface Refund {
  id: string
  transactionId: string
  paymentId: string
  reference: string
  client: string
  amount: number
  currency: Currency
  reason: string
  status: RefundStatus
  createdAt: string
}

export interface RefundFilters {
  search: string
  status: RefundStatus | 'todos'
  date: 'cualquiera' | 'hoy' | '7d' | '30d'
  sort: 'recientes' | 'antiguos' | 'importe-desc'
}

export interface TicketFilters {
  search: string
  status: TicketStatus | 'todos'
  company: string
  date: 'cualquiera' | 'hoy' | '7d' | '30d'
  sort: 'abiertos-antiguos' | 'recientes' | 'antiguos'
  assignee: 'todos' | 'mios' | 'sin-asignar'
}

export interface CompanyForm {
  nombre: string
  razon_social: string
  cif: string
  tipo_empresa: string
  actividad_economica: string
  direccion: string
  codigo_postal: string
  ciudad: string
  provincia: string
  pais: string
  telefono: string
  email: string
  web: string
}

export interface CompanyFilters {
  search: string
  status: CompanyStatus | 'todos'
  sort: 'nombre-az' | 'recientes'
}

export interface PaymentFilters {
  search: string
  status: PaymentStatus | 'todos'
  currency: Currency | 'todas'
  date: 'cualquiera' | 'hoy' | '7d' | '30d'
  sort: 'recientes' | 'antiguos' | 'importe-desc'
}

export interface PaginationState {
  page: number
  perPage: number
}
