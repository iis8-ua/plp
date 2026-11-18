import type { Company, CompanyForm, CreatedCompany } from '@/types'
import { request } from '@/services/http'
import { initials, normalizeApiDate } from '@/shared/utils/format'

interface ApiCompany {
  id: string
  nombre: string
  balance?: number
  status?: string
  registered_at?: string
}

function mapApiCompany(company: ApiCompany): Company {
  return {
    id: company.id,
    name: company.nombre,
    initials: initials(company.nombre),
    registeredAt: normalizeApiDate(company.registered_at ?? ''),
    status: company.status === 'dado-de-baja' ? 'dado-de-baja' : 'activo',
  }
}

export async function fetchCompanies(): Promise<Company[]> {
  const response = await request<ApiCompany[]>('/companies')
  return response.map(mapApiCompany)
}

interface ApiCompanyCreated extends ApiCompany {
  username: string
  password: string
}

export async function createCompany(payload: CompanyForm): Promise<CreatedCompany> {
  const { forceChange, ...company } = payload
  const response = await request<ApiCompanyCreated>('/companies/add', {
    method: 'PUT',
    body: { ...company, force_change: forceChange },
  })
  return {
    company: mapApiCompany(response),
    username: response.username,
    password: response.password,
  }
}

/** Baja lógica: la empresa conserva su histórico y pasa a `dado-de-baja`. */
export async function deleteCompany(companyId: string): Promise<Company> {
  const response = await request<ApiCompany>('/companies/delete', {
    method: 'DELETE',
    query: { id: companyId },
  })
  return mapApiCompany(response)
}

export async function reactivateCompany(companyId: string): Promise<Company> {
  const response = await request<ApiCompany>('/companies/reactivate', {
    method: 'PUT',
    query: { id: companyId },
  })
  return mapApiCompany(response)
}
