import type { Technician, TechnicianActivity, TechnicianCreatePayload } from '@/types'
import { request } from '@/services/http'

interface ApiTechnician {
  id: string
  name: string
  email: string
  username: string
  role: 'tecnico'
  status: 'Activo' | 'Inactivo'
  activity?: TechnicianActivity
  password?: string
}

function mapTechnician(item: ApiTechnician): Technician {
  return {
    id: item.id,
    name: item.name,
    email: item.email,
    username: item.username,
    role: item.role,
    status: item.status,
    activity: item.activity ?? { assigned: 0, open: 0, in_progress: 0, closed: 0 },
    password: item.password,
  }
}

export async function fetchTechnicians(): Promise<Technician[]> {
  const response = await request<ApiTechnician[]>('/technicians')
  return response.map(mapTechnician)
}

export async function createTechnician(payload: TechnicianCreatePayload): Promise<Technician> {
  const response = await request<ApiTechnician>('/technicians', {
    method: 'POST',
    body: payload,
  })
  return mapTechnician(response)
}

async function setActive(id: string, active: boolean): Promise<Technician> {
  const response = await request<ApiTechnician>(
    active ? '/technicians/reactivate' : '/technicians/deactivate',
    {
      method: 'PUT',
      query: { id },
    },
  )
  return mapTechnician(response)
}

export function deactivateTechnician(id: string): Promise<Technician> {
  return setActive(id, false)
}

export function reactivateTechnician(id: string): Promise<Technician> {
  return setActive(id, true)
}
