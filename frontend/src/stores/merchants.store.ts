import { computed, reactive, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Company, CompanyFilters } from '@/types'
import {
  createCompany,
  deleteCompany,
  fetchCompanies,
  reactivateCompany,
} from '@/services/companies.service'

const DEFAULT_FILTERS: CompanyFilters = {
  search: '',
  status: 'todos',
  sort: 'nombre-az',
}

export const useMerchantsStore = defineStore('merchants', () => {
  const companies = ref<Company[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')
  const loaded = ref(false)
  const filters = reactive<CompanyFilters>({ ...DEFAULT_FILTERS })
  const page = ref(1)
  const perPage = ref(7)

  const stats = computed(() => ({
    total: companies.value.length,
    activo: companies.value.filter((company) => company.status === 'activo').length,
    'dado-de-baja': companies.value.filter((company) => company.status === 'dado-de-baja').length,
  }))

  const filtered = computed(() => {
    const search = filters.search.trim().toLowerCase()
    return companies.value.filter((company) => {
      if (filters.status !== 'todos' && company.status !== filters.status) return false
      if (!search) return true
      return company.name.toLowerCase().includes(search) || company.id.toLowerCase().includes(search)
    })
  })

  const sorted = computed(() => {
    const list = [...filtered.value]
    if (filters.sort === 'recientes') {
      return list.sort((a, b) => b.registeredAt.localeCompare(a.registeredAt))
    }
    return list.sort((a, b) => a.name.localeCompare(b.name, 'es'))
  })

  const totalPages = computed(() => Math.max(1, Math.ceil(sorted.value.length / perPage.value)))
  const paginated = computed(() => {
    const start = (page.value - 1) * perPage.value
    return sorted.value.slice(start, start + perPage.value)
  })
  const rangeStart = computed(() => (sorted.value.length === 0 ? 0 : (page.value - 1) * perPage.value + 1))
  const rangeEnd = computed(() => Math.min(page.value * perPage.value, sorted.value.length))

  watch(
    () => ({ ...filters }),
    () => {
      page.value = 1
    },
    { deep: true },
  )

  watch(totalPages, (value) => {
    if (page.value > value) page.value = value
  })

  async function load(force = false): Promise<void> {
    if (loaded.value && !force) return
    loading.value = true
    error.value = ''
    try {
      companies.value = await fetchCompanies()
      loaded.value = true
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudieron cargar los comercios.'
    } finally {
      loading.value = false
    }
  }

  async function addCompany(name: string): Promise<Company> {
    saving.value = true
    error.value = ''
    try {
      const company = await createCompany(name)
      companies.value = [company, ...companies.value]
      return company
    } finally {
      saving.value = false
    }
  }

  async function deactivateCompany(company: Company): Promise<void> {
    saving.value = true
    error.value = ''
    try {
      const updated = await deleteCompany(company.id)
      const index = companies.value.findIndex((candidate) => candidate.id === company.id)
      if (index >= 0) companies.value[index] = updated
    } finally {
      saving.value = false
    }
  }

  async function reactivate(company: Company): Promise<void> {
    saving.value = true
    error.value = ''
    try {
      const updated = await reactivateCompany(company.id)
      const index = companies.value.findIndex((candidate) => candidate.id === company.id)
      if (index >= 0) companies.value[index] = updated
    } finally {
      saving.value = false
    }
  }

  function clearFilters(): void {
    Object.assign(filters, DEFAULT_FILTERS)
    page.value = 1
  }

  return {
    companies,
    loading,
    saving,
    error,
    loaded,
    filters,
    page,
    perPage,
    stats,
    filtered,
    sorted,
    totalPages,
    paginated,
    rangeStart,
    rangeEnd,
    load,
    addCompany,
    deactivateCompany,
    reactivate,
    clearFilters,
  }
})
