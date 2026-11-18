import type { CompanyProfile, TechnicianActivity, UserProfile } from '@/types'
import { request } from '@/services/http'
import { normalizeApiDate } from '@/shared/utils/format'

interface ApiCompanyProfile {
  id: string
  nombre: string
  status: 'activo' | 'dado-de-baja'
  registered_at?: string
  razon_social?: string
  cif?: string
  tipo_empresa?: string
  actividad_economica?: string
  direccion?: string
  codigo_postal?: string
  ciudad?: string
  provincia?: string
  pais?: string
  telefono?: string
  email?: string
  web?: string
}

interface ApiProfile {
  id: string
  name: string
  email: string
  username: string
  role: 'admin' | 'tecnico' | 'comercio'
  status: 'Activo' | 'Inactivo'
  company: ApiCompanyProfile | null
  activity: TechnicianActivity | null
}

function mapCompany(company: ApiCompanyProfile): CompanyProfile {
  return {
    id: company.id,
    nombre: company.nombre,
    status: company.status,
    registeredAt: normalizeApiDate(company.registered_at ?? ''),
    razonSocial: company.razon_social ?? '',
    cif: company.cif ?? '',
    tipoEmpresa: company.tipo_empresa ?? '',
    actividadEconomica: company.actividad_economica ?? '',
    direccion: company.direccion ?? '',
    codigoPostal: company.codigo_postal ?? '',
    ciudad: company.ciudad ?? '',
    provincia: company.provincia ?? '',
    pais: company.pais ?? '',
    telefono: company.telefono ?? '',
    email: company.email ?? '',
    web: company.web ?? '',
  }
}

function mapProfile(profile: ApiProfile): UserProfile {
  return {
    id: profile.id,
    name: profile.name,
    email: profile.email,
    username: profile.username,
    role: profile.role,
    status: profile.status,
    company: profile.company ? mapCompany(profile.company) : null,
    activity: profile.activity,
  }
}

export async function fetchProfile(): Promise<UserProfile> {
  const response = await request<ApiProfile>('/profile')
  return mapProfile(response)
}

export async function updateProfile(payload: Record<string, string>): Promise<UserProfile> {
  const response = await request<ApiProfile>('/profile', {
    method: 'PUT',
    body: payload,
  })
  return mapProfile(response)
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await request<{ message: string }>('/profile/password', {
    method: 'POST',
    body: { current_password: currentPassword, new_password: newPassword },
  })
}
