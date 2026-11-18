<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import DataTable, { type DataColumn } from '@/shared/components/data/DataTable.vue'
import StatCard from '@/shared/components/data/StatCard.vue'
import AppAvatar from '@/shared/components/ui/AppAvatar.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppPagination from '@/shared/components/ui/AppPagination.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import EmptyState from '@/shared/components/ui/EmptyState.vue'
import NewTechnicianDialog from '@/modules/tech/technicians/components/NewTechnicianDialog.vue'
import TechnicianCreatedDialog from '@/modules/tech/technicians/components/TechnicianCreatedDialog.vue'
import TechnicianDetailDialog from '@/modules/tech/technicians/components/TechnicianDetailDialog.vue'
import { useTechniciansStore } from '@/stores/technicians.store'
import { useUiStore } from '@/stores/ui.store'
import type { Technician, TechnicianCreatePayload } from '@/types'

const store = useTechniciansStore()
const ui = useUiStore()

const newOpen = ref(false)
const createdOpen = ref(false)
const detailOpen = ref(false)
const created = ref<Technician | null>(null)
const selected = ref<Technician | null>(null)

const columns: DataColumn[] = [
  { key: 'name', label: 'Nombre completo' },
  { key: 'email', label: 'Correo', class: 'w-[230px]', headerClass: 'w-[230px]' },
  { key: 'username', label: 'Usuario', class: 'w-[130px]', headerClass: 'w-[130px]' },
  { key: 'role', label: 'Rol', class: 'w-[100px]', headerClass: 'w-[100px]' },
  { key: 'status', label: 'Estado', class: 'w-[120px]', headerClass: 'w-[120px]' },
  { key: 'actions', label: 'Acciones', class: 'w-[120px]', headerClass: 'w-[120px]' },
]

const statusOptions = [
  { value: 'todos', label: 'Todos los estados' },
  { value: 'Activo', label: 'Activo' },
  { value: 'Inactivo', label: 'Inactivo' },
]

const hasFilters = computed(
  () => Boolean(store.filters.search) || store.filters.status !== 'todos',
)

const page = ref(1)
const perPage = 10
const totalPages = computed(() => Math.max(1, Math.ceil(store.filtered.length / perPage)))
const paginated = computed(() =>
  store.filtered.slice((page.value - 1) * perPage, page.value * perPage),
)

function openDetail(technician: Technician): void {
  selected.value = technician
  detailOpen.value = true
}

async function createTechnician(payload: TechnicianCreatePayload): Promise<void> {
  try {
    created.value = await store.create(payload)
    newOpen.value = false
    createdOpen.value = true
    page.value = 1
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo crear el técnico.')
  }
}

function closeCreated(): void {
  createdOpen.value = false
  created.value = null
}

function createAnother(): void {
  closeCreated()
  newOpen.value = true
}

onMounted(() => {
  void store.load()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Gestiona tu equipo técnico"
      description="Crea accesos y consulta los técnicos de la plataforma."
    >
      <template #actions>
        <AppButton @click="newOpen = true">+ Nuevo técnico</AppButton>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
      <StatCard label="Técnicos" :value="store.stats.total" context="En el equipo" tone="brand" />
      <StatCard label="Activos" :value="store.stats.activos" context="Con acceso a PLP" tone="success" />
      <StatCard
        label="Tickets en proceso"
        :value="store.stats.enProceso"
        context="En manos del equipo"
        tone="brand"
      />
    </div>

    <section class="rounded-lg border border-line bg-white">
      <div class="grid grid-cols-1 gap-3 p-5 sm:grid-cols-2 xl:grid-cols-[minmax(280px,1fr)_224px_136px]">
        <AppInput
          v-model="store.filters.search"
          icon="search"
          placeholder="Buscar por nombre, correo o usuario"
          inputmode="search"
          aria-label="Buscar técnicos"
        />
        <AppSelect v-model="store.filters.status" :options="statusOptions" :ariaLabel="'Filtrar por estado'" />
        <AppButton variant="secondary" :disabled="!hasFilters" @click="store.clearFilters()">
          Limpiar
        </AppButton>
      </div>

      <div class="flex items-center justify-between gap-3 px-5 pb-4">
        <p class="text-[13px] font-medium leading-[1.5] text-muted">
          {{ store.filtered.length }} técnicos
        </p>
        <p class="text-[12px] leading-[1.5] text-muted">Orden alfabético por nombre</p>
      </div>

      <EmptyState
        v-if="!store.loading && store.filtered.length === 0"
        title="No hay técnicos que coincidan"
        description="Prueba con otra búsqueda o restablece los filtros."
        action-label="Limpiar filtros"
        icon="search"
        @action="store.clearFilters()"
      />

      <template v-else>
        <DataTable :columns="columns" :rows="paginated" :loading="store.loading" :skeleton-rows="6">
          <template #cell-name="{ row }">
            <div class="flex items-center gap-3">
              <AppAvatar :name="row.name" :size="32" shape="circle" tone="brand" />
              <span class="truncate font-medium text-ink">{{ row.name }}</span>
            </div>
          </template>
          <template #cell-email="{ row }">
            <span class="text-[13px] text-secondary">{{ row.email }}</span>
          </template>
          <template #cell-username="{ row }">
            <span class="text-[13px] text-secondary">{{ row.username }}</span>
          </template>
          <template #cell-role>
            <span class="text-[13px] text-secondary">Técnico</span>
          </template>
          <template #cell-status="{ row }">
            <span
              class="inline-flex h-7 items-center rounded-pill px-2.5 text-[12px] font-medium"
              :class="
                row.status === 'Activo'
                  ? 'bg-success-bg text-success-text'
                  : 'bg-neutral-bg text-neutral-text'
              "
            >
              {{ row.status }}
            </span>
          </template>
          <template #cell-actions="{ row }">
            <button
              type="button"
              class="text-[13px] font-semibold text-brand-700 hover:underline"
              @click="openDetail(row)"
            >
              Ver perfil
            </button>
          </template>
        </DataTable>

        <div class="border-t border-line px-5 py-4">
          <AppPagination
            :page="page"
            :total-pages="totalPages"
            :range-start="store.filtered.length === 0 ? 0 : (page - 1) * perPage + 1"
            :range-end="Math.min(page * perPage, store.filtered.length)"
            :total="store.filtered.length"
            label="técnicos"
            @update:page="page = $event"
          />
        </div>
      </template>
    </section>

    <NewTechnicianDialog
      :open="newOpen"
      :loading="store.saving"
      @create="createTechnician"
      @cancel="newOpen = false"
    />

    <TechnicianCreatedDialog
      :open="createdOpen"
      :technician="created"
      @close="closeCreated"
      @create-another="createAnother"
    />

    <TechnicianDetailDialog
      :open="detailOpen"
      :technician="selected"
      @close="detailOpen = false"
    />
  </div>
</template>
