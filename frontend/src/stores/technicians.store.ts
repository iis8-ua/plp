import { computed, reactive, ref } from 'vue'
import { acceptHMRUpdate, defineStore } from 'pinia'
import type { Technician, TechnicianCreatePayload } from '@/types'
import { createTechnician, deactivateTechnician, fetchTechnicians, reactivateTechnician } from '@/services/technicians.service'

export const useTechniciansStore = defineStore('technicians', () => {
  const technicians = ref<Technician[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')
  const loaded = ref(false)
  const filters = reactive<{ search: string; status: 'todos' | 'Activo' | 'Inactivo' }>({
    search: '',
    status: 'todos',
  })

  const stats = computed(() => ({
    total: technicians.value.length,
    activos: technicians.value.filter((item) => item.status === 'Activo').length,
    enProceso: technicians.value.reduce((total, item) => total + item.activity.in_progress, 0),
  }))

  const filtered = computed(() => {
    const search = filters.search.trim().toLowerCase()
    return technicians.value.filter((item) => {
      if (filters.status !== 'todos' && item.status !== filters.status) return false
      if (!search) return true
      return (
        item.name.toLowerCase().includes(search) ||
        item.email.toLowerCase().includes(search) ||
        item.username.toLowerCase().includes(search)
      )
    })
  })

  async function load(force = false): Promise<void> {
    if (loaded.value && !force) return
    loading.value = true
    error.value = ''
    try {
      technicians.value = await fetchTechnicians()
      loaded.value = true
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudieron cargar los técnicos.'
    } finally {
      loading.value = false
    }
  }

  async function create(payload: TechnicianCreatePayload): Promise<Technician> {
    saving.value = true
    error.value = ''
    try {
      const technician = await createTechnician(payload)
      await load(true)
      return technician
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudo crear el técnico.'
      throw cause
    } finally {
      saving.value = false
    }
  }

  async function setActive(id: string, active: boolean): Promise<Technician> {
    saving.value = true
    error.value = ''
    try {
      const technician = active
        ? await reactivateTechnician(id)
        : await deactivateTechnician(id)
      const index = technicians.value.findIndex((item) => item.id === id)
      if (index >= 0) technicians.value[index] = technician
      return technician
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudo actualizar el técnico.'
      throw cause
    } finally {
      saving.value = false
    }
  }

  function clearFilters(): void {
    filters.search = ''
    filters.status = 'todos'
  }

  return { technicians, loading, saving, error, loaded, filters, stats, filtered, load, create, setActive, clearFilters }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useTechniciansStore, import.meta.hot))
}
